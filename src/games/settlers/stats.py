import threading

import lib.datalayer
import games.stats

import hlib.api
import hlib.database
import hlib.log
import hlib.pageable

# pylint: disable-msg=F0401
import hruntime

class UserStats(object):
  def __init__(self, user):
    # pylint: disable-msg=E1002
    super(UserStats, self).__init__()

    self.user				= user
    self.points				= 0
    self.finished_points		= 0
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
      'points':                 self.finished_points,
      'games':                  self.games,
      'finished':               self.finished,
      'wons':                   self.wons,
      'ppg':                    self.points_per_game,
      'forhont':		self.forhont
    }

class Stats(games.stats.Stats):
  def get_records(self, start, length):
    records = self.records

    return (records[start:max(start + length, len(records) - 1)], len(records))

  def refresh_stats(self):
    new_stats = {}

    def __process_game(g):
      for p in g.players.values():
        if p.user not in new_stats:
          s = UserStats(p.user)
          new_stats[p.user] = s

        else:
          s = new_stats[p.user]

        s.points += p.points
        s.games += 1

        if g.is_finished:
          s.finished += 1
          s.finished_points += p.points

          if g.winner_player == p:
            s.wons += 1

        elif g.is_canceled or g.is_suspended:
          pass

        else:
          if p.id == g.forhont:
            s.forhont += 1

    for g in hruntime.dbroot.games.values():
      if hruntime.time - int(hruntime.app.config['stats.games.window']) > g.last_pass:
        continue

      __process_game(g)

    for g in hruntime.dbroot.games_archived.values():
      if hruntime.time - int(hruntime.app.config['stats.games.window']) > g.last_pass:
        continue

      __process_game(g)

    keys_to_remove = []

    for user, stats in new_stats.items():
      if stats.finished < 20:
        keys_to_remove.append(user)

      if stats.finished > 0:
        stats.points_per_game = float(stats.finished_points) / float(stats.finished)

    for user in keys_to_remove:
      del new_stats[user]

    with self.lock:
      self._player_stats = new_stats
      self._records = sorted(new_stats.values(), key = lambda x: x.points_per_game, reverse = True)

      super(Stats, self).refresh_stats()

stats = Stats()
