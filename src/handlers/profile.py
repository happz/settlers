import games
import handlers

import hlib.error
import hlib.input

from handlers import require_login, page

import hruntime

class Handler(handlers.GenericHandler):
  class ValidateProfile(hlib.input.SchemaValidator):
    username = hlib.input.Username()

  @require_login
  @page
  @hlib.input.validate_by(schema = ValidateProfile)
  def index(self, username = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.NoSuchUserError(username)

    gm = games.game_module('settlers', submodule = 'stats')

    return self.generate('profile.mako', params = {'player': hruntime.dbroot.users[username], 'player_stats': gm.stats.player_stats[hruntime.user]})

