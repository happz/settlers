__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import handlers
import lib.trumpet

import hlib
import hlib.api
import hlib.input

# Shortcuts
from handlers import page, require_admin, require_login, require_write
from hlib.api import api
from hlib.input import validator_factory, validate_by

# pylint: disable-msg=F0401
import hruntime

ValidateLang	= validator_factory(hlib.input.CommonString())
ValidateName	= validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(256))
ValidateValue	= validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(256))

class ValidateLangSchema(hlib.input.SchemaValidator):
  lang = ValidateLang()

class Tokens(hlib.api.ApiJSON):
  def __init__(self, names):
    super(Tokens, self).__init__(['tokens'])

    self.tokens = [{'name': name} for name in names]

class Token(hlib.api.ApiJSON):
  def __init__(self, value):
    super(Token, self).__init__(['value'])

    self.value = value

def require_lang(lang):
  if lang not in hruntime.dbroot.localization.languages:
    raise hlib.error.InvalidInputError(invalid_field = 'lang')

  return hruntime.dbroot.localization.languages[lang]

class TrumpetHandler(handlers.GenericHandler):
  password_recovery_mail	= lib.trumpet.PasswordRecoveryMail()
  board				= lib.trumpet.Board()

  #
  # Change Password Recovery Mail
  #
  class ValidateChangePasswordRecoveryMail(hlib.input.SchemaValidator):
    subject			= hlib.input.validator_factory(hlib.input.CommonString())
    text			= hlib.input.validator_factory(hlib.input.CommonString())

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateChangePasswordRecoveryMail)
  @api
  def change_password_recovery_mail(self, subject = None, text = None):
    self.password_recovery_mail.subject = subject
    self.password_recovery_mail.text = text

    return hlib.api.Reply(200, form = hlib.api.Form(updated_fields = {'subject': self.password_recovery_mail.subject, 'text': self.password_recovery_mail.text}))

  #
  # Change Board
  #
  class ValidateChangeBoard(hlib.input.SchemaValidator):
    text = hlib.input.validator_factory(hlib.input.UnicodeString())

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateChangeBoard)
  @api
  def change_board(self, text = None):
    self.board.text = text

    return hlib.api.Reply(200, form = hlib.api.Form(updated_fields = {'text': self.board.text}))

class I18NHandler(handlers.GenericHandler):
  #
  # Tokens
  #
  @require_admin
  @require_login
  @validate_by(schema = ValidateLangSchema)
  @api
  def tokens(self, lang = None):
    lang = require_lang(lang)

    return Tokens(lang.tokens.keys())

  #
  # Token
  #
  class ValidateToken(ValidateLangSchema):
    name = ValidateName()

  @require_admin
  @require_login
  @validate_by(schema = ValidateToken)
  @api
  def token(self, lang = None, name = None):
    lang = require_lang(lang)

    return Token(lang[name])

  #
  # Add
  #
  class ValidateAdd(ValidateLangSchema):
    name = ValidateName()
    value = ValidateValue()

  @handlers.require_write
  @handlers.require_admin
  @handlers.require_login
  @hlib.input.validate_by(schema = ValidateAdd)
  @hlib.api.api
  def add(self, lang = None, name = None, value = None):
    lang = require_lang(lang)

    lang[name] = value

  #
  # Remove
  #
  class ValidateRemove(ValidateLangSchema):
    name = ValidateName()

  @handlers.require_write
  @handlers.require_admin
  @handlers.require_login
  @hlib.input.validate_by(schema = ValidateRemove)
  @hlib.api.api
  def remove(self, lang = None, name = None):
    lang = require_lang(lang)

    del lang[name]

  #
  # Unused
  #
  @require_admin
  @require_login
  @validate_by(schema = ValidateLangSchema)
  @api
  def unused(self, lang = None):
    lang = require_lang(lang)

    if lang.coverage:
      coverage = lang.coverage.coverage(lang)

    return Tokens(coverage[2].keys())

  #
  # Missing
  #
  @require_admin
  @require_login
  @validate_by(schema = ValidateLangSchema)
  @api
  def missing(self, lang = None):
    lang = require_lang(lang)

    if lang.coverage:
      coverage = lang.coverage.coverage(lang)

    return Tokens(coverage[1].keys())

class Handler(handlers.GenericHandler):
  i18n		= I18NHandler()
  trumpet	= TrumpetHandler()

  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin.mako')
