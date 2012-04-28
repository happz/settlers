import lib.datalayer
import tournament.engines
import random

class PlayerRankingRecord(lib.datalayer.GenericRecord):
  TABLE         = 'ranker_swiss'
  FIELDS        = ['player', 'winning_points', 'success', 'points', 'place_1', 'place_2', 'place_3']
  UPDATE_FIELDS = ['winning_points', 'success', 'points', 'place_1', 'place_2', 'place_3']

  def __init__(self, r):
    super(PlayerRankingRecord, self).__init__(PlayerRankingRecord, r)

  @classmethod
  def load_from_db(cls, i):
    return lib.datalayer.load_from_db(cls = cls, keys = [('player', i)])

  def from_record(self, pr):
    pr.winning_points = self.winning_points
    pr.success = self.success
    pr.points  = self.points
    pr.place_1 = self.place_1
    pr.place_2 = self.place_2
    pr.place_3 = self.place_3

  def to_record(self, pr):
    self.winning_points = pr.winning_points
    self.success = pr.success
    self.points  = pr.points
    self.place_1 = pr.place_1
    self.place_2 = pr.place_2
    self.place_3 = pr.place_3

class PlayerRanking(tournament.engines.PlayerRanking):
  def __init__(self, user, record):
    super(PlayerRanking, self).__init__(user, record)

    self.winning_points = 0.0
    self.success = 0.0
    self.points = 0
    self.place_1 = 0
    self.place_2 = 0
    self.place_3 = 0
    self.rand = random.randrange(0, 1000000)

  def __iadd__(self, p):
    def __add(n):
      setattr(self, n, getattr(self, n) + getattr(p, n))

    __add('winning_points')
    __add('success')
    __add('points')
    __add('place_1')
    __add('place_2')
    __add('place_3')

    self.success /= 2.0

  def __str__(self):
    return '%i:\t%.2f\t%.2f\t%i\t%i\t%i\t%i' % (self.user.id, self.winning_points, self.success, self.points, self.place_1, self.place_2, self.place_3)

def __sort_players(a, b):
  if a.winning_points > b.winning_points:
    return 1

  if b.winning_points > a.winning_points:
    return -1

  if a.success > b.success:
    return 1
  if b.success > a.success:
    return -1

  if a.points > b.points:
    return 1
  if b.points > a.points:
    return -1

  if a.place_1 > b.place_1:
    return 1
  if b.place_1 > a.place_1:
    return -1

  if a.place_2 > b.place_2:
    return 1
  if b.place_2 > a.place_2:
    return -1

  if a.place_3 > b.place_3:
    return 1
  if b.place_3 > a.place_3:
    return -1

  if a.rand > b.rand:
    return 1
  if b.rand > a.rand:
    return -1

  return 0

def sort_players(prs):
  return sorted(prs, cmp = __sort_players, reverse = True)

def rate_game(g):
  ret = {}
  for p in g.players.itervalues():
    ret[p.user.id] = PlayerRanking(p.user, None)

  ## winning points
  players = sorted([p for p in g.players.itervalues() if p != g.forhont_player], key = lambda x: x.points)
  points = [p.points for p in players]

  ret[g.forhont_player.user.id].winning_points = 4.0

  if points[0] == points[1]:
    if g.limit == 4:
      if points[1] == points[2]:
        ret[players[0].user.id].winning_points = 2.0
        ret[players[1].user.id].winning_points = 2.0
        ret[players[2].user.id].winning_points = 2.0
        ##

      else:
        ret[players[0].user.id].winning_points = 3.0
        ret[players[1].user.id].winning_points = 2.0
        ret[players[2].user.id].winning_points = 1.0
        ##

    else:
      ret[players[0].user.id].winning_points = 2.5
      ret[players[1].user.id].winning_points = 2.5
      ##

  else:
    ret[players[0].user.id].winning_points = 3.0

    if g.limit == 4:
      if points[1] == points[2]:
        ret[players[1].user.id].winning_points = 1.5
        ret[players[2].user.id].winning_points = 1.5
        ##

      else:
        ret[players[1].user.id].winning_points = 2.0
        ret[players[2].user.id].winning_points = 1.0
        ##

    else:
      ret[players[2].user.id].winning_points = 2.0

  ## success rate
  sum_points = float(sum([p.points for p in g.players.itervalues()]))
  for p in g.players.itervalues():
    ret[p.user.id].success = float(p.points) / sum_points

  ## points
  for p in g.players.itervalues():
    ret[p.user.id].points = p.points

  ## places
  players = [g.forhont_player] + sorted([p for p in g.players.itervalues() if p != g.forhont_player], key = lambda x: x.points)
  ret[players[0].user.id].place_1 = 1
  ret[players[1].user.id].place_2 = 1
  ret[players[2].user.id].place_3 = 1

  return ret

def rate_round(gs):
  players = {}

  for g in gs:
    gr = rate_game(g)
    for uid, data in gr.iteritems():
      if uid in players:
        players[uid] += data

      else:
        players[uid] = data

  return sort_players(players.values())

def load_player_rankings(players):
  ret = []

  for p in players.itervalues():
    pr = PlayerRanking(p.user)
    dr = PlayerRankingRecord.load_from_db(p.id)

    dr.from_record(pr)

    ret.append(pr)

  return ret

class SwissTournamentEngine(tournament.engines.TournamentEngine):
  def prebegin(self):
    for p in self.tournament.players.itervalues():
      PlayerRankingRecord.create_in_db(data = {'player': p.id})

  def create_games(self):
    if self.tournament.round == 1:
      # first round, randomize
      prs = sort_players([PlayerRanking(p.user, None) for p in self.tournament.players.itervalues()])

    else:
      # next rounds, load ranking from db
      prs = sort_players(load_player_rankings(self.tournament.players))

    groups = []
    for i in range(0, len(self.tournament.players) / self.tournament.rules.limit):
      group = [pr.user.id for pr in prs[i * self.tournament.rules.limit:(i + 1) * self.tournament.rules.limit]]
      random.shuffle(group)
      groups.append(group)

    return groups

  def rank_players(self, gs):
    total   = load_player_rankings(self.tournament.players)
    current = rate_round(gs)

    for pr1 in total:
      for pr2 in current:
        if pr1.user.id == pr2.user.id:
          pr1 += pr2
          pr1.record.to_record(pr1)
          break

    return sort_players(total)

import tournament
tournament.ENGINES['swiss'] = SwissTournamentEngine
