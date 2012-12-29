import threading

import hlib.pageable

class Stats(hlib.pageable.Pageable):
  def __init__(self, *args, **kwargs):
    super(Stats, self).__init__(*args, **kwargs)

    self.lock		= threading.RLock()
    self.stats		= None
    self.last_update		= None
