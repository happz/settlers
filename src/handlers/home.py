__author__                      = 'Milos Prchlik'
__copyright__                   = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__                     = 'happz@happz.cz'
__license__                     = 'http://www.php-suit.com/dpl'

import handlers
import lib.datalayer

import hlib.api

from hlib.api import api
from handlers import page, require_login, require_write

# pylint: disable-msg=F0401
import hruntime

#
# Api classes
#
class Player(hlib.api.User):
  def __init__(self, player):
    super(Player, self).__init__(player.user)

    self.update(['is_confirmed', 'is_on_turn'])

    self.is_confirmed		= player.confirmed
    self.is_on_turn		= player.is_on_turn

class Game(hlib.api.ApiJSON):
  def __init__(self, g):
    super(Game, self).__init__(['id', 'name', 'kind', 'limit', 'round', 'players', 'forhont', 'is_present', 'is_invited', 'is_on_turn', 'has_password', 'chat_posts'])

    self.id			= g.id
    self.kind			= g.kind
    self.name			= g.name
    self.limit			= g.limit
    self.round			= g.round
    self.players		= [Player(p) for p in g.players.values()]

    if g.forhont_player != None:
      self.forhont		= hlib.api.User(g.forhont_player.user)

    self.is_present		= g.has_player(hruntime.user)
    self.is_invited		= g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user)
    self.is_on_turn		= g.has_player(hruntime.user) and g.my_player.is_on_turn
    self.has_password		= g.is_password_protected
    if g.chat.unread > 0:
      self.chat_posts = g.chat.unread
    else:
      self.chat_posts = False

class RecentEvents(hlib.api.ApiJSON):
  def __init__(self):
    super(RecentEvents, self).__init__(['games', 'free_games', 'finished_games'])

    self.games			= []
    self.free_games		= []
    self.finished_games		= []

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
    import games

    re = RecentEvents()

    for g in games.f_active(hruntime.user):
      if g.has_player(hruntime.user) and g.my_player.is_on_turn or g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user) or g.has_player(hruntime.user):
        re.games.append(Game(g))
      else:
        re.free_games.append(Game(g))

    return hlib.api.Reply(200, events = re)
