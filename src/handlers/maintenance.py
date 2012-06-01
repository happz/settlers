import handlers

import hlib.api
import hlib.input

# Shortcuts
from handlers import page, require_login, require_admin, require_write
from hlib.api import api
from hlib.input import validate_by, validator_factory

# pylint: disable-msg=F0401
import hruntime

class State(hlib.api.ApiJSON):
  def __init__(self):
    super(State, self).__init__(['enabled'])

    self.enabled		= hruntime.dbroot.server.maintenance_mode == True

class ApiGrantedFull(hlib.api.ApiJSON):
  def __init__(self, users):
    super(ApiGrantedFull, self).__init__(['users'])

    self.users = [hlib.api.User(user) for user in users]

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

    return hlib.api.ApiReply(200, updated_fields = {'mode': 1 if hruntime.dbroot.server.maintenance_mode == True else 0})

  class ValidateGranted(hlib.input.SchemaValidator):
    term = hlib.input.CommonString()

  @handlers.require_admin
  @handlers.require_login
  @hlib.input.validate_by(schema = ValidateGranted)
  @handlers.page
  def granted(self, term = None, full = False):
    return '\n'.join([k for k in hruntime.dbroot.users.iterkeys() if term in k])

  @handlers.require_admin
  @handlers.require_login
  @hlib.api.api
  def granted_full(self, term = None, full = False):
    return ApiGrantedFull([u for u in hruntime.dbroot.users.itervalues() if u.maintenance_access == True])

  class ValidateGrant(hlib.input.SchemaValidator):
    username = hlib.input.Username()

  @handlers.require_write
  @handlers.require_admin
  @handlers.require_login
  @hlib.input.validate_by(schema = ValidateGrant)
  @hlib.api.api
  def grant(self, username = None):
    if username not in hruntime.dbroot.users:
      return hlib.api.ApiReply(401, message = 'No such user')

    u = hruntime.dbroot.users[username]
    u.maintenance_access = True

  @handlers.require_write
  @handlers.require_admin
  @handlers.require_login
  @hlib.input.validate_by(schema = ValidateGrant)
  @hlib.api.api
  def revoke(self, username = None):
    if username not in hruntime.dbroot.users:
      return hlib.api.ApiReply(401, message = 'No such user')

    u = hruntime.dbroot.users[username]
    u.maintenance_access = False

