import games
import handlers

import hlib.api
import hlib.pageable

from handlers import page, require_login
from hlib.api import api

from hlib.input import validate_by

class StatsHandler(handlers.GenericHandler):
  #
  # Index
  #
  @require_login
  @page
  def index(self):
    return self.generate('stats.mako')

  #
  # Page
  #
  @require_login
  @validate_by(schema = hlib.pageable.ValidatePage)
  @api
  def page(self, start = None, length = None):
    gm = games.game_module('settlers', submodule = 'stats')

    return hlib.api.Reply(200, page = getattr(gm, 'stats').get_page(start = start, length = length))
