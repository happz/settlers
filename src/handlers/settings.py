import calendar
import time
import pprint

import hlib
import hlib.api
import hlib.database
import hlib.error
import hlib.input

import games
import handlers
import lib
import lib.datalayer

# Handlers
from handlers import require_login, require_write, page
from hlib.api import api
from hlib.input import Username, Password, CommonString, OneOf, SchemaValidator, NotEmpty, Int, FieldsMatch, validator_factory, validate_by
from games import ValidateKind, GenericValidateKind

# pylint: disable-msg=F0401
import hruntime

TABLE_ROW_COUNTS = range(10, 61, 10)

ValidateColor = validator_factory(CommonString(), OneOf(games.settlers.COLOR_SPACE.colors.keys()))

class ApiTokenHandler(handlers.GenericHandler):
  @require_write
  @require_login
  @api
  def new(self):
    u = hruntime.user

    u.reset_api_tokens()
    u.api_tokens.append(hlib.api.api_token_generate(u))

    return hlib.api.Reply(200, token = u.api_tokens[0])

  @require_login
  @api
  def download(self):
    hruntime.response.headers['Content-Type'] = 'application/force-download'
    hruntime.response.headers['Content-Disposition'] = 'attachment; filename=settlers.conf'

    return hlib.api.Raw({'api_token': hruntime.user.api_tokens[0]})

class OpponentColor(hlib.api.ApiJSON):
  def __init__(self, user, color):
    super(OpponentColor, self).__init__(['user', 'color'])

    self.user = hlib.api.User(user)
    self.color = color.to_api()

class OpponentsHandler(handlers.GenericHandler):
  @require_login
  @validate_by(schema = GenericValidateKind)
  @api
  def colors(self, kind = None):
    gm = games.game_module(kind)

    return hlib.api.Reply(200, colors = [gm.COLOR_SPACE.colors[cn].to_api() for cn in gm.COLOR_SPACE.unused_colors(hruntime.user)])

  @require_login
  @validate_by(schema = GenericValidateKind)
  @api
  def opponents(self, kind = None):
    gm = games.game_module(kind)

    if kind not in hruntime.user.colors:
      return hlib.api.Reply(200, users = [])

    for k, v in hruntime.user.colors[kind].items():
      print k, v

    return hlib.api.Reply(200, users = [OpponentColor(hruntime.dbroot.users[username], gm.COLOR_SPACE.colors[hruntime.user.colors[kind][username]]) for username in hruntime.user.colors[kind].keys() if username != hruntime.user.name])

  class ValidateAdd(GenericValidateKind):
    username = hlib.input.Username()
    color = validator_factory(hlib.input.CommonString())
    
  @require_write
  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, username = None, kind = None, color = None):
    if username not in hruntime.dbroot.users:
      raise hlib.error.NoSuchUserError(username, invalid_field = 'username')

    opponent = hruntime.dbroot.users[username]

    gm = games.game_module(kind)

    if color not in gm.COLOR_SPACE.colors:
      raise hlib.error.InconsistencyError(msg = 'No such color')

    color = gm.COLOR_SPACE.colors[color]

    if opponent == hruntime.user:
      raise hlib.error.InconsistencyError(msg = 'You can not set color for yourself')

    if color.name not in gm.COLOR_SPACE.unused_colors(hruntime.user):
      raise hlib.error.InconsistencyError(msg = 'You can not use this color')

    if len(gm.COLOR_SPACE.unused_colors(hruntime.user)) <= 3:
      raise hlib.error.InconsistencyError(msg = 'You have no free colors to use')

    if kind not in hruntime.user.colors:
      hruntime.user.colors[kind] = hlib.database.StringMapping()

    hruntime.user.colors[kind][opponent.name] = color.name
    hruntime.user._v_used_colors = None

  class ValidateRemove(GenericValidateKind):
    username = hlib.input.Username()

  @require_write
  @require_login
  @validate_by(schema = ValidateRemove)
  @api
  def remove(self, kind = None, username = None):
    if kind not in hruntime.user.colors or username not in hruntime.user.colors[kind]:
      raise hlib.error.InconsistencyError(msg = 'There is no such colorized opponent')

    del hruntime.user.colors[kind][username]
    hruntime.user._v_used_colors = None

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
  api_token	= ApiTokenHandler()

  @require_login
  @page
  def index(self):
    return self.generate('settings.mako')

  #
  # Items per page
  #
  # Used for all tables - games, statistics, ... - if there are any tables at all...
  #
  class ValidatePerPage(SchemaValidator):
    per_page = validator_factory(NotEmpty(), Int(), OneOf(TABLE_ROW_COUNTS))

  @require_write
  @require_login
  @validate_by(schema = ValidatePerPage)
  @api
  def per_page(self, per_page = None):
    hruntime.user.table_length = per_page

    return hlib.api.Reply(200, form = hlib.api.Form(updated_fields = {'per_page': hruntime.user.table_length}))

  #
  # Board skin
  #
  # Select which skin user'd like to use in his games
  #
  class ValidateBoardSkin(SchemaValidator):
    skin = validator_factory(CommonString(), OneOf(['real', 'simple']))

  @require_write
  @require_login
  @validate_by(schema = ValidateBoardSkin)
  @api
  def board_skin(self, skin = None):
    hruntime.user.board_skin = skin

    return hlib.api.Reply(200, form = hlib.api.Form(updated_fields = {'skin': hruntime.user.board_skin}))

  #
  # Password
  #
  # Change password
  #
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

  #
  # Color
  #
  # Change user's color
  #
  class ValidateMyColor(SchemaValidator):
    kind = ValidateKind()
    color = ValidateColor()

  @require_write
  @require_login
  @validate_by(schema = ValidateMyColor)
  @api
  def color(self, kind = None, color = None):
    gm = games.settlers

    if color not in gm.COLOR_SPACE.colors:
      raise NoSuchColorError(color)

    color = gm.COLOR_SPACE.colors[color]

    if color.name not in gm.COLOR_SPACE.unused_colors(hruntime.user):
      raise hlib.error.InconsistencyError(msg = 'You can not use this color')

    hruntime.user.color(gm.COLOR_SPACE, new_color = color)

  #
  # After "Pass turn"
  #
  # What to do after player passes his turn.
  #
  class ValidateAfterPassTurn(SchemaValidator):
    action = validator_factory(NotEmpty(), Int(), OneOf([lib.datalayer.User.AFTER_PASS_TURN_STAY, lib.datalayer.User.AFTER_PASS_TURN_NEXT, lib.datalayer.User.AFTER_PASS_TURN_CURR]))()

  @require_write
  @require_login
  @validate_by(schema = ValidateAfterPassTurn)
  @api
  def after_pass_turn(self, action = None):
    hruntime.user.after_pass_turn = action

    return hlib.api.Reply(200, form = hlib.api.Form(updated_fields = {'action': hruntime.user.after_pass_turn}))

  #
  # Sound
  #
  # Ring a bell when player is on turn
  #
  class ValidateSound(SchemaValidator):
    sound = validator_factory(NotEmpty(), Int(), OneOf([0, 1]))

  @require_write
  @require_login
  @validate_by(schema = ValidateSound)
  @api
  def sound(self, sound = None):
    hruntime.user.sound = (sound == 1)

    return hlib.api.Reply(200, form = hlib.api.Form(updated_fields = {'sound': hruntime.user.sound == True and 1 or 0}))
