import threading

import hlib.pageable

import lib.datalayer

import hruntime

class Stats(hlib.pageable.Pageable):
  def __init__(self, *args, **kwargs):
    super(Stats, self).__init__(*args, **kwargs)

    self.lock		= threading.RLock()
    self.stats		= None
    self.last_update		= None

  def refresh_stats(self):
    with self.lock:
      self.last_update = hruntime.time
      hruntime.cache.remove(lib.datalayer.SystemUser(), 'stats')
