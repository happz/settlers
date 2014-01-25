import games
import handlers

import hlib.api
import hlib.pageable

from handlers import page, require_login
from hlib.api import api
from hlib.stats import stats as STATS

from hlib.input import validate_by

import hruntime

class StatsHandler(handlers.GenericHandler):
  def __init__(self, *args, **kwargs):
    super(StatsHandler, self).__init__(*args, **kwargs)

    STATS.set('Playables - Games', {
      'Active': lambda x: hruntime.dbroot.counters.games_active(),
      'Free': lambda x: hruntime.dbroot.counters.games_free(),
      'Inactive': lambda x: hruntime.dbroot.counters.games_inactive(),
      'Archived': lambda x: hruntime.dbroot.counters.games_archived(),
      'Total': lambda x: hruntime.dbroot.counters.games()
    })

    STATS.set('Playables - Tournaments', {
      'Active': lambda x: hruntime.dbroot.counters.tournaments_active(),
      'Free': lambda x: hruntime.dbroot.counters.tournaments_free(),
      'Inactive': lambda x: hruntime.dbroot.counters.tournaments_inactive(),
      'Archived': lambda x: hruntime.dbroot.counters.tournaments_archived(),
      'Total': lambda x: hruntime.dbroot.counters.tournaments()
    })

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
