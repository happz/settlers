__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import handlers
import lib.trumpet

import hlib.api
import hlib.database
import hlib.datalayer
import hlib.input

# Shortcuts
from handlers import page, require_admin, require_login, require_write
from hlib.api import api
from hlib.input import validator_factory, validate_by

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

ValidateLang	= validator_factory(hlib.input.CommonString())
ValidateName	= validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(256))
ValidateValue	= validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(256))

class ValidateLangSchema(hlib.input.SchemaValidator):
  lang = ValidateLang()

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

    for user in hruntime.dbroot.users.values():
      user.seen_board = False

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

    return hlib.api.Reply(200, tokens = [{'name': name} for name in lang.tokens.keys()])

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

    return hlib.api.Reply(200, value = lang[name])

  #
  # Edit
  #
  class ValidateEdit(ValidateLangSchema):
    name = ValidateName()
    value = ValidateValue()

  @require_write
  @require_admin
  @require_login
  @validate_by(schema = ValidateEdit)
  @api
  def edit(self, lang = None, name = None, value = None):
    lang = require_lang(lang)

    lang[name] = value

    hruntime.cache.remove(lib.datalayer.SystemUser(), 'i18n')

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

    hruntime.cache.remove(lib.datalayer.SystemUser(), 'i18n')

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

    hruntime.cache.remove(lib.datalayer.SystemUser(), 'i18n')

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

    return hlib.api.Reply(200, tokens = [{'name': name} for name in coverage[2].keys()])

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

    return hlib.api.Reply(200, tokens = [{'name': name} for name in coverage[1].keys()])

class DonationsHandler(handlers.GenericHandler):
  @require_login
  @require_admin
  @api
  def list_full(self):
    return hlib.api.Reply(200, donations = [{'user': hlib.api.User(donor), 'amount': amount} for donor, amount in hruntime.dbroot.donors])

  class ValidateAdd(hlib.input.SchemaValidator):
    username = hlib.input.Username()
    amount = hlib.input.validator_factory(hlib.input.NotEmpty(), hlib.input.Number())

  @require_login
  @require_admin
  @require_write
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, username = None, amount = None):
    if username not in hruntime.dbroot.users:
      user = hlib.datalayer.DummyUser(username)
    else:
      user = hruntime.dbroot.users[username]

    hruntime.dbroot.donors.append((user, amount))

  class ValidateRemove(hlib.input.SchemaValidator):
    username = hlib.input.Username()

  @require_login
  @require_admin
  @require_write
  @validate_by(schema = ValidateRemove)
  @api
  def remove(self, username = None):
    donors_updated = hlib.database.SimpleList()

    for e in hruntime.dbroot.donors:
      if e[0].name == username:
        continue
      donors_updated.append(e)

    hruntime.dbroot.donors = donors_updated

class Handler(handlers.GenericHandler):
  i18n		= I18NHandler()
  trumpet	= TrumpetHandler()
  donations			= DonationsHandler()

  @require_admin
  @require_login
  @page
  def index(self):
    return self.generate('admin.mako')
