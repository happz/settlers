import time
import handlers
import events.game

import hlib.events
import hlib.server

import games
import games.settlers.stats
import lib.play

# Handlers
from handlers import require_write, require_hosts
from hlib.api import api

from hlib.input import validate_by

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

maint_require_hosts = lambda: hruntime.app.config['hosts']['maint.*']

class StatsRefreshThread(hlib.server.Producer):
  def __init__(self, pool, name, kind, *args, **kwargs):
    hlib.server.Producer.__init__(self, pool, name, *args, **kwargs)

    self.kind = kind

  def produce(self):
    gm = games.game_module(self.kind, submodule = 'stats')
    gm.stats.refresh_stats()

class ArchiveDeadlinesThread(hlib.server.Producer):
  def produce(self):
    hruntime.dont_commit = False

    def __process_list(playable_list, playable_archived_list, event_name, handle_name):
      archived = []

      for playable in playable_list.values():
        if playable.can_be_archived != True:
          continue

        archived.append((playable, playable.atime, hruntime.time - playable.archive_deadline, hruntime.time - playable.archive_deadline_hard))

      ret = []

      for playable, atime, ddiff, dhdiff in archived:
        del playable_list[playable.id]

        playable_archived_list[playable.id] = playable

        # pylint: disable-msg=W0142
        hlib.events.trigger(event_name, playable, **{handle_name: playable})

        ret.append((playable.id, atime, ddiff, dhdiff))

      return ret

    return [
      __process_list(hruntime.dbroot.games, hruntime.dbroot.games_archived, 'game.GameArchived', 'game'),
      __process_list(hruntime.dbroot.tournaments, hruntime.dbroot.tournaments_archived, 'tournament.Archived', 'tournament')
    ]

class FreeDeadlinesThread(hlib.server.Producer):
  def produce(self):
    hruntime.dont_commit = False

    canceled = []

    for g in hruntime.dbroot.games.values():
      if not g.is_waiting_begin or g.deadline > hruntime.time:
        continue

      t = (g.id, g.type, hruntime.time - g.deadline, [p.user.name for p in g.players.values()], g.forhont_player.user.name)
      g.cancel(reason = events.game.GameCanceled.REASON_EMPTY, user = None)
      canceled.append(t)

    return canceled

class ActiveDeadlinesThread(hlib.server.Producer):
  def produce(self):
    canceled = []

    for g in hruntime.dbroot.games.values():
      if not g.is_waiting_turn or g.deadline > hruntime.time:
        continue

      t = (g.id, g.type, hruntime.time - g.deadline, [p.user.name for p in g.players.values()], g.forhont_player.user.name)
      g.cancel(reason = events.game.GameCanceled.REASON_ABSENTEE, user = g.forhont_player.user)
      canceled.append(t)

    hruntime.dont_commit = True
    return canceled

class SystemGamesThread(hlib.server.Producer):
  def produce(self):
    hruntime.dont_commit = False

    def __create_games(count, limit, sleep = 5):
      for _ in range(0, count):
        games.create_system_game('settlers', limit = limit, turn_limit = 604800)
        time.sleep(sleep)
        hruntime.time = None

    cnt = hruntime.app.config['system_games.limit'] - hruntime.dbroot.counters.games_free() / 2
    if cnt > 0:
      __create_games(cnt, 3, sleep = hruntime.app.config['system_games.sleep'])

      # pylint: disable-msg=W0212
      games._game_lists.inval_all('active')

    else:
      cnt = 0

    return cnt

class Handler(handlers.GenericHandler):
  def __run_thread(self, thread_class, thread_name, *args, **kwargs):
    t = thread_class(hruntime.service_thread.pool, thread_name, *args, **kwargs)
    t.start()
    t.join()

    if t.failed:
      raise t.error

    return t.result

  @require_hosts(get_hosts = maint_require_hosts)
  @api
  def process_free_deadlines(self):
    return hlib.api.Reply(200, canceled_games = self.__run_thread(FreeDeadlinesThread, 'Free deadlines'))

  @require_hosts(get_hosts = maint_require_hosts)
  @api
  def process_active_deadlines(self):
    return hlib.api.Reply(200, canceled_games = self.__run_thread(ActiveDeadlinesThread, 'Active deadlines'))

  @require_hosts(get_hosts = maint_require_hosts)
  @api
  def process_archive_deadlines(self):
    result = self.__run_thread(ArchiveDeadlinesThread, 'Archive deadlines')

    return hlib.api.Reply(200, archived_games = result[0], archived_tournaments = result[1])

  @require_hosts(get_hosts = maint_require_hosts)
  @validate_by(schema = games.GenericValidateKind)
  @api
  def refresh_stats_games(self, kind = None):
    return hlib.api.Reply(200, stats_refreshed = self.__run_thread(StatsRefreshThread, 'Stats refreshing: %s' % kind, kind))

  @require_hosts(get_hosts = maint_require_hosts)
  @api
  def create_system_games(self):
    return hlib.api.Reply(200, created_games = self.__run_thread(SystemGamesThread, 'System games'))
