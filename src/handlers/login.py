import hlib.auth
import hlib.event
import hlib.log

import handlers
import lib.datalayer

from handlers import page
from hlib.api import api, ApiReply
from hlib.input import validate_by, SchemaValidator, Username, Password

# pylint: disable-msg=F0401
import hruntime

class LoginHandler(handlers.GenericHandler):
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'login', self.generate, 'login.mako')

  class ValidateLogin(SchemaValidator):
    username = Username()
    password = Password()

  @api
  @validate_by(schema = ValidateLogin)
  def login(self, username = None, password = None):
    if username not in hruntime.dbroot.users:
      return ApiReply(401, message = 'No such user')

    u = hruntime.dbroot.users[username]

    if u.password != lib.pwcrypt(password):
      return ApiReply(401, message = 'Password or username are wrong')

    hlib.auth.start_session(user = u)

    hlib.event.trigger('system.UserLoggedIn', hruntime.dbroot.server, user = u)

    if u.is_on_vacation:
      return ApiReply(403)

class LoginAsHandler(handlers.GenericHandler):
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'loginas', self.generate, 'loginas.mako')

  class ValidateLoginAs(SchemaValidator):
    username = Username()
    password = Password()
    loginas  = Username()

  @validate_by(schema = ValidateLoginAs)
  @api
  def loginas(self, username = None, password = None, loginas = None):
    if username not in hruntime.dbroot.users:
      return ApiReply(401, message = 'No such user')

    u = hruntime.dbroot.users[username]

    if not u.is_admin and not u.is_autoplayer:
      return ApiReply(401, message = 'You are not admin')

    if loginas not in hruntime.dbroot.users:
      return ApiReply(401, message = 'No such user')

    if u.password != lib.pwcrypt(password):
      return ApiReply(401, message = 'Password or username are wrong')

    a = hruntime.dbroot.users[loginas]

    hlib.auth.start_session(user = a, tainted = u)
