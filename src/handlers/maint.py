import time
import handlers
import games
import games.settlers.stats
import hlib
import hlib.log
import hlib.error
import hlib.event
import events.game
import tournament

import hlib.event

import lib.play

# Handlers
from handlers import page, require_write
from hlib.api import api

from hlib.input import validate_by

# pylint: disable-msg=F0401
import hruntime

class Handler(handlers.GenericHandler):
  @require_write
  @api
  def process_archive_deadlines(self):
    def __process_list(playable_list, playable_archived_list, event_name, handle_name):
      archived = []

      for p in playable_list.values():
        try:
          if p.archive_deadline >= hruntime.time:
            continue
        except lib.play.CannotBeArchivedError, e:
          continue

        archived.append(p)

      for p in archived:
        del playable_list[p.id]

        playable_archived_list[p.id] = p

        kwargs = {handle_name: p}
        hlib.event.trigger(event_name, p, **kwargs)

      return [p.id for p in archived]

    return hlib.api.Reply(200, archived_games = __process_list(hruntime.dbroot.games, hruntime.dbroot.games_archived, 'game.GameArchived', 'game'),
                               archived_tournaments = __process_list(hruntime.dbroot.tournaments, hruntime.dbroot.tournaments_archived, 'tournament.Archived', 'tournament'))

  @require_write
  @validate_by(schema = games.GenericValidateKind)
  @api
  def refresh_stats_games(self, kind = None):
    gm = games.game_module(kind, submodule = 'stats')
    gm.stats.refresh_stats()

  @require_write
  @api
  def create_system_games(self):
    def __create_games(count, limit):
      for i in range(0, count):
        g = games.create_system_game('settlers', limit = limit, turn_limit = 604800)
        time.sleep(5)
        hruntime.time = None

    cnt = hruntime.dbroot.counters.games_free()
    if cnt <= hruntime.app.config['system_games.limit']:
      __create_games(hruntime.app.config['system_games.limit'] - cnt, hruntime.app.config['system_games.sleep'])
      games._game_lists.inval_all('active')

    return hlib.api.Reply(200, created_games = (hruntime.app.config['system_games.limit'] - cnt))
