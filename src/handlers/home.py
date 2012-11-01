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

class Playable(hlib.api.ApiJSON):
  def __init__(self, o):
    super(Playable, self).__init__(['id', 'name', 'kind', 'limit', 'round', 'players', 'forhont', 'is_present', 'is_invited', 'is_on_turn', 'has_password', 'chat_posts', 'is_game', 'num_players'])

    self.id			= o.id
    self.kind			= o.kind
    self.name			= o.name
    self.round			= o.round
    self.players		= [Player(p) for p in o.players.values()]

    self.is_present		= o.has_player(hruntime.user)
    self.has_password		= o.is_password_protected

    if o.chat.unread > 0:
      self.chat_posts = o.chat.unread
    else:
      self.chat_posts = False

class Game(Playable):
  def __init__(self, g):
    super(Game, self).__init__(g)

    self.is_game		= True

    self.limit			= g.limit

    if g.forhont_player != None:
      self.forhont		= hlib.api.User(g.forhont_player.user)

    self.is_invited		= g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user)
    self.is_on_turn		= g.has_player(hruntime.user) and g.my_player.is_on_turn

class Tournament(Playable):
  def __init__(self, t):
    super(Tournament, self).__init__(t)

    self.is_game		= False
    self.limit			= t.flags.limit
    self.num_players		= t.num_players

class RecentEvents(hlib.api.ApiJSON):
  def __init__(self):
    super(RecentEvents, self).__init__(['playable', 'free', 'finished'])

    self.playable			= []
    self.free				= []
    self.finished			= []

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
    import tournaments

    re = RecentEvents()

    for g in games.f_active(hruntime.user):
      if g.has_player(hruntime.user) and g.my_player.is_on_turn or g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user) or g.has_player(hruntime.user):
        re.playable.append(Game(g))
      else:
        re.free.append(Game(g))

    for t in tournaments.f_active(hruntime.user):
      if t.has_player(hruntime.user):
        re.playable.append(Tournament(t))
      else:
        re.free.append(Tournament(t))

    return hlib.api.Reply(200, events = re)
