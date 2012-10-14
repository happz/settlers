import handlers

import hlib.stats

from handlers import page, require_login

class Handler(handlers.GenericHandler):
  @require_login
  @page
  def index(self):
    return self.generate('monitor.mako', params = {'stats': hlib.stats.snapshot(hlib.stats.stats)})
