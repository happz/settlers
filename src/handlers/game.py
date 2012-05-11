import games
import handlers

import hlib.pageable
import hlib.ui.templates
import hlib.ui.templates.Mako

import lib.datalayer

from handlers import require_login, require_write, page
from games import GenericValidateGID, ValidateCardID, ValidateKind
from hlib.input import validate_by, validator_factory, validator_optional, CommonString, Password, MinLength, MaxLength, NotEmpty, Int, OneOf, Username, SchemaValidator
from hlib.api import api, ApiRaw, ApiReply
from lib.chat import ValidateChatPost
import hlib.api

# pylint: disable-msg=F0401
import hruntime

def require_presence_in_game(gid):
  if gid not in hruntime.dbroot.games:
    raise hlib.error.AccessDeniedError()

  g = hruntime.dbroot.games[gid]
  if not g.has_player(hruntime.user):
    raise hlib.error.AccessDeniedError()

  return g

def require_on_turn(gid):
  if gid not in hruntime.dbroot.games:
    raise hlib.error.AccessDeniedError()

  g = hruntime.dbroot.games[gid]
  if not g.has_player(hruntime.user) or not g.my_player.is_on_turn:
    raise hlib.error.AccessDeniedError()

  return g

def require_on_game(gid):
  if gid not in hruntime.dbroot.games:
    raise hlib.error.AccessDeniedError()

  g = hruntime.dbroot.games[gid]
  if not g.has_player(hruntime.user) or not g.my_player.is_on_game:
    raise hlib.error.AccessDeniedError()

  return g

class ApiPassTurn(hlib.api.ApiJSON):
  def __init__(self):
    super(ApiPassTurn, self).__init__(['after', 'gid'])

    self.after		= 'stay'

class ApiRenderInfo(hlib.api.ApiJSON):
  def __init__(self, u):
    super(ApiRenderInfo, self).__init__(['board_skin'])

    self.board_skin	= u.board_skin

class ApiPlayerState(hlib.api.ApiJSON):
  def __init__(self, p):
    super(ApiPlayerState, self).__init__(['id', 'user', 'my_player', 'points', 'color'])

    self.id		= p.id
    self.user		= hlib.api.ApiUserInfo(p.user)
    self.my_player	= p.id == p.game.my_player.id
    self.points		= p.points

    m = games.game_module(p.game.kind)
    self.color = m.COLOR_SPACE.colorize_player(p, p.game.my_player).to_api()

class ApiGameState(hlib.api.ApiJSON):
  def __init__(self, g):
    super(ApiGameState, self).__init__(['gid', 'name', 'round', 'players', 'render_info', 'can_pass', 'events'])

    self.gid		= g.id
    self.name		= g.name
    self.round		= g.round
    self.players	= []
    self.render_info	= ApiRenderInfo(g.my_player.user)
    self.can_pass	= g.my_player.can_pass

    self.events		= [e.to_api() for e in g.events.itervalues() if e.hidden != True]

class ChatHandler(handlers.GenericHandler):
  class ValidateAdd(GenericValidateGID):
    text = ValidateChatPost

  @require_write
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, gid = None, text = None):
    g = require_presence_in_game(gid)

    g.chat.add(text = text)

  class ValidatePage(hlib.pageable.ValidatePage):
    gid = games.ValidateGID()

  @require_login
  @validate_by(schema = ValidatePage)
  @api
  def page(self, gid = None, start = None, length = None):
    g = require_presence_in_game(gid)

    return g.chat.get_page(start = start, length = length)

class Handler(handlers.GenericHandler):
  chat = ChatHandler()

  def __init__(self):
    super(Handler, self).__init__()

    import games.settlers.handler
    self.settlers = games.settlers.handler.Handler()

  class ValidateJoin(GenericValidateGID):
    password = validator_optional(Password())

  @require_write
  @require_login
  @validate_by(schema = ValidateJoin)
  @api
  def join(self, gid = None, password = None):
    g = hruntime.dbroot.games[gid]
    g.join_player(hruntime.user, password)

  def do_pass_turn(self, gid, **kwargs):
    # pylint: disable-msg=E1101
    g = require_on_turn(gid)

    g.pass_turn(**kwargs)

    reply = hlib.api.ApiReply(200, pass_turn = ApiPassTurn())

    if hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_STAY:
      pass

    elif hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_NEXT:
      for kind in games.GAME_KINDS:
        check_result = games.game_module(kind, submodule = 'handler').GameOnTurnChecker.check()
        if len(check_result) <= 0:
          continue

        # pylint: disable-msg=E1101
        reply.pass_turn.after = 'next'
        reply.pass_turn.gid = check_result[0].id
        break

      else:
        reply.pass_turn.after = 'games'

    else:
      # pylint: disable-msg=E1101
      reply.pass_turn.after = 'games'

    return reply

  @require_write
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def pass_turn(self, gid = None):
    return self.do_pass_turn(gid)

  @require_write
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def buy_card(self, gid = None):
    g = require_on_game(gid)

    return g.buy_card()

  class ValidateCardClick(GenericValidateGID):
    cid = ValidateCardID()

  @require_write
  @require_login
  @validate_by(schema = ValidateCardClick)
  @api
  def card_click(self, gid = None, cid = None):
    g = require_on_turn(gid)

    return g.card_clicked(cid)

  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def state(self, gid = None):
    g = require_presence_in_game(gid)

    g_state = ApiGameState(g)

    for p in g.players.itervalues():
      p_state = ApiPlayerState(p)
      p.update_state(p_state)

      g_state.players.append(p_state)

    g.update_state(g_state)

    return hlib.api.ApiReply(200, game = g_state)

  class ValidateIndex(GenericValidateGID):
    _view = validator_optional(CommonString())

  @require_login
  @validate_by(schema = ValidateIndex)
  @page
  def index(self, gid = None, _view = None):
    g = require_presence_in_game(gid)

    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'game-%s' % g.id, self.generate, 'games/' + g.kind + '.mako', params = {'game': g})

  class ValidateNew(SchemaValidator):
    name = validator_factory(CommonString(), MinLength(2), MaxLength(64))
    limit = validator_factory(NotEmpty(), Int(), OneOf([3, 4]))
    turn_limit = validator_factory(NotEmpty(), Int(), OneOf([0, 43200, 86400, 172800, 259200, 604800, 1209600]))
    kind = ValidateKind()

    password = validator_optional(Username())
    desc = validator_optional(validator_factory(CommonString(), MaxLength(64)))

    opponent1 = validator_optional(Username())
    opponent2 = validator_optional(Username())
    opponent3 = validator_optional(Username())

    allow_extra_fields = True
    if_key_missing = None

  @require_login
  @require_write
  @validate_by(schema = ValidateNew)
  @api
  def new(self, **kwargs):
    game_module = games.game_module(kwargs['kind'])

    creation_flags = game_module.GameCreationFlags(kwargs)
    creation_flags.owner = hruntime.user

    game_module.Game.create_game(creation_flags)
    return None
