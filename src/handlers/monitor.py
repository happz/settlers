import handlers

import hlib.api
from hlib.stats import stats as STATS

from handlers import page, require_login
from hlib.api import api

class Handler(handlers.GenericHandler):
  @require_login
  @page
  def index(self):
    with STATS:
      snapshot = STATS.snapshot()

    return self.generate('monitor.mako', params = {'stats': snapshot})

  @api
  def snapshot_stats(self):
    with STATS:
      snapshot = STATS.snapshot()

    return hlib.api.Reply(200, snapshot = snapshot)
