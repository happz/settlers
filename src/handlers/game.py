__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import games
import handlers
import lib.datalayer

import hlib.api
import hlib.error
import hlib.input
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
  if gid in hruntime.dbroot.games:
    g = hruntime.dbroot.games[gid]

  elif gid in hruntime.dbroot.games_archived:
    g = hruntime.dbroot.games_archived[gid]

  else:
    raise hlib.error.AccessDeniedError()

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

    return hlib.api.Reply(200, page = g.chat.get_page(start = start, length = length), last_board = g.my_player.last_board)

  class ValidateLastAccess(hlib.input.SchemaValidator):
    gid = games.ValidateGID()
    last_access = validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

  @require_login
  @require_write
  @validate_by(schema = ValidateLastAccess)
  @api
  def last_access(self, gid = None, last_access = None):
    g = require_presence_in_game(gid)
    g.chat.update_last_access(last_access)

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

    return self.generate('games/' + g.kind + '.mako', params = {'game': g})

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
      return hlib.api.Reply(200, game = g.to_state())

    if hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_NEXT:
      for kind in games.GAME_KINDS:
        check_result = games.game_module(kind, submodule = 'handler').GameOnTurnChecker.check()
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
    return hlib.api.Reply(200, game = g.to_state())

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
    return hlib.api.Reply(200, game = g.to_state())

  #
  # State
  #
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def state(self, gid = None):
    g = require_presence_in_game(gid)

    return hlib.api.Reply(200, game = g.to_state())
