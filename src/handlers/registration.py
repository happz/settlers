import random
import handlers
import lib.datalayer
import hlib.mail

import lib

# Handlers
from hlib.api import api, ApiReply
from handlers import page, require_write

# Validators
from hlib.input import validate_by, Username, Password, Email, FieldsMatch, SchemaValidator

# pylint: disable-msg=F0401
import hruntime

class RecoveryHandler(handlers.GenericHandler):
  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'password_recovery', self.generate, 'password_recovery.mako')

  class ValidatePasswordRecovery(SchemaValidator):
    username = Username()
    email = Email()

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

  @page
  def index(self):
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'registration', self.generate, 'registration.mako')

  class ValidateRegistration(SchemaValidator):
    username = Username()
    password1 = Password()
    password2 = Password()
    email = Email()

    chained_validators = [FieldsMatch('password1', 'password2')]

  @require_write
  @validate_by(schema = ValidateRegistration)
  @api
  def checkin(self, username = None, password1 = None, password2 = None, email = None):
    # pylint: disable-msg=R0201
    if username in hruntime.dbroot.users:
      return reply(403, message = 'User name already used', orig_fields = True, invalid_field = 'username')

    u = lib.datalayer.User(username, lib.pwcrypt(password1), email)
    hruntime.dbroot.users[u.name] = u
