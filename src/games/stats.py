import UserDict
import threading

import hlib.pageable

import lib.datalayer

# pylint: disable-msg=F0401
import hruntime

class PlayerStatsWrapper(UserDict.UserDict):
  def default(self, key):
    return None

  def __getitem__(self, key):
    if key not in self.data:
      return self.default(key)

    return UserDict.UserDict.__getitem__(self, key)

class Stats(hlib.pageable.Pageable):
  def __init__(self, *args, **kwargs):
    super(Stats, self).__init__(*args, **kwargs)

    self.lock		= threading.RLock()

    self._stats		= None
    self._player_stats	= None

    self.last_update	= None

  def __getattr__(self, name):
    if name == 'records' or name == 'player_stats':
      with self.lock:
        if not self._stats:
          self.refresh_stats()

        if name == 'records':
          return self._records

        if name == 'player_stats':
          return self._player_stats

    return super(Stats, self).__getattr__(name)

  def refresh_stats(self):
    with self.lock:
      self.last_update = hruntime.time
      hruntime.cache.remove_for_all_users('stats')
