import UserDict
import threading

import hlib.locks
import hlib.pageable

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class PlayerStats(object):
  def __init__(self, user, default = False):
    super(PlayerStats, self).__init__()

    self.username = user.name
    self.default = default

  def to_api(self):
    return {}

class PlayerStatsWrapper(UserDict.UserDict):
  def default(self, key):
    return None

  def __contains__(self, key):
    return key in self.data

  def __getitem__(self, key):
    if key not in self.data:
      return self.default(key)

    return UserDict.UserDict.__getitem__(self, key)

class Stats(hlib.pageable.Pageable):
  def __init__(self, *args, **kwargs):
    super(Stats, self).__init__(*args, **kwargs)

    self.lock		= hlib.locks.RLock(name = 'Game stats')

    self._records = []
    self._player_stats = []

    self.last_update	= None

  def __getattr__(self, name):
    if name == 'records' or name == 'player_stats':
      with self.lock:
        if name == 'records':
          return self._records

        if name == 'player_stats':
          return self._player_stats

    return super(Stats, self).__getattr__(name)

  def refresh_stats(self):
    with self.lock:
      self.last_update = hruntime.time
      hruntime.cache.remove_for_all_users('stats')
