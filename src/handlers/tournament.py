__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import hlib.error
import handlers
import hlib.i18n

import lib.datalayer
import games
import tournaments

# Handlers
from hlib.api import api
from handlers import page, require_admin, require_login, require_write

# Validators
from hlib.input import validate_by, validator_factory, validator_optional
from lib.chat import ValidateChatPost
from games import ValidateKind
from tournaments import ValidateTID

# pylint: disable-msg=F0401
import hruntime

def require_presence_in_tournament(tid):
  if tid not in hruntime.dbroot.tournaments:
    raise hlib.error.AccessDeniedError()

  t = hruntime.dbroot.tournaments[tid]
  if not t.has_player(hruntime.user):
    raise hlib.error.AccessDeniedError()

  return t

class GenericValidateTID(hlib.input.SchemaValidator):
  tid = tournaments.ValidateTID

class ChatHandler(handlers.GenericHandler):
  #
  # Add
  #
  class ValidateAdd(GenericValidateTID):
    text = ValidateChatPost()

  @require_write
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, tid = None, text = None):
    t = require_presence_in_tournament(tid)

    t.chat.add(text = text)

  #
  # Page
  #
  class ValidatePage(hlib.pageable.ValidatePage):
    tid = tournaments.ValidateTID()

  @require_login
  @validate_by(schema = ValidatePage)
  @api
  def page(self, tid = None, start = None, length = None):
    t = require_presence_in_tournament(tid)

    return hlib.api.Reply(200, page = t.chat.get_page(start = start, length = length))

class Handler(handlers.GenericHandler):
  chat = ChatHandler()

  #
  # Index
  #
  @require_login
  @validate_by(schema = GenericValidateTID)
  @page
  def index(self, tid = None):
    t = require_presence_in_tournament(tid)

    return self.generate('tournament.mako', params = {'tournament': t})

  #
  # State
  #
  @require_login
  @validate_by(schema = GenericValidateTID)
  @api
  def state(self, tid = None):
    t = require_presence_in_tournament(tid)

    return hlib.api.Reply(200, tournament = t.to_state())

  #
  # Join
  #
  class ValidateJoin(GenericValidateTID):
    password = validator_optional(hlib.input.Password())

  @require_write
  @require_login
  @validate_by(schema = ValidateJoin)
  @api
  def join(self, tid = None, password = None):
    t = hruntime.dbroot.tournaments[tid]
    t.join_player(hruntime.user, password)

  #
  # New
  #
  class ValidateNew(hlib.input.SchemaValidator):
    engine			= validator_factory(hlib.input.CommonString(), hlib.input.OneOf(['swiss']))
    name			= validator_factory(hlib.input.CommonString(), hlib.input.MinLength(2), hlib.input.MaxLength(64))
    limit			= validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([3, 4]))
    num_players			= validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([12, 24]))
    turn_limit			= validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([0, 43200, 86400, 172800, 259200, 604800, 1209600]))
    kind                        = ValidateKind()
    password                    = validator_optional(hlib.input.Username())
    desc                        = validator_optional(validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(64)))

    allow_extra_fields          = True
    if_key_missing              = None

  @require_login
  @require_write
  @validate_by(schema = ValidateNew)
  @api
  def new(self, **kwargs):
    gm = games.game_module(kwargs['kind'])

    flags = gm.GameCreationFlags(**kwargs)
    flags.owner = hruntime.user

    t = tournaments.Tournament.create_tournament(flags, kwargs['num_players'], kwargs['engine'])
