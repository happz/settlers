import handlers
import lib.datalayer
import hlib.pageable

# Handlers
from hlib.api import api, ApiRaw
from handlers import page, require_login, require_write

# Validators
from hlib.input import validator_factory, validate_by, CommonString, MaxLength, SchemaValidator
from lib.chat import ValidateChatPost

# pylint: disable-msg=F0401
import hruntime

class ChatHandler(handlers.GenericHandler):
  def __init__(self, chat):
    super(ChatHandler, self).__init__()

    self.chat = chat

  class ValidateAdd(SchemaValidator):
    text = validator_factory(CommonString(), MaxLength(65535))

  @require_login
  @require_write
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, text = None):
    self.chat.add(text = text)

  @require_login
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'chat', self.generate, 'chat.mako')

  @require_login
  @validate_by(schema = hlib.pageable.ValidatePage)
  @api
  def page(self, start = None, length = None):
    return self.chat.get_page(start = start, length = length)
