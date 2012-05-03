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

class ValidateLangSchema(hlib.input.SchemaValidator):
  lang = ValidateLang()

class ApiTokens(hlib.api.ApiJSON):
  def __init__(self, names):
    super(ApiTokens, self).__init__(['tokens'])

    self.tokens = [{'name': name} for name in names]

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
  @require_admin
  @require_login
  @validate_by(schema = ValidateLangSchema)
  @api
  def tokens(self, lang = None, name = None):
    return ApiTokens(hruntime.dbroot.localization.languages[lang].tokens.keys())

  class ValidateToken(ValidateLangSchema):
    name = ValidateName()

  @require_admin
  @require_login
  @validate_by(schema = ValidateToken)
  @api
  def token(self, lang = None, name = None):
    return ApiToken(hruntime.dbroot.localization.languages[lang][name])

  class ValidateAdd(ValidateLangSchema):
    name = ValidateName()
    value = ValidateValue()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, lang = None, name = None, value = None):
    hruntime.dbroot.localization.languages[lang][name] = value

  class ValidateRemove(ValidateLangSchema):
    name = ValidateName()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateRemove)
  @api
  def remove(self, lang = None, name = None):
    del hruntime.dbroot.localization.languages[lang][name]

  @require_admin
  @require_login
  @validate_by(schema = ValidateLangSchema)
  @api
  def unused(self, lang = None):
    lang = hruntime.dbroot.localization.languages[lang]

    if lang.coverage:
      coverage = lang.coverage.coverage(lang)

    return ApiTokens(coverage[2].keys())

  @require_admin
  @require_login
  @validate_by(schema = ValidateLangSchema)
  @api
  def missing(self, lang = None):
    lang = hruntime.dbroot.localization.languages[lang]

    if lang.coverage:
      coverage = lang.coverage.coverage(lang)

    return ApiTokens(coverage[1].keys())

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
