import threading

import hlib.pageable

import lib.datalayer

# pylint: disable-msg=F0401
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
      hruntime.cache.remove_for_all_users('stats')
