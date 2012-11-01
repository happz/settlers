import collections
import pprint
import threading

import hlib.event
import hlib.input
import hlib.error

import games
import lib.datalayer
import lib.chat

import hruntime

ValidateTID = hlib.input.validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

class TournamentLists(object):
  def __init__(self):
    super(TournamentLists, self).__init__()

    self._lock          = threading.RLock()

    self._active        = {}
    self._inactive      = {}
    self._archived      = {}

  def __get_f_list(self, name, user, update):
    cache = getattr(self, '_' + name)

    with self._lock:
      if user.name not in cache:
        cache[user.name] = update()

      return cache[user.name]

  def f_active(self, user):
    return self.__get_f_list('active', user, lambda: [t for t in hruntime.dbroot.tournaments.values() if t.is_active and (t.has_player(user) or t.stage == Tournament.STAGE_FREE)])

  def f_inactive(self, user):
    return self.__get_f_list('inactive', user, lambda: [t for t in hruntime.dbroot.tournaments.values() if not t.is_active and t.has_player(user)])

  def f_archived(self, user):
    return self.__get_f_list('archived', user, lambda: [t for t in hruntime.dbroot.tournaments_archived.values() if user.name in t.players])

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

  def inval_players(self, t):
    with self._lock:
      for p in t.players.values():
        self._inval_user(p.user)

    return True

  # Shortcuts
  def tournament_created(self, t):
    with self._lock:
      hruntime.dbroot.tournaments.push(t)

      self.inval_players(t)

    return True

  def tournament_started(self, t):
    with self._lock:
      self.inval_players(t)

    return True

  def tournament_finished(self, t):
    with self._lock:
      self.inval_players(t)

    return True

_tournament_lists = TournamentLists()

f_active        = _tournament_lists.f_active
f_inactive      = _tournament_lists.f_inactive
f_archived      = _tournament_lists.f_archived

class Player(hlib.database.DBObject):
  def __init__(self, tournament, user):
    hlib.database.DBObject.__init__(self)

    self.tournament		= tournament
    self.user			= user
    self.confirmed		= True
    self.last_board		= 0
    self.active			= True

  def __getattr__(self, name):
    if name == 'chat':
      return lib.chat.ChatPagerTournament(self.tournament)

    if name == 'is_on_turn':
      return False

    raise AttributeError(name)

class Group(hlib.database.DBObject):
  def __init__(self, id, tournament, round, players):
    hlib.database.DBObject.__init__(self)

    self.id			= id
    self.tournament		= tournament
    self.round			= round
    self.players		= players

    self.games			= hlib.database.SimpleList()

  def __getattr__(self, name):
    if name == 'finished_games':
      return [g for g in self.games if g.type == games.Game.TYPE_FINISHED]

    if name == 'closed_games':
      return [g for g in self.games if g.type in [games.Game.TYPE_FINISHED, games.Game.TYPE_CANCELED]]

    raise AttributeError(name)

class Tournament(hlib.database.DBObject):
  STAGE_FREE     = 0
  STAGE_RUNNING  = 1
  STAGE_FINISHED = 2
  STAGE_CANCELED = 3

  def __init__(self, flags, num_players, engine_name):
    hlib.database.DBObject.__init__(self)

    self.flags			= flags

    self.id			= None
    self.kind			= flags.kind
    self.stage			= Tournament.STAGE_FREE
    self.owner			= flags.owner
    self.name			= flags.name
    self.password		= flags.password
    self.round			= 0
    self.limit			= flags.limit
    self.num_players		= num_players

    self.chat_posts		= lib.chat.ChatPosts()
    self.players		= hlib.database.SimpleMapping()

    self.events			= hlib.database.IndexedMapping()

    self._v_engine		= None
    self.engine_name		= engine_name

    self.rounds			= hlib.database.SimpleMapping()

  def __getattr__(self, name):
    if name == 'is_active':
      return self.stage in (Tournament.STAGE_FREE, Tournament.STAGE_RUNNING)

    if name == 'user_to_player':
      if not hasattr(self, '_v_user_to_player') or self._v_user_to_player == None:
        self._v_user_to_player = lib.UserToPlayerMap(self)
      return self._v_user_to_player

    if name == 'is_password_protected':
      return self.password != None and len(self.password) > 0

    if name == 'my_player':
      return self.user_to_player[hruntime.user]

    if name == 'engine':
      if not self._v_engine:
        self._v_engine = tournaments.engines.engines[self.engine_name](self)

      return self._v_engine

    if name == 'chat':
      return lib.chat.ChatPagerTournament(self)

    raise AttributeError(name)

  def has_player(self, user):
    return user in self.user_to_player

  def create_games(self):
    player_groups = self.engine.create_groups()

    group_id = 0
    for group in player_groups:
      group_id += 1

      kwargs = {'limit':		self.flags.limit,
                'turn_limit':		self.flags.turn_limit,
                'dont_shuffle':		True,
                'owner':		group.players[0].user,
                'label':		'Turnajovka \'%s\' - %i-%i' % (self.name, self.round, group_id),
                'data':			{
                  'tournament':		self,
                  'tournament_group':	group
                  }
                }

      # player_id 0 is game owner
      for player_id in range(1, self.flags.limit):
        kwargs['opponent' + str(j)] = group.players[j].user

      games.create_system_game(self.flags.kind, **kwargs)

  def next_round(self):
    self.engine.rank_players(self.get_games())
    self.round += 1
    self.create_games()

  def begin(self):
    self.stage = Tournament.STAGE_RUNNING
    self.round = 1
    self.create_games()

    hlib.event.trigger('tournament.Started', self, tournament = self)

  def finish(self):
    hlib.event.trigger('tournament.Finished', self, tournament = self)

  def cancel(self):
    hlib.event.trigger('tournament.Canceled', self, tournament = self)

  def join_player(self, user, password):
    if self.stage != Tournament.STAGE_FREE:
      raise TournamentAlreadyStartedError()

    if user in self.user_to_player:
      raise AlreadyJoinedError()

    if self.is_password_protected and (password == None or len(password) <= 0 or lib.pwcrypt(password.encode('ascii', 'replace')) != self.password):
      raise WrongPasswordError()

    player = self.engine.player_class(self, user)
    self.players[user.name] = player

    hlib.event.trigger('tournament.PlayerJoined', self, tournament = self, user = user)

    if len(self.players) >= self.num_players:
      self.begin()

    return player

  @staticmethod
  def create_tournament(flags, num_players, engine_name):
    t = Tournament(flags, num_players, engine_name)

    hlib.event.trigger('tournament.Created', t, tournament = t)

    p = t.join_player(flags.owner, flags.password)

    return t

class TournamentError(hlib.error.BaseError):
  pass

WrongPasswordError		= lambda: TournamentError(msg = 'Wrong password', reply_status = 401, no_code = True)
TournamentAlreadyStartedError	= lambda: TournamentError(msg = 'Game already started', reply_status = 401)
AlreadyJoinedError		= lambda: TournamentError(msg = 'Already joined game', reply_status = 402)

hlib.event.Hook('tournament.Created', 'invalidate_caches',  lambda e: _tournament_lists.tournament_created(e.tournament))
hlib.event.Hook('tournament.Finished', 'invalidate_caches', lambda e: _tournament_lists.tournament_finished(e.tournament))

import events.tournament

import tournaments.engines
import tournaments.engines.swiss
