__author__                      = 'Milos Prchlik'
__copyright__                   = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__                     = 'happz@happz.cz'
__license__                     = 'http://www.php-suit.com/dpl'

import hlib.api

import handlers

from hlib.api import api
from handlers import page, require_login

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

#
# Api classes
#
class RecentEvents(hlib.api.ApiJSON):
  def __init__(self):
    super(RecentEvents, self).__init__(['playable', 'free', 'finished', 'finished_chat'])

    self.playable			= []
    self.free				= []
    self.finished			= []
    self.finished_chat			= False

class Handler(handlers.GenericHandler):
  #
  # Index
  #
  @require_login
  @page
  def index(self):
    return self.generate('home.mako')

  #
  # Recent events
  #
  @require_login
  @api
  def recent_events(self):
    def __recent_events():
      import games
      import tournaments

      re = RecentEvents()

      for g in games.f_active(hruntime.user):
        ga = g.to_api()

        if g.has_player(hruntime.user) and g.my_player.is_on_turn or g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user) or g.has_player(hruntime.user):
          re.playable.append(ga)
        else:
          re.free.append(ga)

      cnt = 0
      for g in games.f_inactive(hruntime.user):
        re.finished.append(g.to_api())

        if g.my_player.chat.unread > 0:
          cnt += 1

      if cnt > 0:
        re.finished_chat = cnt

      for t in tournaments.f_active(hruntime.user):
        ta = t.to_api()

        if t.has_player(hruntime.user):
          re.playable.append(ta)
        else:
          re.free.append(ta)

      return hlib.api.Reply(200, events = re)

    return __recent_events()
