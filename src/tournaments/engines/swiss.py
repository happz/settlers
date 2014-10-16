__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2014, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import collections
import random

import lib.datalayer
import tournaments
import tournaments.engines

import hlib.database

__all__ = []

class RoundStats(hlib.datalayer.DBObject):
  def __init__(self, round = None):
    hlib.datalayer.DBObject.__init__(self)

    self.round = round or 0.0

    self.winning_points = 0.0
    self.success = 0.0
    self.game_points = 0.0
    self.rand = 0.0
    self.placed_1 = 0.0
    self.placed_2 = 0.0
    self.placed_3 = 0.0

    self.finished = False

  def __enter__(self):
    return self

  def __exit__(self, *args):
    return False

  def __str__(self):
    d = collections.OrderedDict()
    d['round'] = self.round
    d['wps'] = self.winning_points
    d['success'] = self.success
    d['gps'] = self.game_points
    d['placed_1'] = self.placed_1
    d['placed_2'] = self.placed_2
    d['placed_3'] = self.placed_3
    d['rand'] = self.rand
    d['finished'] = self.finished

    return ', '.join(['{}={:>9}'.format(key, '%.2f' % value) for key, value in d.items()])

class Player(tournaments.Player):
  def __init__(self, tournament, user):
    tournaments.Player.__init__(self, tournament, user)

    self.round_stats = hlib.database.SimpleList()
    self._v_summary_stats = None

    self.bye_player = False

  def __getattr__(self, name):
    if name == 'last_stats':
      return self.round_stats[-1] if len(self.round_stats) > 0 else None

    if name == 'finished_stats':
      return [s for s in self.round_stats if s.finished == True]

    if name == 'summary_stats':
      if not self._v_summary_stats:
        finished_stats = self.finished_stats
        finished_stats_cnt = float(len(finished_stats))

        self._v_summary_stats = RoundStats()

        if finished_stats_cnt > 0:
          with self._v_summary_stats as ss:
            ss.winning_points = sum([s.winning_points for s in finished_stats])
            ss.success = sum([s.success for s in finished_stats]) / finished_stats_cnt
            ss.game_points = sum([s.game_points for s in finished_stats])
            ss.placed_1 = sum([s.placed_1 for s in finished_stats])
            ss.placed_2 = sum([s.placed_2 for s in finished_stats])
            ss.placed_3 = sum([s.placed_3 for s in finished_stats])

      return self._v_summary_stats

    return hlib.database.DBObject.__getattr__(self, name)

  def __repr__(self):
    return '%s' % self.user.name

  def start_round_stats(self):
    self.round_stats.append(RoundStats(round = self.tournament.round))

  def reset_summary_stats(self):
    self._v_summary_stats = None

def sort_players_cmp(a, b):
  with a.summary_stats as ssa, b.summary_stats as ssb:
    if ssa.winning_points > ssb.winning_points:
      return 1
    if ssb.winning_points > ssa.winning_points:
      return -1

    if ssa.success > ssb.success:
      return 1
    if ssb.success > ssa.success:
      return -1

    if ssa.game_points > ssb.game_points:
      return 1
    if ssb.game_points > ssa.game_points:
      return -1

    if ssa.placed_1 > ssb.placed_1:
      return 1
    if ssb.placed_1 > ssa.placed_1:
      return -1

    if ssa.placed_2 > ssb.placed_2:
      return 1
    if ssb.placed_2 > ssa.placed_2:
      return -1

    if ssa.placed_3 > ssb.placed_3:
      return 1
    if ssb.placed_3 > ssa.placed_3:
      return -1

    if a.last_stats.rand > b.last_stats.rand:
      return 1
    if b.last_stats.rand > a.last_stats.rand:
      return -1

  return 0

class Engine(tournaments.engines.Engine):
  player_class = Player

  def sort_players(self, players, reverse = False):
    reverse = not reverse
    return sorted(players, cmp = sort_players_cmp, reverse = reverse)

  def create_groups(self):
    T = self.tournament

    # create round stats for each player and randomize
    for p in T.players.values():
      p.reset_summary_stats()
      p.start_round_stats()
      p.last_stats.rand = random.randrange(0, 1000000)

    players = self.sort_players([p for p in T.players.values()], reverse = True)
    groups = []

    missing_player = Engine.player_class(T, tournaments.Tournament.MISSING_USER)

    def __player_lister_0(gid):
      """
      No missing player
      """

      start = T.game_flags.limit * gid
      end   = start + T.game_flags.limit

      return players[start:end]

    def __player_lister_3(gid):
      placeholders = []
      if gid == 0:
        start = 0
        end   = T.game_flags.limit - 1
        placeholders = [missing_player]
      else:
        start = T.game_flags.limit - 1 + T.game_flags.limit * (gid - 1)
        end   = start + T.game_flags.limit

      return players[start:end] + placeholders

    def __player_lister_2(gid):
      placeholders = []
      if gid in (0, 1):
        start = (T.game_flags.limit - 1) * gid
        end   = start + T.game_flags.limit - 1
        placeholders = [missing_player]
      else:
        start = (T.game_flags.limit - 1) * 2 + T.game_flags.limit * (gid - 2)
        end   = start + T.game_flags.limit

      return players[start:end] + placeholders

    def __player_lister_1(gid):
      if gid == 0:
        players[0].bye_player = True

        start = 1
        end   = start + T.game_flags.limit
      else:
        start = 1 + T.game_flags.limit * gid
        end   = start + T.game_flags.limit

      return players[start:end]

    group_size      = T.flags.limit / T.game_flags.limit
    group_remainder = T.flags.limit % T.game_flags.limit

    player_listers = [
      __player_lister_0,
      __player_lister_1,
      __player_lister_2,
      __player_lister_3
    ]

    group_counts = [
      group_size,
      group_size,
      group_size + 1,
      group_size + 1
    ]

    for i in range(0, group_counts[group_remainder]):
      group_players = player_listers[group_remainder](i)
      groups.append(tournaments.Group(i, T, T.round, group_players))

    return groups

  def __evaluate_game(self, G):
    T = self.tournament
    UP = T.user_to_player

    ## winning points
    loosers = sorted([p for p in G.players.values() if p != G.forhont_player],
                     key = lambda x: x.points, reverse = True)
    loosers_points = [min(p.points, 10) for p in loosers]

    with UP[G.forhont_player.user].last_stats as ls:
      ls.winning_points = 4.0
      ls.placed_1 = 1.0

    if loosers_points[0] == loosers_points[1]:
      if len(G.players) == 4:
        if loosers_points[1] == loosers_points[2]:
          with UP[loosers[0].user].last_stats as ls:
            ls.winning_points = 2.0
            ls.placed_2 = 1.0
          with UP[loosers[1].user].last_stats as ls:
            ls.winning_points = 2.0
            ls.placed_2 = 1.0
          with UP[loosers[2].user].last_stats as ls:
            ls.winning_points = 2.0
            ls.placed_2 = 1.0
          ##

        else:
          with UP[loosers[0].user].last_stats as ls:
            ls.winning_points = 2.5
            ls.placed_2 = 1.0
          with UP[loosers[1].user].last_stats as ls:
            ls.winning_points = 2.5
            ls.placed_2 = 1.0
          with UP[loosers[2].user].last_stats as ls:
            ls.winning_points = 1.0
            # no placed_4
          ##

      else:
        with UP[loosers[0].user].last_stats as ls:
          ls.winning_points = 2.5
          ls.placed_2 = 1.0
        with UP[loosers[1].user].last_stats as ls:
          ls.winning_points = 2.5
          ls.placed_2 = 1.0
        ##

    else:
      with UP[loosers[0].user].last_stats as ls:
        ls.winning_points = 3.0
        ls.placed_2 = 1.0

      if len(G.players) == 4:
        if loosers_points[1] == loosers_points[2]:
          with UP[loosers[1].user].last_stats as ls:
            ls.winning_points = 1.5
            ls.placed_3 = 1.0
          with UP[loosers[2].user].last_stats as ls:
            ls.winning_points = 1.5
            ls.placed_3 = 1.0
          ##

        else:
          with UP[loosers[1].user].last_stats as ls:
            ls.winning_points = 2.0
            ls.placed_3 = 1.0
          with UP[loosers[2].user].last_stats as ls:
            ls.winning_points = 1.0
            # no placed_4
          ##

      else:
        with UP[loosers[1].user].last_stats as ls:
          ls.winning_points = 2.0
          ls.placed_3 = 1.0

    ## points and success rate
    sum_points = float(sum([min(p.points, 10) for p in G.players.values()]))
    for p in G.players.values():
      UP[p.user].last_stats.game_points = min(p.points, 10)
      UP[p.user].last_stats.success = float(min(p.points, 10)) / sum_points

  def __evaluate_round(self, groups):
    T = self.tournament

    for p in T.players.values():
      p.reset_summary_stats()

    for group in groups:
      for game in group.completed_games:
        self.__evaluate_game(game)

    for p in T.players.values():
      p.last_stats.finished = True

  def __evaluate_finals(self):
    T = self.tournament

    players = self.sort_players(T.players.values()[:])
    T.winner_player = players[0]

  def round_finished(self):
    T = self.tournament

    self.__evaluate_round(T.current_round)

    if T.round == T.flags.limit_rounds:
      self.__evaluate_finals()

tournaments.engines.engines['swiss'] = Engine
