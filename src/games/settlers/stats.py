import threading

import lib.datalayer
import games.stats

import hlib.api
import hlib.database
import hlib.log
import hlib.pageable

# pylint: disable-msg=F0401
import hruntime

_stats_lock = threading.RLock()
_stats = None

class UserStats(object):
  def __init__(self, user, points, gs, finished, wons, points_per_game):
    # pylint: disable-msg=E1002
    super(UserStats, self).__init__()

    self.user			= user
    self.points			= points
    self.games			= gs
    self.finished		= finished
    self.wons			= wons
    self.points_per_game	= points_per_game

  def __str__(self):
    return '%s: %i, %i, %f' % (self.user.name.encode('ascii', 'replace'), self.points, self.games, self.points_per_game)

class Stats(games.stats.Stats):
  def record_to_api(self, record):
    return {
      'user':			hlib.api.User(record.user),
      'points':			record.points,
      'games':			record.games,
      'finished':		record.finished,
      'wons':			record.wons,
      'ppg':			record.points_per_game
    }

  def get_records(self, start, length):
    records = []

    with self.lock:
      if self.stats == None:
        self.refresh_stats()

      records = self.stats[start:max(start + length, len(self.stats) - 1)]

      return (records, len(self.stats))

  def refresh_stats(self):
    with self.lock:
      new_stats = {}

      for g in hruntime.dbroot.games.values():
        if hruntime.time - (86400 * 7 * 52) > g.last_pass:
          continue

        for p in g.players.values():
          if p.user.name not in new_stats:
            s = UserStats(p.user, 0, 0, 0, 0, 0.0)
            new_stats[p.user.name] = s

          else:
            s = new_stats[p.user.name]

          s.points += p.points
          s.games += 1

          if g.winner_player == p:
            s.wons += 1

      self.stats = new_stats.values()

      for s in self.stats:
        s.points_per_game = float(s.points) / float(s.games)

      for v in self.stats:
        print str(v)

#    for s in hruntime.dbroot.stats.settlers.values():
#      if s.games < 20:
#        to_delete.append(s)
#
#      s.points_per_game = float(s.points) / float(s.games)
#
#    for s in to_delete:
#      del hruntime.dbroot.stats.settlers[s.user]

stats = Stats()
