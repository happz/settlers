__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import handlers
import lib.chat
import lib.datalayer

import hlib.api
import hlib.input
import hlib.pageable

# Handlers
from hlib.api import api
from handlers import page, require_login, require_write

# Validators
from hlib.input import validator_factory, validate_by

# pylint: disable-msg=F0401
import hruntime

class Handler(handlers.GenericHandler):
  def __init__(self, chat):
    super(Handler, self).__init__()

    self.chat = chat

  @require_login
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'chat', self.generate, 'chat.mako')

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
