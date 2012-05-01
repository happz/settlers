import handlers
import hlib
import lib.trumpet

import hlib.api

# Handlers
from hlib.api import api
from handlers import page, require_login, require_admin, require_write

# Validators
import hlib.input
from hlib.input import validate_by

# pylint: disable-msg=F0401
import hruntime

ValidateLang	= hlib.input.validator_factory(hlib.input.CommonString())
ValidateName	= hlib.input.validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(256))
ValidateValue	= hlib.input.validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(256))

class ApiTokens(hlib.api.ApiJSON):
  def __init__(self, lang):
    super(ApiTokens, self).__init__(['tokens'])

    self.tokens = []

    for key in lang.tokens.iterkeys():
      self.tokens.append({'name': key})

class ApiToken(hlib.api.ApiJSON):
  def __init__(self, value):
    super(ApiToken, self).__init__(['value'])

    self.value = value

class AdminStatsHandler(handlers.GenericHandler):
  @handlers.require_admin
  @handlers.require_login
  @page
  def index(self):
    return self.generate('admin_stats.mako')

class AdminEventsHandler(handlers.GenericHandler):
  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin_events.mako')

class TrumpetHandler(handlers.GenericHandler):
  password_recovery_mail = lib.trumpet.PasswordRecoveryMail()
  board                = lib.trumpet.Board()

  class ValidateChangePasswordRecoveryMail(hlib.input.SchemaValidator):
    subject = hlib.input.validator_factory(hlib.input.CommonString())
    text = hlib.input.validator_factory(hlib.input.CommonString())

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateChangePasswordRecoveryMail)
  @api
  def change_password_recovery_mail(self, subject = None, text = None):
    self.password_recovery_mail.subject = subject
    self.password_recovery_mail.text = text

    return hlib.api.ApiReply(200, updated_fields = {'subject': self.password_recovery_mail.subject, 'text': self.password_recovery_mail.text})

  class ValidateChangeBoard(hlib.input.SchemaValidator):
    text = hlib.input.validator_factory(hlib.input.CommonString())

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateChangeBoard)
  @api
  def change_board(self, text = None):
    self.board.text = text

    return hlib.api.ApiReply(200, updated_fields = {'text': self.board.text})

class I18NHandler(handlers.GenericHandler):
  class ValidateTokens(hlib.input.SchemaValidator):
    lang = ValidateLang()

  @require_admin
  @require_login
  @validate_by(schema = ValidateTokens)
  @api
  def tokens(self, lang = None, name = None):
    return ApiTokens(hruntime.dbroot.localization.languages[lang])

  class ValidateToken(hlib.input.SchemaValidator):
    lang = ValidateLang()
    name = ValidateName()

  @require_admin
  @require_login
  @validate_by(schema = ValidateToken)
  @api
  def token(self, lang = None, name = None):
    return ApiToken(hruntime.dbroot.localization.languages[lang].tokens[name])

  class ValidateAdd(hlib.input.SchemaValidator):
    lang = ValidateLang()
    name = ValidateName()
    value = ValidateValue()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, lang = None, name = None, value = None):
    hruntime.dbroot.localization.languages[lang].tokens[name] = value

  class ValidateRemove(hlib.input.SchemaValidator):
    lang = ValidateLang()
    name = ValidateName()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateRemove)
  @api
  def remove(self, lang = None, name = None):
    del hruntime.dbroot.localization.languages[lang].tokens[name]

class Handler(handlers.GenericHandler):
  i18n		= I18NHandler()
  trumpet	= TrumpetHandler()
  events    = AdminEventsHandler()
  stats     = AdminStatsHandler()

  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin.mako')
