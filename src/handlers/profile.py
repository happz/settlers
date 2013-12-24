import games
import handlers

import hlib.error
import hlib.input

from handlers import require_login, page

import hruntime  # @UnresolvedImport

class Handler(handlers.GenericHandler):
  class ValidateProfile(hlib.input.SchemaValidator):
    username = hlib.input.Username()

  @require_login
  @page
  @hlib.input.validate_by(schema = ValidateProfile)
  def index(self, username = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.NoSuchUserError(username)

    user = hruntime.dbroot.users[username]
    gm = games.game_module('settlers', submodule = 'stats')

    return self.generate('profile.mako', params = {'player': user, 'player_stats': gm.stats.player_stats[user.name]})
