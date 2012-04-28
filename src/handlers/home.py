import hlib.api

import handlers
import lib.datalayer

from hlib.api import api, ApiReply, ApiJSON
from handlers import require_login, page, require_write

import hruntime

class ApiUserInfo(hlib.api.ApiUserInfo):
  def __init__(self, player):
    super(ApiUserInfo, self).__init__(player.user)

    self.update(['is_confirmed', 'is_on_turn'])

    self.is_confirmed = player.confirmed
    self.is_on_turn   = player.is_on_turn

class ApiGame(ApiJSON):
  def __init__(self, g):
    super(ApiGame, self).__init__(['id', 'name', 'kind', 'limit', 'round', 'players', 'forhont', 'is_present', 'is_invited', 'is_on_turn', 'has_password', 'chat_posts'])

    self.id		= g.id
    self.kind		= g.kind
    self.name		= g.name
    self.limit		= g.limit
    self.round		= g.round
    self.players	= [ApiUserInfo(p) for p in g.players.itervalues()]

    if g.forhont_player != None:
      self.forhont	= hlib.api.ApiUserInfo(g.forhont_player.user)

    self.is_present	= g.has_player(hruntime.user)
    self.is_invited	= g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user)
    self.is_on_turn	= g.has_player(hruntime.user) and g.my_player.is_on_turn
    self.has_password	= g.is_password_protected
    if g.chat.unread > 0:
      self.chat_posts	= g.chat.unread
    else:
      self.chat_posts	= False

class ApiRecentEvents(ApiJSON):
  def __init__(self):
    super(ApiRecentEvents, self).__init__(['games', 'free_games', 'finished_games'])

    self.games = []
    self.free_games = []
    self.finished_games = []

class Handler(handlers.GenericHandler):
  @require_login
  @api
  def recent_events(self):
    import games

    re = ApiRecentEvents()

    for g in games.f_active(hruntime.user):
      if g.has_player(hruntime.user) and g.my_player.is_on_turn or g.has_player(hruntime.user) and not g.has_confirmed_player(hruntime.user) or g.has_player(hruntime.user):
        re.games.append(ApiGame(g))
      else:
        re.free_games.append(ApiGame(g))

    return ApiReply(200, events = re)

  @require_login
  @page
  def index(self):
    return self.generate('home.mako')
