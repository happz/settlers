import formencode
import handlers
import hlib
import lib.trumpet

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

class AdminTestHandler(handlers.GenericHandler):
  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin_test.mako')

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

class AdminTrumpetHandler(handlers.GenericHandler):
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

  class ValidateChangeMOTD(hlib.input.SchemaValidator):
    text = hlib.input.validator_factory(hlib.input.CommonString())

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateChangeMOTD)
  @api
  def change_motd(self, text = None):
    self.motd.text = text

  class ValidateChangeBoard(hlib.input.SchemaValidator):
    text = hlib.input.validator_factory(hlib.input.CommonString())

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateChangeBoard)
  @api
  def change_board(self, text = None):
    self.board.text = text

  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin_trumpet.mako', params = {'trumpet': self})

class AdminLanguagesHandler(handlers.GenericHandler):
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
    hruntime.localization[lang][name] = value

  class ValidateRemove(hlib.input.SchemaValidator):
    lang = ValidateLang()
    name = ValidateName()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateRemove)
  @api
  def remove(self, lang = None, name = None):
    del hruntime.localization.languages[lang][name]

  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin_languages.mako', params = {'languages': self})

class Handler(handlers.GenericHandler):
  languages = AdminLanguagesHandler()
  trumpet   = AdminTrumpetHandler()
  events    = AdminEventsHandler()
  test      = AdminTestHandler()
  stats     = AdminStatsHandler()

  @require_login
  @page
  def index(self):
    return self.generate('admin.mako')

  @require_write
  @require_admin
  @require_login
  @api
  def game(self):
    import games

    games.create_system_game('settlers', limit = 3, turn_limit = 604800)
