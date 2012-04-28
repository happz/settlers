import threading

import lib.datalayer
import games.stats

import hlib.database
import hlib.log

# pylint: disable-msg=F0401
import hruntime

_stats_lock = threading.RLock()
_stats = None

class Stats(hlib.database.DBObject):
  def __init__(self, user, points, gs, finished, wons, points_per_game):
    # pylint: disable-msg=E1002
    super(Stats, self).__init__()

    self.user			= user
    self.points			= points
    self.games			= gs
    self.finished		= finished
    self.wons			= wons
    self.points_per_game	= points_per_game

  def __str__(self):
    return '%s: %i, %i, %f' % (self.user.name.encode('ascii', 'replace'), self.points, self.games, self.points_per_game)

class GamesStats(games.stats.GamesStats):
  _lock = threading.RLock()
  _stats = None

  @staticmethod
  def items(key = None, reverse = False, window = None):
    with GamesStats._lock:
      if GamesStats._stats == None:
        GamesStats.refresh_stats()

      items = sorted(GamesStats._stats, key = key, reverse = reverse)
      return (items[window[0]:window[0] + window[1]], len(GamesStats._stats))

  @staticmethod
  def refresh_stats():
    GamesStats._stats = []

    with GamesStats._lock:
      new_stats = {}

      for g in hruntime.dbroot.games.itervalues():
        if hruntime.time - (86400 * 7 * 52) > g.last_pass:
          continue

        for p in g.players.itervalues():
          if p.user.name not in new_stats:
            s = Stats(p.user, 0, 0, 0, 0, 0.0)
            new_stats[p.user.name] = s

          else:
            s = new_stats[p.user.name]

          s.points += p.points
          s.games += 1

          if g.winner_player == p:
            s.wons += 1

      GamesStats._stats = new_stats.values()

      for s in GamesStats._stats:
        s.points_per_game = float(s.points) / float(s.games)

      for v in GamesStats._stats:
        print str(v)

#    for s in hruntime.dbroot.stats.settlers.itervalues():
#      if s.games < 20:
#        to_delete.append(s)
#
#      s.points_per_game = float(s.points) / float(s.games)
#
#    for s in to_delete:
#      del hruntime.dbroot.stats.settlers[s.user]

from hlib.ui.table import Table, TableHeader

STATS_TABLE = Table(
  ('name',            TableHeader(type = 'html', key = lambda x: x.user.name, label = 'Name')),
  ('total_games',     TableHeader(type = 'numeric', key = lambda x: x.games, label = 'Total games')),
  ('won_games',       TableHeader(type = 'numeric', key = lambda x: x.wons, label = 'Won games')),
  ('total_points',    TableHeader(type = 'numeric', key = lambda x: x.points, label = 'Total points')),
  ('points_per_game', TableHeader(type = 'numeric', key = lambda x: x.points_per_game, label = 'Points per game'))
)
