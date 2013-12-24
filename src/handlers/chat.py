__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import handlers

import hlib.api
import hlib.events
import hlib.input
import hlib.pageable

# Handlers
from hlib.api import api
from handlers import page, require_login, require_write

# Validators
from hlib.input import validator_factory, validate_by

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class Handler(handlers.GenericHandler):
  def __init__(self, chat):
    super(Handler, self).__init__()

    self.chat = chat

  @require_login
  @page
  def index(self):
    return self.generate('chat.mako')

  #
  # Add
  #
  class ValidateAdd(hlib.input.SchemaValidator):
    text = validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(65535))

  @require_login
  @require_write
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, text = None):
    self.chat.add(text = text)

  @require_login
  @validate_by(schema = hlib.pageable.ValidatePage)
  @api
  def page(self, start = None, length = None):
    last_board = hruntime.user.last_board
    return hlib.api.Reply(200, page = self.chat.get_page(start = start, length = length), last_board = last_board)

  class ValidateLastAccess(hlib.input.SchemaValidator):
    last_access = validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

  @require_login
  @require_write
  @validate_by(schema = ValidateLastAccess)
  @api
  def last_access(self, last_access = None):
    self.chat.update_last_access(last_access)

hlib.events.Hook('system.ChatPost', lambda e: hruntime.cache.remove_for_all_users('recent_events'))
