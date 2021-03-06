__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import hlib.error
import handlers

import games
import tournaments
import tournaments.engines

# Handlers
from hlib.api import api
from handlers import page, require_login, require_write, require_admin

# Validators
from hlib.input import validate_by, validator_factory, validator_optional
from lib.chat import ValidateChatPost
from games import ValidateKind

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

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

  #
  # Last access
  #
  class ValidateLastAccess(hlib.input.SchemaValidator):
    tid = games.ValidateGID()
    last_access = validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

  @require_login
  @require_write
  @validate_by(schema = ValidateLastAccess)
  @api
  def last_access(self, tid = None, last_access = None):
    t = require_presence_in_tournament(tid)
    t.chat.update_last_access(last_access)

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
    engine = validator_factory(hlib.input.CommonString(), hlib.input.OneOf(tournaments.engines.engines.keys()))
    name = validator_factory(hlib.input.CommonString(), hlib.input.MinLength(2), hlib.input.MaxLength(64))
    limit = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([3, 4]))
    num_players = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(min = 6, max = 48))
    limit_rounds = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(min = 4, max = 5))
    turn_limit = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([0, 43200, 86400, 172800, 259200, 604800, 1209600]))
    kind = ValidateKind()
    password = validator_optional(hlib.input.Username())
    desc = validator_optional(validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(64)))

    allow_extra_fields          = True
    if_key_missing              = None

  @require_login
  @require_write
  @require_admin
  @validate_by(schema = ValidateNew)
  @api
  def new(self, **kwargs):
    gm = games.game_module(kwargs['kind'])

    tkwargs = {}
    for name in tournaments.TournamentCreationFlags.FLAGS:
      if name in kwargs:
        tkwargs[name] = kwargs[name]

    gkwargs = {}
    for name in gm.GameCreationFlags.FLAGS:
      if name in kwargs:
        gkwargs[name] = kwargs[name]

    tflags = tournaments.TournamentCreationFlags(**tkwargs)
    tflags.owner = hruntime.user
    tflags.limit = int(kwargs['num_players'])

    gflags = gm.GameCreationFlags(**gkwargs)
    gflags.opponents = []
    gflags.desc = ''
    gflags.password = None
    gflags.owner = None

    tournaments.Tournament.create_tournament(tflags, gflags)
