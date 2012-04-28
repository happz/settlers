import handlers
import hlib.i18n
import tournament

# Handlers
from hlib.api import api
from handlers import page, require_admin, require_login, require_write

# Validators
from hlib.input import validate_by, validator_factory
from lib.chat import ValidateChatPost
from tournament import ValidateTID

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
  tid = tournament.ValidateTID

class ChatHandler(handlers.GenericHandler):
  class ValidateAdd(GenericValidateTID):
    text = ValidateChatPost()

  @require_write
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, tid = None, text = None):
    t = require_presence_in_tournament(tid)

    t.chat.add(text = text)

  class ValidateLister(GenericValidateTID):
    allow_extra_fields = True

  @require_login
  @validate_by(schema = ValidateLister)
  @api
  def lister(self, **kwargs):
    t = require_presence_in_tournament(tid)

    return t.chat.lister(**kwargs)

class Handler(handlers.GenericHandler):
  chat = ChatHandler()

  @require_login
  @validate_by(schema = GenericValidateTID)
  @page
  def index(self, tid = None):
    return self.generate('tournament.mako', params = {'current_tournament': hruntime.dbroot.tournaments[tid]})

  class ValidateJoin(GenericValidateTID):
    password = hlib.input.validator_optional(hlib.input.Password())

  @require_write
  @require_login
  @validate_by(schema = ValidateJoin)
  @api
  def join(self, tid = None, password = None):
    t = require_presence_in_tournament(tid)

    t.add_player(hruntime.user, password)

  @require_admin
  @require_write
  @require_login
  @validate_by(schema = GenericValidateTID)
  @api
  def begin(self, tid = None):
    t = require_presence_in_tournament(tid)

    t.begin()
