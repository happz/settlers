import collections

import hlib.event
import hlib.input
import hlib.error

import games
import lib.datalayer
import lib.chat

import hruntime

f_free		= lambda _u: [t for t in hruntime.dbroot.tournaments.itervalues() if t.stage == Tournament.STAGE_FREE]
f_current	= lambda _u: [t for t in hruntime.dbroot.tournaments.itervalues() if t.stage == Tournament.STAGE_RUNNING  and t.has_player(hruntime.user)]
f_finished	= lambda _u: [t for t in hruntime.dbroot.tournaments.itervalues() if t.stage == Tournament.STAGE_FINISHED and t.has_player(hruntime.user)]
f_canceled	= lambda _u: [t for t in hruntime.dbroot.tournaments.itervalues() if t.stage == Tournament.STAGE_CANCELED and t.has_player(hruntime.user)]

ValidateTID = hlib.input.validator_factory(hlib.input.NotEmpty(), hlib.input.Int())

def load_tournaments_records(t, order = None, window = None, count_all = False, keys = None, by_user = None):
  keys = keys or []

  fields = list(TournamentRecord.FIELDS)

  if by_user != None:
    fields[0] = t + '`.`' + fields[0]
    keys.append('(`tournaments_players`.`tournament` = `%s`.`id` AND `tournaments_players`.`user` = %i)' % (t, by_user.id))
    t = t + ', tournaments_players'

  rs = lib.datalayer.simple_load_from_db(t, fields, order = order, window = window, empty_query = True, count_all = count_all, keys = keys)

  if count_all == True:
    return [[TournamentRecord(r) for r in rs[0]], rs[1]]

  return [TournamentRecord(r) for r in rs]

def load_tournaments(t, order = None, window = None, count_all = False, keys = None, by_user = None):
  rs = load_tournaments_records(t, order = order, window = window, count_all = count_all, keys = keys, by_user = by_user)

  if count_all == True:
    return [[Tournament(r) for r in rs[0]], rs[1]]

  return [Tournament(r) for r in rs]

class TournamentRules(hlib.database.DBObject):
  def __init__(self, flags):
    super(TournamentRules, self).__init__()

    self.tournament		= None
    self.limit			= flags.limit
    self.turn_limit		= flags.turn_limit

class TournamentPlayer(hlib.database.DBObject):
  def __init__(self, t, user):
    super(TournamentPlayer, self).__init__()

    self.tournament		= t
    self.user			= user
    self.confirmed		= True
    self.last_board		= 0
    self.active			= True

  def __getattribute__(self, name):
    if name == 'chat':
      return lib.chat.ChatPagerTournament(self.tournament)

    return super(TournamentPlayer, self).__getattribute__(name)

class TournamentRoundGroup(object):
  def __init__(self, tournament, round, group):
    object.__init__(self)

    self.tournament = tournament
    self.round = round
    self.group = group

    self._games = None
    self._players = None

  def __getattribute__(self, name):
    if name == 'games':
      if self._games == None:
        self._games = self.tournament.get_games(round = self.round, group = self.group)

      return self._games

    if name == 'finished_games':
      return [g for g in self.games if g.type == games.Game.TYPE_FINISHED]

    if name == 'closed_games':
      return [g for g in self.games if g.type in [games.Game.TYPE_FINISHED, games.Game.TYPE_CANCELED]]

    if name == 'players':
      if self._players == None:
        self._players = {}

        for p in self.games[0].players.itervalues():
          self.players[p.user.id] = self.tournament.players[p.user.id]

      return self._players

    return object.__getattribute__(self, name)

class Tournament(hlib.database.DBObject):
  STAGE_FREE     = 0
  STAGE_RUNNING  = 1
  STAGE_FINISHED = 2
  STAGE_CANCELED = 3

  def __init__(self, name, kind, owner, num_players, password, rules):
    super(Tournament, self).__init__()

    self.id			= None
    self.name			= name
    self.kind			= kind
    self.stage			= Tournament.STAGE_FREE
    self.round			= 0
    self.owner			= owner
    self.num_players		= num_players
    self.password		= password
    self.engine			= tournament.engines.swiss.SwissTournamentEngine()

    self.players		= hlib.database.IndexedMapping()
    self.rules			= rules

    self._user_to_player	= lib.UserToPlayerMap(self)

    self.events			= hlib.database.IndexedMapping()

  chat = property(lambda self: lib.chat.ChatPagerTournament(self))

  def __getattribute__(self, name):
    if name == 'has_password':
      return self.password != None and len(self.password) > 0

    if name == 'my_player':
      return self._user_to_player[hruntime.user]

    if name == 'has_closed_all_games':
      return self.get_has_all_closed_games()

    return super(Tournament, self).__getattribute__(name)

  def get_active_players(self, round = None):
    ret = collections.OrderedDict()
    round = round or self.round

    for p in self.players.itervalues():
      if p.active <= round:
        continue

      ret[p.user.id] = p

    return ret

  def get_groups(self, round = None):
    groups = {}
    seen_players = []
    byes = []

    for game in self.get_games(round = round):
      if game.tournament_group in groups:
        continue

      groups[game.tournament_group] = TournamentRoundGroup(self, round or self.round, game.tournament_group)

      for p in groups[game.tournament_group].players.itervalues():
        seen_players.append(p.user.id)

    byes = []
    for p in self.get_active_players(round = round).itervalues():
      if p.user.id in seen_players:
        continue

      byes.append(p.user)

    return (groups, byes)

  def get_games(self, round = None, group = None):
    round = round or self.round

    return [g for g in hruntime.dbroot.games.itervalues() if g.tournament == self.id and g.tournament_round == round and ((group and g.tournament_group == group) or (True))]

  def get_has_closed_all_games(self, round = None):
    round = round or self.round

    for g in self.get_groups(round = round)[0].itervalues():
      if len(g.closed_games) != self.rules.limit:
        return False

    return True

  def has_player(self, user):
    return user.id in self.players

  def has_confirmed_player(self, user):
    return self.has_player(user) and self.players[user.id].confirmed

  def create_games(self):
    player_groups = self.engine.create_games()

    i = 0
    for group in player_groups:
      i += 1
      kwargs = {'limit':      self.rules.limit,
                'turn_limit': self.rules.turn_limit,
                'dont_shuffle': True}

      for j in range(1, len(group)):
        kwargs['opponent' + str(j)] = hruntime.dbroot.users[j]

      games.create_system_game(self.kind, label = 'Turnajovka \'%s\' - %i-%i' % (self.name, self.round, i), owner = hruntime.dbroot.users[group[0]],
                               data = {'tournament': self.id, 'tournament_round': self.round, 'tournament_group': i}, **kwargs)
  def next_round(self):
    self.engine.rank_players(self.get_games())
    self.round = self.round + 1
    self.create_games()

  def begin(self):
    self.engine.prebegin()

    self.stage = Tournament.STAGE_RUNNING
    self.round = 1
    self.create_games()

    hlib.event.trigger('tournament.TournamentStarted', self, tournament = self)

  def finish(self):
    hlib.event.trigger('tournament.TournamentFinished', self, tournament = self)

  def cancel(self):
    hlib.event.trigger('tournament.TournamentCanceled', self, tournament = self)

  def add_player(self, user, password):
    assert len(self.players) < self.num_players, 'Too many players in tournament already!'
    assert user.id not in self.players, 'Already joined!'

    if len(self.players) >= self.num_players:
      raise hlib.error.Error(msg = 'Tournament started already')

    if self.has_password and password != self.password:
      raise hlib.error.Error(msg = 'Wrong password')

    p = TournamentPlayer(t, user)

    hlib.event.trigger('tournament.PlayerJoined', self, tournament = self, user = user)

    if len(self.players) >= self.num_players:
      self.begin()

    return p

  @staticmethod
  def create_tournament(kind, flags):
    mod_game = games.game_module(kind)
    mod_tour = games.game_module(kind, 'tour')
    classes = {'game':  mod_game.Game,
               'rules': mod_tour.TournamentRules}

    rules = classes['rules'](flags)
    t = Tournament(flags.name, flags.kind, flags.owner, flags.tournament_players, flags.password, rules)
    rules.tournament = t

    hlib.event.trigger('tournament.TournamentCreated', self, tournament = t)

    t.add_player(flags.owner, flags.password)

    return t


import games.settlers.tour

import events.tournament

#import tournament.engines.swiss
