"""
Basic game classes
"""

__author__		= 'Milos Prchlik'
__copyright__		= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__		= 'happz@happz.cz'
__license__		= 'http://www.php-suit.com/dpl'

import sys
import threading
import time

import hlib
import hlib.error
import hlib.event
import hlib.i18n
import hlib.input
import hlib.log

import lib
import lib.chat
import lib.datalayer

# pylint: disable-msg=F0401
import hruntime

GAME_KINDS = ['settlers']
"""
List of all known game kinds.

@type:			C{list} of C{string}s
"""

ValidateKind = hlib.input.validator_factory(hlib.input.CommonString(), hlib.input.OneOf(GAME_KINDS))
ValidateGID  = hlib.input.validator_factory(hlib.input.NotEmpty(), hlib.input.Int())
ValidateCardID = hlib.input.validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

class GenericValidateGID(hlib.input.SchemaValidator):
  gid = ValidateGID()

# ----- Lists --------------------------------
class GameLists(object):
  def __init__(self):
    super(GameLists, self).__init__()

    self._lock		= threading.RLock()

    self._active	= {}
    self._inactive	= {}
    self._archived	= {}

  def __get_f_list(self, name, user, update):
    cache = getattr(self, '_' + name)

    with self._lock:
      if user.name not in cache:
        cache[user.name] = update()

      return cache[user.name]

  def f_active(self, user):
    return self.__get_f_list('active', user, lambda: [g for g in hruntime.dbroot.games.itervalues() if g.is_active and (g.has_player(user) or (g.is_global_free() or g.is_personal_free(user)))])

  def f_inactive(self, user):
    return self.__get_f_list('inactive', user, lambda: [g for g in hruntime.dbroot.games.itervalues() if not g.is_active and g.has_player(user)])

  def f_archived(self, user):
    return self.__get_f_list('archived', user, lambda: [g for g in hruntime.dbroot.games_archive.itervalues() if user.name in g.players])

  # Cache invalidation
  def _inval_user(self, user):
    with self._lock:
      try:
        del self._active[user.name]
      except KeyError:
        pass

      try:
        del self._inactive[user.name]
      except KeyError:
        pass

      try:
        del self._archived[user.name]
      except KeyError:
        pass

    return True

  def inval_players(self, g):
    with self._lock:
      for p in g.players.itervalues():
        self._inval_user(p.user)

    return True

  # Shortcuts
  def game_created(self, g):
    with self._lock:
      hruntime.dbroot.games.push(g)

      self.inval_players(g)

    return True

  def game_started(self, g):
    with self._lock:
      self.inval_players(g)

    return True

  def game_finished(self, g):
    with self._lock:
      self.inval_players(g)

    return True

_game_lists = GameLists()

f_active	= _game_lists.f_active
f_inactive	= _game_lists.f_inactive
f_archived	= _game_lists.f_archived

def game_module(k, submodule = None):
  return sys.modules['games.' + k + ('.' + submodule if submodule != None else '')]

class GameCreationFlags(hlib.database.DBObject):
  FLAGS = ['name', 'limit', 'turn_limit', 'password', 'desc', 'kind', 'opponent1', 'opponent2', 'opponent3', 'tournament_players', 'dont_shuffle', 'owner']

  def __init__(self, kwargs):
    hlib.database.DBObject.__init__(self)

    self.flags = kwargs

  def __getattr__(self, name):
    if name in self.FLAGS:
      return self.flags.get(name, None)

    if name == 'opponents':
      return [self.opponent1, self.opponent2, self.opponent3]

    return hlib.database.DBObject.__getattr__(self, name)

  def __setattr__(self, name, value):
    if name in self.FLAGS:
      self.flags[name] = value
      return

    hlib.database.DBObject.__setattr__(self, name, value)

class Card(hlib.database.DBObject):
  def __init__(self, game, player, typ, bought):
    hlib.database.DBObject.__init__(self)

    self.game		= game
    self.id		= None
    self.player		= player
    self.type		= typ
    self.bought		= bought
    self.used		= 0

  def __getattr__(self, name):
    if name == 'is_used':
      return self.used > 0

    raise AttributeError(name)

  def to_api(self):
    return {
      'id':		self.id,
      'type':		self.type,
      'bought':		self.bought,
      'used':		self.used
    }

class Player(hlib.database.DBObject):
  def __init__(self, game, user):
    hlib.database.DBObject.__init__(self)

    self.game		= game
    self.id		= None
    self.user		= user
    self.last_board	= 0
    self.turns_missed	= 0
    self.turns_missed_notlogged = 0
    self.confirmed	= True

  def __getattr__(self, name):
    if name == 'is_on_turn':
      return self.game.type not in [Game.TYPE_FREE, Game.TYPE_FINISHED, Game.TYPE_CANCELED] and self.game.is_forhont_player(self)

    if name == 'is_slacker':
      return self.turns_missed > Game.TURNS_MISSED or self.turns_missed_notlogged > Game.TURNS_MISSED_NOTLOGGED or self.confirmed == False

    if name == 'points':
      return 0

    if name == 'can_pass':
      return self.game.type == Game.TYPE_GAME and self.is_on_turn

    if name == 'chat':
      return lib.chat.ChatPagerGame(self.game)

    raise AttributeError(name)

  def update_state(self, state):
    state.update(['is_confirmed', 'is_on_turn', 'can_pass'])

    state.is_confirmed		= self.confirmed
    state.is_on_turn		= self.is_on_turn
    state.can_pass		= self.can_pass

  def add_resource_raw(self, resource, amount):
    self.resources[resource] += amount

  def has_too_many_misses(self, logged = None):
    if logged == None:
      return self.turns_missed > Game.TURNS_MISSED or self.turns_missed_notlogged > Game.TURNS_MISSED_NOTLOGGED

    elif logged == True:
      return self.turns_missed > Game.TURNS_MISSED

    else:
      return self.turns_missed_notlogged > Game.TURNS_MISSED_NOTLOGGED

  def has_resources_for(self, desc):
    for (r, a) in desc.iteritems():
      if self.resources[r] < a:
        return False

    return True

  def spend_resources_for(self, desc):
    for (r, a) in desc.iteritems():
      self.resources[r] = self.resources[r] - a

class Game(hlib.database.DBObject):
  TIMEOUT_BEGIN_TYPES = []
  TIMEOUT_TURN_TYPES  = []

  TYPE_FREE              =  0
  TYPE_GAME              =  1
  TYPE_FINISHED          =  2
  TYPE_CANCELED          =  3

  TURNS_MISSED           = 2
  TURNS_MISSED_NOTLOGGED = 2

  def __init__(self, flags, player_class):
    hlib.database.DBObject.__init__(self)

    self.flags		= flags
    self.player_class	= player_class

    self.id		= None
    self.type		= Game.TYPE_FREE
    self.owner		= flags.owner
    self.name		= flags.name
    self.desc		= flags.desc
    self.password	= flags.password
    self.limit		= flags.limit
    self.round		= 0
    self.forhont	= 0
    self.last_pass	= hruntime.time
    self.deleted	= False
    self.turn_limit	= flags.turn_limit
    self.kind		= flags.kind
    self.suspended	= False
    self.autoplayer	= False

    self.tournament	= None
    self.tournament_round = None
    self.tournament_group = None

    self.chat_posts     = lib.chat.ChatPosts()
    self.players	= hlib.database.IndexedMapping()

    self.board		= None

    self.events		= hlib.database.IndexedMapping()

  def __getattr__(self, name):
    if name == 'user_to_player':
      if not hasattr(self, '_v_user_to_player') or self._v_user_to_player == None:
        self._v_user_to_player = lib.UserToPlayerMap(self)

      return self._v_user_to_player

    if name == 'forhont_player':
      return self.players[self.forhont] if len(self.players) > 0 else None

    if name == 'my_player':
      return self.user_to_player[hruntime.user]

    if name == 'am_i_on_turn':
      return self.forhont_player == self.my_player

    if name == 'is_free':
      return self.is_global_free() or self.is_personal_free(hruntime.user)

    if name == 'is_deleted':
      return self.deleted == True

    if name == 'is_password_protected':
      return self.password != None and len(self.password) > 0

    if name == 'is_finished':
      return self.type == Game.TYPE_FINISHED

    if name == 'is_canceled':
      return self.type == Game.TYPE_CANCELED

    if name == 'is_completed':
      return self.is_finished or self.is_canceled

    if name == 'is_suspended':
      return self.suspended == True

    if name == 'is_active':
      return self.type not in [Game.TYPE_FINISHED, Game.TYPE_CANCELED] and not self.is_deleted and not self.is_suspended

    if name == 'is_inactive':
      return self.type in [Game.TYPE_FINISHED, Game.TYPE_CANCELED] or self.is_deleted or self.is_suspended

    if name == 'chat':
      return lib.chat.ChatPagerGame(self)

    if name == 'is_waiting_begin':
      return self.type in self.TIMEOUT_BEGIN_TYPES

    if name == 'is_waiting_turn':
      return self.type not in self.TIMEOUT_TURN_TYPES

    if name == 'has_all_confirmed':
      if len(self.players) < self.limit:
        return False

      for p in self.players.itervalues():
        if p.confirmed != True:
          return False

      return True

    if name == 'has_invited_players':
      for p in self.players.itervalues():
        if p.confirmed == False:
          return True

      return False

    if name == 'confirmed_players':
      ret = {}

      for p in self.players.itervalues():
        if p.confirmed == True:
          ret[p.id] = p

      return ret

    if name == 'has_next_player':
      for p in self.players.itervalues():
        if p.id == self.forhont_player.id:
          continue

        if p.has_too_many_misses():
          continue

        return True
      return False

    if name == 'can_be_archived':
      if self.is_active:
        return False

      atime = self.last_pass

      for p in self.players.itervalues():
        chat_lister = lib.chat.ChatPagerGame(self, accessed_by = p)
        if chat_lister.unread > 0:
          return False

        atime = max(atime, p.last_board)

      if hruntime.time - atime < (86400 * 6 * 30):
        return False

      return True

    if name == 'deadline':
      d = self.last_pass + self.turn_limit

      if len(self.players) <= 0:
        return d

      if len(self.forhont_player.user.vacations) > 0:
        for v in [w for w in self.forhont_player.user.vacations if (w.start <= self.last_pass and self.last_pass <= w.start + w.length) or (self.last_pass <= w.start)]:
          if v.start > d:
            break

          if v.killed:
            length = v.killed - v.start

          else:
            length = v.length

          if v.start < self.last_pass:
            if v.killed > self.last_pass:
              d += (v.killed - self.last_pass)
            else:
              d += (v.start + v.length - self.last_pass)
          else:
            d += length

      return d

    raise AttributeError(name)

  def update_state(self, state):
    state.update(['state', 'my_player', 'forhont_player', 'has_all_confirmed'])

    state.state 		= self.type
    state.my_player		= self.my_player.id
    state.forhont_player	= self.forhont_player.id
    state.has_all_confirmed	= self.has_all_confirmed

  def is_personal_free(self, user):
    return self.type == Game.TYPE_FREE and self.has_player(user)

  def is_global_free(self):
    return self.type == Game.TYPE_FREE and self.limit > len(self.players)

  def reset_players(self):
    self.players = None

  def has_player(self, user):
    """
    Returns True if exists player with USERID same as USER.id
    """

    return user in self.user_to_player

  def has_confirmed_player(self, user):
    """
    Returns True if exists player with USERID same as USER.id and player is confirmed
    """

    for p in self.confirmed_players.itervalues():
      if p.user.name == user.name:
        return True

    return False

  def join_player(self, user, password, invite = False):
    if user not in self.user_to_player:
      if self.is_password_protected and (password == None or len(password) <= 0 or lib.pwcrypt(password.encode('ascii', 'replace')) != self.password):
        raise WrongPasswordError()

      if len(self.players) >= self.limit:
        raise GameAlreadyStartedError()

      player = self.player_class(self, user)

      self.players.push(player)

    else:
      player = self.user_to_player[user]

      if player.confirmed == True:
        raise AlreadyJoinedError()

      player.confirmed = True

    if invite:
      player.confirmed = False

    else:
      hlib.event.trigger('game.PlayerJoined', self, game = self, user = player.user)

      # pylint: disable-msg=W0201
      self.last_pass = hruntime.time

      if len(self.confirmed_players) == self.limit:
        self.begin()

    return player

  def begin(self):
    hlib.event.trigger('game.GameStarted', self, game = self)

  def finish(self):
    self.type = Game.TYPE_FINISHED
    self.last_pass = hruntime.time

    for p in self.players.itervalues():
      p.user.vacation_add_game()

    hlib.event.trigger('game.GameFinished', self, game = self)

  def cancel(self, reason = None, user = None):
    self.type = Game.TYPE_CANCELED

    if reason == None:
      hlib.event.trigger('game.GameCanceled', self, game = self)

    else:
      hlib.event.trigger('game.GameCanceled', self, game = self, reason = reason, user = user)

  def do_pass_turn(self, forced = False):
    pass

  def pass_turn_real(self, record = True, forced = False):
    if record:
      prev_player = self.forhont_player
      next_round = self.do_pass_turn(forced = forced)
      next_player = self.forhont_player

      hlib.event.trigger('game.Pass', self, game = self, prev = prev_player.user, next = next_player.user)

    else:
      next_round = self.do_pass_turn(forced = forced)

    if next_round == True:
      self.round = self.round + 1

  def pass_turn(self, check = True, record = False, forced = False):
    if check == True:
      if not self.my_player.is_on_turn:
        raise NotYourTurnError()

      if not self.my_player.can_pass:
        raise NotYourTurnError()

      self.last_pass = hruntime.time
      self.pass_turn_real()
    else:
      self.pass_turn_real(record = record, forced = forced)

  def is_forhont_player(self, p):
    return self.forhont_player.id == p.id

  @staticmethod
  def create_game(game_class, flags, system_game = False):
    opponents = []
    for opponent_name in flags.opponents:
      if opponent_name == None or len(opponent_name) <= 0:
        continue

      # fuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuj
      if opponent_name not in hruntime.dbroot.users:
        raise NoSuchPlayerError()

      opponent = hruntime.dbroot.users[opponent_name]

      if opponent == flags.owner and system_game != True:
        raise WrongInviteError()

      if opponent in opponents:
        raise DoubleInviteError()

      opponents.append(opponent)

    if len(opponents) > flags.limit - 1:
      raise TooManyInvitesError()

    if flags.password == '' or flags.password == None:
      flags.password = None

    else:
      flags.password = lib.pwcrypt(flags.password.encode('ascii', 'replace'))

    g = game_class(flags)

    hlib.event.trigger('game.GameCreated', g, game = g)

    if flags.owner != hruntime.dbroot.users['SYSTEM']:
      g.join_player(flags.owner, flags.password)

    for u in opponents:
      if u in g.user_to_player:
        raise AlreadyJoinedError()

      p = g.join(u, flags.password, invite = True)

      hlib.event.trigger('game.PlayerInvited', g, game = g, user = p.user)

    return g

# --- Classes --------------------------------------------------------
class GameError(hlib.error.Error):
  pass

WrongPasswordError		= lambda: GameError(msg = 'Wrong password', reply_status = 401, no_code = True)
GameAlreadyStartedError		= lambda: GameError(msg = 'Game already started', reply_status = 401)
AlreadyJoinedError		= lambda: GameError(msg = 'Already joined game', reply_status = 402)
NotYourTurnError		= lambda: GameError(msg = 'Not your turn', reply_status = 402)
NameAlreadyExistsError		= lambda: GameError(msg = 'Such name already exists', reply_status = 403, no_code = True, invalid_field = 'name')
NoSuchPlayerError		= lambda: GameError(msg = 'No such player', reply_status = 403)
WrongInviteError		= lambda: GameError(msg = 'You can not invite this player', reply_status = 402)
DoubleInviteError		= lambda: GameError(msg = 'You can not invite one player twice', reply_status = 402)
TooManyInvitesError		= lambda: GameError(msg = 'Too many invited players', reply_status = 402)
NotEnoughResourcesError		= lambda: GameError(msg = 'You do not have enough resources', reply_status = 403)
InactiveCardError               = lambda: games.GameError(msg = 'This card is not active right now', reply_status = 402)

class _DummyOwner(hlib.database.DBObject):
  def __init__(self):
    hlib.database.DBObject.__init__(self)

    self.id = -1

def DummyOwner():
  if not hruntime.dbroot.dummy_owner:
    hruntime.dbroot.dummy_owner = _DummyOwner()

  return hruntime.dbroot.dummy_owner

class OwnerableDBObject(hlib.database.DBObject):
  def __init__(self, game, typ, owner):
    hlib.database.DBObject.__init__(self)

    self.game		= game
    self.id		= None
    self.type		= typ
    self.owner		= owner

  def to_api(self):
    return {
      'id':		self.id,
      'type':		self.type,
      'owner':		self.owner.id
    }

  def is_owner(self, player):
    return self.owner.id == player.id

class Resource(object):
  RESOURCE_FREE    = -2
  RESOURCE_UNKNOWN = -1
  RESOURCE_MIN     =  0
  RESOURCE_MAX     =  0

  map_resource2str = {-2: 'free',
                      -1: 'unknown'
                     }

  map_str2resource = {'free':    -2,
                      'unknown': -1
                     }

class Resources(hlib.database.DBObject):
  # pylint: disable-msg=E1002
  def __init__(self):
    hlib.database.DBObject.__init__(self)

  def __len__(self):
    # pylint: disable-msg=R0201
    return 0

  def __getitem__(self, key):
    return getattr(self, key)

  def __setitem__(self, key, value):
    setattr(self, key, value)

  def add(self, key, value):
    self[key] += value

  def keys(self):
    # pylint: disable-msg=R0201
    return []

  def values(self):
    # pylint: disable-msg=R0201
    return []

  def update(self):
    # pylint: disable-msg=R0201
    return {}

  def sum(self):
    return sum(self.values())

  def __str__(self):
    return ', '.join([str(k) + '=' + str(self[k]) for k in self.keys()])

class Board(hlib.database.DBObject):
  def __init__(self, game):
    hlib.database.DBObject.__init__(self)

    self.game		= game

    self.render_offset = None
    self.controls = None

def create_system_game(kind, label = None, owner = None, **kwargs):
  gm = games.game_module(kind)

  owner = owner or hruntime.dbroot.users[1]

  if label == None:
    label = 'SH - ' + time.strftime('%d/%m/%Y %H:%M:%S', hruntime.localtime)

  flags = gm.GameCreationFlags(kwargs)

  flags.name      = label
  flags.password  = None
  flags.desc      = ''
  flags.opponent1 = kwargs.get('opponent1', None)
  flags.opponent2 = kwargs.get('opponent2', None)
  flags.opponent3 = kwargs.get('opponent3', None)
  flags.owner     = owner

  g = gm.Game.create_game(flags, system_game = True)

  return g

# Event hooks
hlib.event.Hook('game.GameCreated', 'invalidate_caches',  lambda e: _game_lists.game_created(e.game))
hlib.event.Hook('game.GameFinished', 'invalidate_caches', lambda e: _game_lists.game_finished(e.game))
hlib.event.Hook('game.PlayerJoined', 'invalidate_caches', lambda e: _game_lists.inval_players(e.game))
hlib.event.Hook('game.PlayerInvited', 'invalidate_caches', lambda e: _game_lists.inval_players(e.game))

import games.settlers

import events.game
