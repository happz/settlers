__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2014, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import collections
import threading

from collections import OrderedDict

import hlib.api
import hlib.events
import hlib.input
import hlib.error

import games
import lib.datalayer
import lib.chat
import lib.play

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

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

from hlib.stats import stats as STATS
STATS.set('Tournaments lists', OrderedDict([
  ('Active', lambda s: dict([ (k.name, dict(tournaments = ', '.join([str(i) for i in v]))) for k, v in _tournament_lists.snapshot('active').items() ])),
  ('Inactive', lambda s: dict([ (k.name, dict(tournaments = ', '.join([str(i) for i in v]))) for k, v in _tournament_lists.snapshot('inactive').items() ])),
  ('Archived', lambda s: dict([ (k.name, dict(tournaments = ', '.join([str(i) for i in v]))) for k, v in _tournament_lists.snapshot('archived').items() ]))
]))

class TournamentCreationFlags(games.GameCreationFlags):
  FLAGS = ['name', 'desc', 'kind', 'owner', 'engine', 'password', 'num_players', 'limit_rounds']
  MAX_OPPONENTS = 48

class Player(lib.play.Player):
  def __init__(self, tournament, user):
    lib.play.Player.__init__(self, user)

    self.tournament = tournament
    self.active = True

    self.points = 0
    self.wins = 0

  def __getattr__(self, name):
    if name == 'chat':
      return lib.chat.ChatPagerTournament(self.tournament)

    return lib.play.Player.__getattr__(self, name)

  def __str__(self):
    return 'Player(name = "%s", active = %s, points = %i, wins = %i)' % (self.user.name, self.active, self.points, self.wins)

  def to_state(self):
    d = lib.play.Player.to_state(self)

    d['points'] = self.points
    d['wins'] = self.wins

    return d

class Group(hlib.database.DBObject):
  def __init__(self, gid, tournament, round, players):
    hlib.database.DBObject.__init__(self)

    self.id = gid
    self.tournament = tournament
    self.round = round
    self.players = players

    self.games = hlib.database.SimpleList()

  def __getattr__(self, name):
    if name == 'finished_games':
      return [g for g in self.games if g.type == games.Game.TYPE_FINISHED]

    if name == 'completed_games':
      return [g for g in self.games if g.type in [games.Game.TYPE_FINISHED, games.Game.TYPE_CANCELED]]

    return hlib.database.DBObject.__getattr__(self, name)

  def __str__(self):
    attrs = {
      'tid': self.tournament.id,
      'gid': self.id,
      'players': [str(p) for p in self.players],
      'games': self.games,
      'completed_games': self.completed_games
    }

    attrs = ', '.join(['%s = "%s"' % (key, value) for key, value in attrs.items()])

    return 'Group(%s)' % attrs

  def to_state(self):
    def __game_to_state(g):
      if not self.tournament.is_active or self.round != self.tournament.round:
        __player_to_state = lambda x: {'user': hlib.api.User(x.user), 'points': x.points}
      else:
        __player_to_state = lambda x: {'user': hlib.api.User(x.user)}

      return {
        'id': g.id,
        'round': g.round,
        'type': g.type,
        'players': [__player_to_state(p) for p in g.players.values()]
      }

    return {
      'id': self.id,
      'players': [{'user': hlib.api.User(p.user)} for p in self.players],
      'games': [__game_to_state(g) for g in self.games]
    }

class Tournament(lib.play.Playable):
  STAGE_FREE     = 0
  STAGE_RUNNING  = 1
  STAGE_FINISHED = 2
  STAGE_CANCELED = 3

  MISSING_USER = lib.datalayer.User('"MISSING" player', 'foobar', 'osadnici@happz.cz')
  BYE_USER     = lib.datalayer.User('"BYE" player', 'foobar', 'osadnici@happz.cz')

  def __init__(self, tournament_flags, game_flags):
    lib.play.Playable.__init__(self, tournament_flags)

    #if tournament_flags.limit % game_flags.limit != 0:
    #  raise WrongNumberOfPlayers()

    self.game_flags = game_flags

    self.chat_class = lib.chat.ChatPagerTournament

    self.stage = Tournament.STAGE_FREE

    self.players = hlib.database.SimpleMapping()
    self.winner_player = None

    self._v_engine = None
    self.engine_class = tournaments.engines.engines[self.flags.engine]
    self.engine_data = None

    self.rounds = hlib.database.SimpleMapping()

  def __getattr__(self, name):
    if name == 'is_active':
      return self.stage in (Tournament.STAGE_FREE, Tournament.STAGE_RUNNING)

    if name == 'is_finished':
      return self.stage == Tournament.STAGE_FINISHED

    if name == 'engine':
      if not hasattr(self, '_v_engine') or not self._v_engine:
        self._v_engine = self.engine_class(self)

      return self._v_engine

    if name == 'chat':
      return lib.chat.ChatPagerTournament(self)

    if name == 'current_round':
      return self.rounds[self.round]

    if name == 'completed_current_round':
      return [group for group in self.current_round if len(group.completed_games) == len(group.games)]

    return lib.play.Playable.__getattr__(self, name)

  def get_type(self):
    return 'tournament'

  def to_api(self):
    d = lib.play.Playable.to_api(self)

    d['is_game'] = False
    d['limit'] = self.limit
    d['limit_per_game'] = self.game_flags.limit
    d['limit_rounds'] = self.flags.limit_rounds
    d['winner'] = self.winner_player.to_state()

    return d

  def to_state(self):
    d = lib.play.Playable.to_state(self)

    d['tid'] = self.id
    d['stage'] = self.stage
    d['limit'] = self.limit
    d['limit_rounds'] = self.flags.limit_rounds
    d['winner'] = self.winner_player.to_state()

    d['rounds'] = [[g.to_state() for g in self.rounds[round]] for round in sorted(self.rounds.keys())]

    return d

  def create_games(self):
    # Create new round - list of player groups
    self.rounds[self.round] = ROUND = hlib.database.SimpleList()

    # Ask engine to group players
    player_groups = self.engine.create_groups()

    for group_id in range(0, len(player_groups)):
      GROUP = player_groups[group_id]

      ROUND.append(GROUP)

      real_players = [p for p in GROUP.players if p.user.name != '"MISSING" player']

      kwargs = {
        'limit': len(real_players),
        'turn_limit': self.game_flags.turn_limit,
        'dont_shuffle': True,
        'owner': real_players[0].user,
        'label': 'Turnajovka \'%s\' - %i-%i' % (self.name, self.round, group_id + 1)
      }

      for player_id in range(1, len(real_players)):
        kwargs['opponent' + str(player_id)] = real_players[player_id].user.name

      # pylint: disable-msg=W0142
      g = games.create_system_game(self.flags.kind, **kwargs)

      g.tournament = self
      g.tournament_group = GROUP

      GROUP.games.append(g)

  def next_round(self):
    self.engine.round_finished()

    if self.round == self.flags.limit_rounds:
      self.finish()
      return

    self.round += 1
    self.create_games()

  def begin(self):
    self.stage = Tournament.STAGE_RUNNING
    self.round = 1
    self.create_games()

    hlib.events.trigger('tournament.Started', self, tournament = self)

  def finish(self):
    self.stage = Tournament.STAGE_FINISHED

    hlib.events.trigger('tournament.Finished', self, tournament = self)

  def cancel(self):
    hlib.events.trigger('tournament.Canceled', self, tournament = self)

  def join_player(self, user, password):
    if self.stage != Tournament.STAGE_FREE:
      raise lib.play.AlreadyStartedError()

    if user in self.user_to_player:
      raise lib.play.AlreadyJoinedError()

    if self.is_password_protected and (password == None or len(password) <= 0 or lib.pwcrypt(password) != self.password):
      raise lib.play.WrongPasswordError()

    player = self.engine_class.player_class(self, user)
    self.players[user.name] = player

    hlib.events.trigger('tournament.PlayerJoined', self, tournament = self, user = user)

    if len(self.players) == self.flags.limit:
      self.begin()

    return player

  @staticmethod
  def create_tournament(tournament_flags, game_flags):
    t = Tournament(tournament_flags, game_flags)

    hlib.events.trigger('tournament.Created', t, tournament = t)

    if tournament_flags.owner != hruntime.dbroot.users['SYSTEM']:
      t.join_player(tournament_flags.owner, tournament_flags.password)

    return t

class TournamentError(lib.play.PlayableError):
  pass

WrongNumberOfPlayers = lambda: TournamentError(msg = 'Number of players of the tournament must be divisible by number of players per game', reply_status = 402)

hlib.events.Hook('tournament.Created', lambda e: _tournament_lists.created(e.tournament))
hlib.events.Hook('torunament.Started', lambda e: _tournament_lists.started(e.tournament))
hlib.events.Hook('tournament.Finished', lambda e: _tournament_lists.finished(e.tournament))
hlib.events.Hook('tournament.Archived', lambda e: _tournament_lists.archived(e.tournament))
hlib.events.Hook('tournament.Canceled', lambda e: _tournament_lists.canceled(e.tournament))
hlib.events.Hook('tournament.PlayerJoined', lambda e: _tournament_lists.inval_players(e.tournament))
hlib.events.Hook('tournament.PlayerInvited', lambda e: _tournament_lists.inval_players(e.tournament))
hlib.events.Hook('tournament.ChatPost', lambda e: hruntime.cache.remove_for_users([p.user for p in e.tournament.players.values()], 'recent_events'))

import events.tournament

import tournaments.engines
import tournaments.engines.swiss
import tournaments.engines.randomized
