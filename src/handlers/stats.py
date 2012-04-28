import hlib.i18n

import games
import handlers
import lib.datalayer
import lib.lister

from handlers import page, require_login
from hlib.api import api, ApiJSON, ApiRaw, ApiReply

# pylint: disable-msg=F0401
import hruntime

class GlobalStats(ApiJSON):
  def __init__(self):
    super(GlobalStats, self).__init__(['total_games', 'free_games', 'finished_games'])

class StatsHandler(handlers.GenericHandler):
  @require_login
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'stats', self.generate, 'stats.mako')

  @require_login
  @api
  def lister(self, **kwargs):
    stats_module = games.settlers.stats
    stats_table = getattr(stats_module, 'STATS_TABLE')

    reply = lib.lister.ApiLister()

    headers_offset = 1

    if 'sSortDir_0' not in kwargs:
      kwargs['sSortDir_0'] = 'desc'

    if 'iSortCol_0' not in kwargs or kwargs['iSortCol_0'] == '0':
      kwargs['iSortCol_0'] = stats_table.headers.keys().index('points_per_game') + headers_offset
      kwargs['sSortDir_0'] = 'desc'

    sort_by_field_name = stats_table.headers.keys()[int(kwargs['iSortCol_0']) - headers_offset]
    sort_by_field = stats_table.headers[sort_by_field_name]
    window = (int(kwargs.get('iDisplayStart', 0)), int(kwargs.get('iDisplayLength', 10)))

    rs, rs_cnt = getattr(stats_module, 'GamesStats').items(key = sort_by_field.key, reverse = (kwargs['sSortDir_0'] == 'desc'), window = window)

    reply.cnt_display = rs_cnt
    reply.cnt_total   = rs_cnt

    for r in rs:
      reply.records.append(['', unicode(r.user.name), int(r.games), int(r.wons), int(r.points), float(r.points_per_game)])

    return ApiRaw(reply)
