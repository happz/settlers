import random

import handlers
import lib
import lib.datalayer

import hlib.api
import hlib.error
import hlib.input
import hlib.mail

# Shortcuts
from hlib.api import api
from handlers import page, require_write
from hlib.input import validate_by

# pylint: disable-msg=F0401
import hruntime

class RecoveryHandler(handlers.GenericHandler):
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'password_recovery', self.generate, 'password_recovery.mako')

  class ValidatePasswordRecovery(hlib.input.SchemaValidator):
    username = hlib.input.Username()
    email = hlib.input.Email()

  @require_write
  @validate_by(schema = ValidatePasswordRecovery)
  @api
  def recover(self, username = None, email = None):
    if username not in hruntime.dbroot.users:
      return ApyReply(401)

    u = hruntime.dbroot.users[username]

    if email != u.email:
      return ApyReply(401, message = 'E-mail address is wrong')

    new_password = ''

    # pylint: disable-msg=W0612
    for i in range(0, 10):
      new_password = new_password + str(random.randint(0, 9))

    u.password = lib.pwcrypt(new_password)

    hlib.mail.send_email('osadnici@happz.cz', email, hruntime.root.admin.trumpet.password_recovery_mail.subject, hruntime.root.admin.trumpet.password_recovery_mail.text % (u.name, new_password), SMTPserver = 'localhost')

class Handler(handlers.GenericHandler):
  recovery = RecoveryHandler()

  #
  # Index
  #
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'registration', self.generate, 'registration.mako')

  #
  # Checkin
  #
  class UserExistsError(hlib.error.BaseError):
    def __init__(self, **kwargs):
      kwargs['reply_status']	= 403

      super(UserExistsError, self).__init__(**kwargs)

  class ValidateRegistration(hlib.input.SchemaValidator):
    username			= hlib.input.Username()
    password1			= hlib.input.Password()
    password2			= hlib.input.Password()
    email			= hlib.input.Email()

    chained_validators = [hlib.input.FieldsMatch('password1', 'password2')]

  @require_write
  @validate_by(schema = ValidateRegistration)
  @api
  def checkin(self, username = None, password1 = None, password2 = None, email = None):
    # pylint: disable-msg=R0201
    if username in hruntime.dbroot.users:
      raise UserExistsError(orig_fields = True, invalid_field = 'username')

    u = lib.datalayer.User(username, lib.pwcrypt(password1), email)
    hruntime.dbroot.users[u.name] = u
