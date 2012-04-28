import calendar
import time

import hlib
import hlib.error

import games
import handlers
import lib
import lib.datalayer

# Handlers
from handlers import require_login, require_write, page
from hlib.api import api, ApiReply
from hlib.input import Username, Password, CommonString, OneOf, SchemaValidator, NotEmpty, Int, FieldsMatch, validator_factory, validate_by
from games import ValidateKind

# pylint: disable-msg=F0401
import hruntime

TABLE_ROW_COUNTS = range(10, 61, 10)

ValidateColor = validator_factory(CommonString(), OneOf(games.settlers.COLOR_SPACE.colors.keys()))

class OpponentsHandler(handlers.GenericHandler):
  @require_write
  @require_login
  @api
  def add(self, username = None, kind = None, color = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.Error('No such player', invalid_field = 'username')

    opponent = hruntime.dbroot.users[username]

    gm = games.game_module(kind)

    if color not in gm.COLOR_SPACE.colors:
      hlib.error.Error('No such color')

    color = gm.COLOR_SPACE.colors[color]

    if opponent == hruntime.user:
      raise hlib.error.Error('You can not set color for yourself')

    if color.name not in gm.COLOR_SPACE.unused_colors(hruntime.user):
      raise hlib.error.Error('You can not use this color')

    if len(gm.COLOR_SPACE.unused_colors(hruntime.user)) <= 3:
      raise hlib.error.Error('You have no free colors to use')

    hruntime.user.colors[kind][opponent.name] = color.name

  @require_write
  @require_login
  @api
  def remove(self, kind = None, username = None):
    if kind not in hruntime.user.colors or username not in hruntime.user.colors[kind]:
      raise hlib.error.Error(msg = 'There is no such colorized opponent')

    del hruntime.user[kind][username]

class VacationHandler(handlers.GenericHandler):
  @require_write
  @require_login
  @api
  def start(self, vacation_from_day = None, vacation_from_hour = None, vacation_to_day = None, vacation_to_hour = None):
    start = calendar.timegm(time.strptime('00:00:00 ' + vacation_from_day, '%H:%M:%S %d.%m.%Y')) + vacation_from_hour * 3600
    end = calendar.timegm(time.strptime('00:00:00 ' + vacation_to_day, '%H:%M:%S %d.%m.%Y')) + vacation_to_hour * 3600

    start = start + time.timezone
    end = end + time.timezone
    if time.daylight:
      start = start - 3600
      end = end - 3600

    hruntime.user.vacation_revoke()
    hruntime.user.vacation_prepare(start, end)

  @require_write
  @require_login
  @api
  def revoke(self):
    hruntime.user.vacation_revoke()

class Handler(handlers.GenericHandler):
  vacation      = VacationHandler()
  opponents     = OpponentsHandler()

  class ValidateTableLength(SchemaValidator):
    per_page = validator_factory(NotEmpty(), Int(), OneOf(TABLE_ROW_COUNTS))

  @require_write
  @require_login
  @validate_by(schema = ValidateTableLength)
  @api
  def table_length(self, per_page = None):
    hruntime.user.table_length = per_page

    return ApiReply(200, updated_fields = {'per_page': hruntime.user.table_length})

  class ValidateBoardSkin(SchemaValidator):
    skin = validator_factory(CommonString(), OneOf(['real', 'simple']))

  @require_write
  @require_login
  @validate_by(schema = ValidateBoardSkin)
  @api
  def board_skin(self, skin = None):
    hruntime.user.board_skin = skin

    return ApiReply(200, updated_fields = {'skin': hruntime.user.board_skin})

  class ValidatePassword(SchemaValidator):
    password1 = Password()
    password2 = Password()

    chained_validators = [FieldsMatch('password1', 'password2')]

  @require_write
  @require_login
  @validate_by(schema = ValidatePassword)
  @api
  def password(self, password1 = None, password2 = None):
    hruntime.user.password = lib.pwcrypt(password1)

  class ValidateMyColor(SchemaValidator):
    color = ValidateColor()

  @require_write
  @require_login
  @validate_by(schema = ValidateMyColor)
  @api
  def color(self, color = None):
    color = games.settlers.COLOR_SPACE.colors[color]

    if color.name not in games.settlers.COLOR_SPACE.unused_colors(hruntime.user):
      raise hlib.error.Error('You can not use this color')

    hruntime.user.color(games.settlers.COLOR_SPACE, new_color = color)

  class ValidateAfterPassTurn(SchemaValidator):
    action = validator_factory(NotEmpty(), Int(), OneOf([lib.datalayer.User.AFTER_PASS_TURN_STAY, lib.datalayer.User.AFTER_PASS_TURN_NEXT, lib.datalayer.User.AFTER_PASS_TURN_CURR]))()

  @require_write
  @require_login
  @validate_by(schema = ValidateAfterPassTurn)
  @api
  def after_pass_turn(self, action = None):
    hruntime.user.after_pass_turn = action

    return ApiReply(200, updated_fields = {'action': hruntime.user.after_pass_turn})

  class ValidateSound(SchemaValidator):
    sound = validator_factory(NotEmpty(), Int(), OneOf([0, 1]))

  @require_write
  @require_login
  @validate_by(schema = ValidateSound)
  @api
  def sound(self, sound = None):
    hruntime.user.sound = (sound == 1)

    return ApiReply(200, updated_fields = {'sound': hruntime.user.sound == True and 1 or 0})

  @require_login
  @page
  def index(self):
    return self.generate('settings.mako')
