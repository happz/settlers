__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import games
import handlers
import lib.datalayer

import hlib.api
import hlib.error
import hlib.pageable

# Shortcuts
from handlers import page, require_admin, require_login, require_write
from hlib.api import api
from hlib.input import validator_factory, validate_by, validator_optional

from games import GenericValidateGID, ValidateCardID, ValidateKind
from lib.chat import ValidateChatPost

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

class ApiRenderInfo(hlib.api.ApiJSON):
  def __init__(self, u):
    super(ApiRenderInfo, self).__init__(['board_skin'])

    self.board_skin	= u.board_skin

class ApiPlayerState(hlib.api.ApiJSON):
  def __init__(self, p):
    super(ApiPlayerState, self).__init__(['id', 'user', 'my_player', 'points', 'color'])

    self.id		= p.id
    self.user		= hlib.api.User(p.user)
    self.my_player	= p.id == p.game.my_player.id
    self.points		= p.points

    gm = games.game_module(p.game.kind)
    self.color = gm.COLOR_SPACE.colorize_player(p, p.game.my_player).to_api()

class ApiGameState(hlib.api.ApiJSON):
  def __init__(self, g):
    super(ApiGameState, self).__init__(['gid', 'name', 'round', 'players', 'render_info', 'can_pass', 'events'])

    self.gid		= g.id
    self.name		= g.name
    self.round		= g.round
    self.players	= []
    self.render_info	= ApiRenderInfo(g.my_player.user)
    self.can_pass	= g.my_player.can_pass

    self.events		= [e.to_api() for e in g.events.values() if e.hidden != True]

class ChatHandler(handlers.GenericHandler):
  #
  # Add
  #
  class ValidateAdd(GenericValidateGID):
    text = ValidateChatPost

  @require_write
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, gid = None, text = None):
    g = require_presence_in_game(gid)

    g.chat.add(text = text)

  #
  # Page
  #
  class ValidatePage(hlib.pageable.ValidatePage):
    gid = games.ValidateGID()

  @require_login
  @validate_by(schema = ValidatePage)
  @api
  def page(self, gid = None, start = None, length = None):
    g = require_presence_in_game(gid)

    return hlib.api.Reply(200, page = g.chat.get_page(start = start, length = length))

class Handler(handlers.GenericHandler):
  chat = ChatHandler()

  def __init__(self):
    super(Handler, self).__init__()

    import games.settlers.handler
    self.settlers = games.settlers.handler.Handler()

  #
  # Index
  #
  @require_login
  @validate_by(schema = GenericValidateGID)
  @page
  def index(self, gid = None):
    g = require_presence_in_game(gid)

    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'game-%s' % g.id, self.generate, 'games/' + g.kind + '.mako', params = {'game': g})

  #
  # Join
  #
  class ValidateJoin(GenericValidateGID):
    password = validator_optional(hlib.input.Password())

  @require_write
  @require_login
  @validate_by(schema = ValidateJoin)
  @api
  def join(self, gid = None, password = None):
    g = hruntime.dbroot.games[gid]
    g.join_player(hruntime.user, password)

  #
  # Pass turn
  #
  def do_pass_turn(self, gid, **kwargs):
    # pylint: disable-msg=E1101
    g = require_on_turn(gid)

    g.pass_turn(**kwargs)

    if hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_STAY:
      return

    if hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_NEXT:
      for kind in games.GAME_KINDS:
        check_result = games.game_module(kind, submodule = 'handler').GameOnTurnChecker.check()
        print [_g.id for _g in check_result]
        if len(check_result) <= 0:
          continue

        raise hlib.http.Redirect('/game?gid=' + str(check_result[0].id))

      else:
        raise hlib.http.Redirect('/home/')

    raise hlib.http.Redirect('/home/')

  @require_write
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def pass_turn(self, gid = None):
    return self.do_pass_turn(gid)

  #
  # Buy card
  #
  @require_write
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def buy_card(self, gid = None):
    g = require_on_game(gid)

    g.buy_card()

  #
  # Card click
  #
  class ValidateCardClick(GenericValidateGID):
    cid = ValidateCardID()

  @require_write
  @require_login
  @validate_by(schema = ValidateCardClick)
  @api
  def card_click(self, gid = None, cid = None):
    g = require_on_turn(gid)

    g.card_clicked(cid)

  #
  # State
  #
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def state(self, gid = None):
    g = require_presence_in_game(gid)

    g_state = ApiGameState(g)

    for p in g.players.values():
      p_state = ApiPlayerState(p)
      p.update_state(p_state)

      g_state.players.append(p_state)

    g.update_state(g_state)

    return hlib.api.Reply(200, game = g_state)

  #
  # New
  #
  class ValidateNew(hlib.input.SchemaValidator):
    name			= validator_factory(hlib.input.CommonString(), hlib.input.MinLength(2), hlib.input.MaxLength(64))
    limit			= validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([3, 4]))
    turn_limit			= validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([0, 43200, 86400, 172800, 259200, 604800, 1209600]))
    kind			= ValidateKind()

    password			= validator_optional(hlib.input.Username())
    desc			= validator_optional(validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(64)))

    opponent1			= validator_optional(hlib.input.Username())
    opponent2			= validator_optional(hlib.input.Username())
    opponent3			= validator_optional(hlib.input.Username())

    allow_extra_fields		= True
    if_key_missing		= None

  @require_login
  @require_write
  @validate_by(schema = ValidateNew)
  @api
  def new(self, **kwargs):
    gm = games.game_module(kwargs['kind'])

    creation_flags = gm.GameCreationFlags(kwargs)
    creation_flags.owner = hruntime.user

    gm.Game.create_game(creation_flags)
