import handlers

import hlib.api
import hlib.stats

import hruntime

from handlers import page, require_login
from hlib.api import api

class Handler(handlers.GenericHandler):
  @require_login
  @page
  def index(self):
    return self.generate('monitor.mako', params = {'stats': hlib.stats.snapshot(hlib.stats.stats)})

  @api
  def snapshot_stats(self):
    return hlib.api.Reply(200, snapshot = hlib.stats.snapshot(hlib.stats.stats))
