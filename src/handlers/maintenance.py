import handlers

import hlib.api
import hlib.error
import hlib.event
import hlib.input

# Shortcuts
from handlers import page, require_login, require_admin, require_write
from hlib.api import api
from hlib.input import validate_by, validator_factory

# pylint: disable-msg=F0401
import hruntime

class State(hlib.api.ApiJSON):
  def __init__(self):
    super(State, self).__init__(['status', 'enabled'])

    self.status			= 200
    self.enabled		= hruntime.dbroot.server.maintenance_mode == True

class Handler(handlers.GenericHandler):
  #
  # Index
  #
  @page
  def index(self):
    return self.generate('maintenance.mako')

  #
  # State
  #
  @api
  def state(self):
    return State()

  #
  # Mode
  #
  class ValidateMode(hlib.input.SchemaValidator):
    mode = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([0, 1]))

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateMode)
  @hlib.api.api
  def mode(self, mode = None):
    hruntime.dbroot.server.maintenance_mode = (mode == 1)

    return hlib.api.Reply(200, updated_fields = {'mode': 1 if hruntime.dbroot.server.maintenance_mode == True else 0})

  class ValidateGranted(hlib.input.SchemaValidator):
    term = hlib.input.CommonString()

  @require_admin
  @require_login
  @validate_by(schema = ValidateGranted)
  @page
  def granted(self, term = None, full = False):
    return '\n'.join([k for k in hruntime.dbroot.users.keys() if term in k])

  @require_admin
  @require_login
  @api
  def granted_full(self, term = None, full = False):
    return hlib.api.Reply(200, users = [hlib.api.User(user) for user in hruntime.dbroot.users.values() if user.maintenance_access == True])

  class ValidateGrant(hlib.input.SchemaValidator):
    username = hlib.input.Username()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateGrant)
  @api
  def grant(self, username = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.NoSuchUserError(username)

    u = hruntime.dbroot.users[username]
    u.maintenance_access = True

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateGrant)
  @api
  def revoke(self, username = None):
    if username not in hruntime.dbroot.users:
      return hlib.api.Reply(401, message = 'No such user')

    u = hruntime.dbroot.users[username]
    u.maintenance_access = False

  #
  #
  #
  @require_write
  @api
  def process_active_games(self):
    for g in hruntime.dbroot.games.values():
      if not g.can_be_archived:
        continue

      del hruntime.dbroot.games[g.id]

      hruntime.dbroot.games_archived[g.id] = g
      hlib.event.trigger('game.GameArchived', g, game = g)
