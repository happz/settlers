import hlib.api

import games.stats

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class PlayerStats(games.stats.PlayerStats):
  def __init__(self, user, **kwargs):
    # pylint: disable-msg=E1002
    super(PlayerStats, self).__init__(user, **kwargs)

    self.points				= 0
    self.finished_points		= 0
    self.games				= 0
    self.finished			= 0
    self.wons				= 0
    self.points_per_game		= 0.0
    self.forhont			= 0

  def to_api(self):
    return {
      'user':                   hlib.api.User(hruntime.dbroot.users[self.username]),
      'points':                 self.finished_points,
      'games':                  self.games,
      'finished':               self.finished,
      'wons':                   self.wons,
      'ppg':                    self.points_per_game,
      'forhont':		self.forhont
    }

class PlayerStatsWrapper(games.stats.PlayerStatsWrapper):
  def default(self, key):
    return PlayerStats(hruntime.dbroot.users[key], default = True)

class Stats(games.stats.Stats):
  def get_records(self, start, length):
    records = self.records

    return (records[start:start + max(length, len(records))], len(records), None)

  def refresh_stats(self):
    new_stats = PlayerStatsWrapper()

    def __process_game(g):
      for p in g.players.values():
        try:
          if p.user.name not in new_stats:
            s = PlayerStats(p.user)
            new_stats[p.user.name] = s

          else:
            s = new_stats[p.user.name]
        except AttributeError:
          continue

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

      if g.is_canceled:
        continue

      __process_game(g)

    for g in hruntime.dbroot.games_archived.values():
      if hruntime.time - int(hruntime.app.config['stats.games.window']) > g.last_pass:
        continue

      if g.is_canceled:
        continue

      __process_game(g)

    keys_to_remove = []

    for username, stats in new_stats.items():
      if stats.finished < 20:
        keys_to_remove.append(username)

      if stats.finished > 0:
        stats.points_per_game = float(stats.finished_points) / float(stats.finished)

    for username in keys_to_remove:
      del new_stats[username]

    with self.lock:
      self._player_stats = new_stats
      self._records = sorted(new_stats.values(), key = lambda x: x.points_per_game, reverse = True)

      super(Stats, self).refresh_stats()

stats = Stats()
