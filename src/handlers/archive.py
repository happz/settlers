__author__                      = 'Milos Prchlik'
__copyright__                   = 'Copyright 2013, Milos Prchlik'
__contact__                     = 'happz@happz.cz'
__license__                     = 'http://www.php-suit.com/dpl'

import os.path
import handlers

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
    return hruntime.cache.test_and_set(hruntime.user, 'archive-page', self.generate, 'archive.mako')
