import handlers
import lib.datalayer

# Shortcuts
from handlers import page, require_login, require_write

# pylint: disable-msg=F0401
import hruntime

class Handler(handlers.GenericHandler):
  #
  # Index
  #
  @require_login
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'new', self.generate, 'new.mako')
