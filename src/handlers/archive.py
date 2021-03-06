__author__                      = 'Milos Prchlik'
__copyright__                   = 'Copyright 2013, Milos Prchlik'
__contact__                     = 'happz@happz.cz'
__license__                     = 'http://www.php-suit.com/dpl'

import handlers

import hlib.events

from handlers import page, require_login

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class Handler(handlers.GenericHandler):
  #
  # Index
  #
  @require_login
  @page
  def index(self):
    return hruntime.cache.test_and_set(hruntime.user, 'archive-page', self.generate, 'archive.mako')

def __invalidate_render_cache(e):
  for p in e.game.players.values():
    hruntime.cache.remove(p.user, 'archive-page')

hlib.events.Hook('game.GameArchived', __invalidate_render_cache)
