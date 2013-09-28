import collections
import threading

import hlib.api
import hlib.event
import hlib.input
import hlib.error

import games
import lib.datalayer
import lib.chat
import lib.play

# pylint: disable-msg=F0401
import hruntime

ValidateTID = hlib.input.validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

class TournamentLists(lib.play.PlayableLists):
  def get_objects(self, l):
    return [hruntime.dbroot.tournaments[tid] for tid in l]

  def get_active(self, user):
    return [t.id for t in hruntime.dbroot.tournaments.values() if t.is_active and (t.has_player(user) or t.stage == Tournament.STAGE_FREE)]

  def get_inactive(self, user):
    return [t.id for t in hruntime.dbroot.tournaments.values() if not t.is_active and t.has_player(user)]

  def get_archived(self, user):
    return [t.id for t in hruntime.dbroot.tournaments_archived.values() if user.name in t.players]

  # Shortcuts
  def created(self, t):
    with self._lock:
      super(TournamentLists, self).created(t)
      hruntime.dbroot.tournaments.push(t)

    return True

_tournament_lists = TournamentLists()

f_active        = _tournament_lists.f_active
f_inactive      = _tournament_lists.f_inactive
f_archived      = _tournament_lists.f_archived

import hlib.stats
hlib.stats.init_namespace('Tournaments lists', {
  'Active':			lambda s: dict([ (k.name, dict(tournaments = ', '.join([str(i) for i in v]))) for k, v in _tournament_lists.snapshot('active').items() ]),
  'Inactive':			lambda s: dict([ (k.name, dict(tournaments = ', '.join([str(i) for i in v]))) for k, v in _tournament_lists.snapshot('inactive').items() ]),
  'Archived':			lambda s: dict([ (k.name, dict(tournaments = ', '.join([str(i) for i in v]))) for k, v in _tournament_lists.snapshot('archived').items() ])
})

class TournamentCreationFlags(games.GameCreationFlags):
  FLAGS = ['name', 'desc', 'kind', 'owner', 'limit', 'engine']
  MAX_OPPONENTS = 16

class Player(lib.play.Player):
  def __init__(self, tournament, user):
    lib.play.Player.__init__(self, user)

    self.tournament		= tournament
    self.active			= True

  def __getattr__(self, name):
    if name == 'chat':
      return lib.chat.ChatPagerTournament(self.tournament)

    if name == 'points':
      return 0

    return lib.play.Player.__getattr__(self, name)

  def to_state(self):
    d = lib.play.Player.to_state(self)

    d['points'] = self.points

    return d

class Group(hlib.database.DBObject):
  def __init__(self, gid, tournament, round, players):
    hlib.database.DBObject.__init__(self)

    self.id			= gid
    self.tournament		= tournament
    self.round			= round
    self.players		= players

    self.games			= hlib.database.SimpleList()

  def __getattr__(self, name):
    if name == 'finished_games':
      return [g for g in self.games if g.type == games.Game.TYPE_FINISHED]

    if name == 'closed_games':
      return [g for g in self.games if g.type in [games.Game.TYPE_FINISHED, games.Game.TYPE_CANCELED]]

    return hlib.database.DBObject.__getattr__(self, name)

  def to_state(self):
    def __game_to_state(g):
      return {
        'id':			g.id,
        'round':		g.round,
        'players':		[{'user': hlib.api.User(p.user), 'points': p.points} for p in g.players.values()]
      }

    return {
      'id':			self.id,
      'players':		[{'user': hlib.api.User(p.user)} for p in self.players],
      'games':			[__game_to_state(g) for g in self.games]
    }

class Tournament(lib.play.Playable):
  STAGE_FREE     = 0
  STAGE_RUNNING  = 1
  STAGE_FINISHED = 2
  STAGE_CANCELED = 3

  def __init__(self, flags, num_players, engine_name):
    lib.play.Playable.__init__(self, flags)

    self.chat_class		= lib.chat.ChatPagerTournament

    self.stage			= Tournament.STAGE_FREE
    self.num_players		= num_players

    self.players		= hlib.database.SimpleMapping()

    self._v_engine		= None
    self.engine_name		= engine_name

    self.rounds			= hlib.database.SimpleMapping()

  def __getattr__(self, name):
    if name == 'is_active':
      return self.stage in (Tournament.STAGE_FREE, Tournament.STAGE_RUNNING)

    if name == 'is_finished':
      return self.stage == Tournament.STAGE_FINISHED

    if name == 'engine':
      if not hasattr(self, '_v_engine') or not self._v_engine:
        self._v_engine = tournaments.engines.engines[self.engine_name](self)

      return self._v_engine

    if name == 'chat':
      return lib.chat.ChatPagerTournament(self)

    return lib.play.Playable.__getattr__(self, name)

  def get_type(self):
    return 'tournament'

  def to_api(self):
    d = lib.play.Playable.to_api(self)

    d['is_game']		= False
    d['limit']			= self.flags.limit
    d['num_players']		= self.num_players

    return d

  def to_state(self):
    d = lib.play.Playable.to_state(self)

    d['tid']			= self.id
    d['stage']			= self.stage
    d['num_players']		= self.num_players

    d['rounds'] = [[g.to_state() for g in self.rounds[round]] for round in sorted(self.rounds.keys())]

    return d

  def create_games(self):
    self.rounds[self.round] = hlib.database.SimpleList()
    player_groups = self.engine.create_groups()

    group_id = 0
    for group in player_groups:
      group_id += 1
      self.rounds[self.round].append(group)

      kwargs = {'limit':		self.flags.limit,
                'turn_limit':		self.flags.turn_limit,
                'dont_shuffle':		True,
                'owner':		group.players[0].user,
                'label':		'Turnajovka \'%s\' - %i-%i' % (self.name, self.round, group_id)
                }

      # player_id 0 is game owner
      for player_id in range(1, self.flags.limit):
        kwargs['opponent' + str(player_id)] = group.players[player_id].user.name

      # pylint: disable-msg=W0142
      g = games.create_system_game(self.flags.kind, **kwargs)

      g.tournament = self
      g.tournament_group = group

      group.games.append(g)

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
      raise lib.play.AlreadyStartedError()

    if user in self.user_to_player:
      raise lib.play.AlreadyJoinedError()

    if self.is_password_protected and (password == None or len(password) <= 0 or lib.pwcrypt(password) != self.password):
      raise lib.play.WrongPasswordError()

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

    t.join_player(flags.owner, flags.password)

    return t

class TournamentError(hlib.error.BaseError):
  pass

hlib.event.Hook('tournament.Created', 'invalidate_caches',  lambda e: _tournament_lists.created(e.tournament))
hlib.event.Hook('torunament.Started', 'invalidate_caches',  lambda e: _tournament_lists.started(e.tournament))
hlib.event.Hook('tournament.Finished', 'invalidate_caches', lambda e: _tournament_lists.finished(e.tournament))
hlib.event.Hook('tournament.Archived', 'invalidate_caches', lambda e: _tournament_lists.archived(e.tournament))
hlib.event.Hook('tournament.Canceled', 'invalidate_caches', lambda e: _tournament_lists.canceled(e.tournament))
hlib.event.Hook('tournament.PlayerJoined', 'invalidate_caches', lambda e: _tournament_lists.inval_players(e.tournament))
hlib.event.Hook('tournament.PlayerInvited', 'invalidate_caches', lambda e: _tournament_lists.inval_players(e.tournament))
hlib.event.Hook('tournament.ChatPost', 'ivalidate_caches', lambda e: hruntime.cache.remove_for_users([p.user for p in e.tournament.players.values()], 'recent_events'))

import events.tournament

import tournaments.engines
import tournaments.engines.swiss
