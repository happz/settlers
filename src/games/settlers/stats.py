import threading

import lib.datalayer
import games.stats

import hlib.api
import hlib.database
import hlib.log
import hlib.pageable

# pylint: disable-msg=F0401
import hruntime

WINDOW				= 86400 * 7 * 52

_stats_lock = threading.RLock()
_stats = None

class UserStats(object):
  def __init__(self, user):
    # pylint: disable-msg=E1002
    super(UserStats, self).__init__()

    self.user				= user
    self.points				= 0
    self.games				= 0
    self.finished			= 0
    self.wons				= 0
    self.points_per_game		= 0.0
    self.forhont			= 0

  def __str__(self):
    return '%s: %i, %i, %f' % (self.user.name.encode('ascii', 'replace'), self.points, self.games, self.points_per_game)

  def to_api(self):
    return {
      'user':                   hlib.api.User(self.user),
      'points':                 self.points,
      'games':                  self.games,
      'finished':               self.finished,
      'wons':                   self.wons,
      'ppg':                    self.points_per_game,
      'forhont':		self.forhont
    }

class Stats(games.stats.Stats):
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
        if hruntime.time - WINDOW > g.last_pass:
          continue

        for p in g.players.values():
          if p.user not in new_stats:
            s = UserStats(p.user)
            new_stats[p.user] = s

          else:
            s = new_stats[p.user]

          s.points += p.points
          s.games += 1

          if g.is_finished:
            if g.winner_player == p:
              s.wons += 1

          elif g.is_canceled or g.is_suspended:
            pass

          else:
            if p.id == g.forhont:
              s.forhont += 1

      self.stats = new_stats.values()

      for s in self.stats:
        s.points_per_game = float(s.points) / float(s.games)

      for s in self.stats:
        print str(s)

#    for s in hruntime.dbroot.stats.settlers.values():
#      if s.games < 20:
#        to_delete.append(s)
#
#      s.points_per_game = float(s.points) / float(s.games)
#
#    for s in to_delete:
#      del hruntime.dbroot.stats.settlers[s.user]

stats = Stats()
