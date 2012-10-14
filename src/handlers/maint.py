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

# Handlers
from handlers import page
from hlib.api import api

# pylint: disable-msg=F0401
import hruntime

def process_games_begin(gs):
  for game in gs:
    if game.deadline > hruntime.time:
      continue

    game.cancel(reason = events.game.GameCanceled.REASON_EMPTY, user = None)

def process_games_turn(gs):
  for game in gs:
    if hruntime.time <= game.deadline:
      continue

    player = game.forhont_player

    if game.last_pass <= player.user.atime and player.user.atime <= game.deadline:
      player.turns_missed = player.turns_missed + 1
      hlib.event.trigger('game.PlayerMissed', game, game = game, user = player.user, logged = True)

    else:
      player.turns_missed_notlogged = player.turns_missed_notlogged + 1
      hlib.event.trigger('game.PlayerMissed', game, game = game, user = player.user, logged = False)

    if player.has_too_many_misses(logged=False):
      game.cancel(reason = events.game.GameCanceled.REASON_ABSENTEE, user = player.user)

    else:
      if game.has_next_player == True:
        hruntime.session.name = player.user.name
        game.type = games.Game.TYPE_GAME
        game.pass_turn(check = False, record = False, forced = True)

      else:
        game.cancel(reason = events.game.GameCanceled.REASON_MASSIVE, user = None)

class MaintHandler(handlers.GenericHandler):
  @api
  def process_timeouts(self):
    process_games_begin([g for g in hruntime.dbroot.games if g.is_free and g.is_waiting_begin])
    process_games_turn([g for g in games.f_active if g.is_waiting_begin])

    raise hlib.error.DieError()

  @api
  def process_deads(self):
    for u in hruntime.server.dead_accounts:
      u.delete_from_db()

    raise hlib.error.DieError()

  @api
  def refresh_stats(self):
    # pylint: disable-msg=R0201
    games.settlers.stats.GamesStats.refresh_stats()

  @api
  def create_system_games(self):
    def __create_games(count, limit):
      # pylint: disable-msg=W0612
      for i in range(0, count):
        games.create_system_game('settlers', limit = limit, turn_limit = 604800)
        time.sleep(5)
        hruntime.time = None

    cnt = hruntime.server.free_system_games_count
    if cnt <= 20:
      __create_games(20 - cnt, 3)

  @api
  def process_tournaments(self):
    for t in hruntime.dbroot.tournaments.values():
      if t.stage != tournament.Tournament.STAGE_RUNNING:
        continue

      if t.has_closed_all_games != True:
        continue

      t.next_round()

    raise hlib.error.DieError()
