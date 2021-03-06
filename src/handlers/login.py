import handlers

import hlib.auth
import hlib.events
import hlib.error
import hlib.http

import lib

# Shortcuts
from handlers import page
from hlib.api import api
from hlib.input import validate_by

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class LoginHandler(handlers.GenericHandler):
  #
  # Index
  #
  @page
  def index(self):
    try:
      hlib.auth.check_session()

    except hlib.http.Redirect, e:
      if e.location != '/login/':
        raise e

    else:
      raise hlib.http.Redirect('/home/')

    return self.generate('login.mako')

  class ValidateCheck(hlib.input.SchemaValidator):
    username = hlib.input.Username()

  @api
  @validate_by(schema = ValidateCheck)
  def check(self, username = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.NoSuchUserError(username = username)

  #
  # Login
  #
  class ValidateLogin(hlib.input.SchemaValidator):
    username = hlib.input.Username()
    password = hlib.input.Password()

  @api
  @validate_by(schema = ValidateLogin)
  def login(self, username = None, password = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.InvalidAuthError(msg = 'Invalid username or password')

    u = hruntime.dbroot.users[username]

    if u.password != lib.pwcrypt(password):
      raise hlib.error.InvalidAuthError(msg = 'Invalid username or password')

    if hruntime.dbroot.server.maintenance_mode == True and u.maintenance_access != True:
      if 'Referer' in hruntime.request.headers and hruntime.request.headers['Referer'].endswith('/login/'):
        raise hlib.http.Redirect('/maintenance/')

      raise hlib.error.AccessDeniedError(msg = 'Sorry, you are not allowed to log in')

    hlib.auth.start_session(user = u)

    hlib.events.trigger('system.UserLoggedIn', hruntime.dbroot.server, user = u)

    if u.is_on_vacation:
      raise hlib.http.Redirect('/vacation/')

    raise hlib.http.Redirect('/home/')

class LoginAsHandler(handlers.GenericHandler):
  #
  # index
  #
  @page
  def index(self):
    return self.generate('loginas.mako')

  #
  # Login
  #
  class ValidateLoginAs(hlib.input.SchemaValidator):
    username = hlib.input.Username()
    password = hlib.input.Password()
    loginas  = hlib.input.Username()

  @validate_by(schema = ValidateLoginAs)
  @api
  def loginas(self, username = None, password = None, loginas = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.InvalidAuthError(msg = 'Invalid username or password')

    u = hruntime.dbroot.users[username]

    if not u.is_admin and not u.is_autoplayer:
      raise hlib.error.AccessDeniedError(msg = 'You are not admin')

    if loginas not in hruntime.dbroot.users:
      raise hlib.error.NoSuchUserError(loginas)

    if u.password != lib.pwcrypt(password):
      raise hlib.error.InvalidAuthError(msg = 'Invalid username or password')

    a = hruntime.dbroot.users[loginas]

    hlib.auth.start_session(user = a, tainted = u)

    raise hlib.http.Redirect('/home/')
