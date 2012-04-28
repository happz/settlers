import handlers
import lib.datalayer

# Handlers
from hlib.api import api, ApiRaw
from handlers import page, require_login, require_write

# Validators
from hlib.input import validator_factory, validate_by, CommonString, MaxLength, SchemaValidator
from lib.chat import ValidateChatPost

# pylint: disable-msg=F0401
import hruntime

class Handler(handlers.GenericHandler):
  @require_login
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'new', self.generate, 'new.mako')
