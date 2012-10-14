import games.settlers
import handlers
import hlib
import lib.chat

import hlib.api
import hlib.error
import hlib.log

# Shortcuts
from handlers import page, require_login, require_write
from hlib.api import api
from hlib.input import validate_by, validator_factory

# Validators
from games import ValidateGID
from lib.chat import ValidateChatPost
from handlers.game import require_presence_in_game, require_on_turn, require_on_game
from games import GenericValidateGID

# pylint: disable-msg=F0401
import hruntime

ValidateNID = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf(range(0, 128)))
ValidatePID = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf(range(0, 128)))
ValidateResource = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([0, 1, 2, 3, 4]))

class GameOnTurnChecker(object):
  @staticmethod
  def check():
    return [g for g in games.f_active(hruntime.user) if not g.is_free and g.my_player != None and g.my_player.is_on_turn]

class Handler(handlers.GenericHandler):
  class ValidatNodeClick(GenericValidateGID):
    nid = ValidateNID()

  @require_write
  @require_login
  @validate_by(schema = ValidatNodeClick)
  @api
  def node_click(self, gid = None, nid = None):
    require_on_turn(gid)

    return hruntime.dbroot.games[gid].node_clicked(nid)

  class ValidatePathClick(GenericValidateGID):
    pid = ValidatePID()

  @require_write
  @require_login
  @validate_by(schema = ValidatePathClick)
  @api
  def path_click(self, gid = None, pid = None):
    require_on_turn(gid)

    return hruntime.dbroot.games[gid].path_clicked(pid)

  class ValidateNumberClick(GenericValidateGID):
    nid = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf(range(1, 20)))

  @require_write
  @require_login
  @validate_by(schema = ValidateNumberClick)
  @api
  def number_click(self, gid = None, nid = None):
    require_on_turn(gid)

    return hruntime.dbroot.games[gid].number_clicked(nid)

  class ValidateExchange(GenericValidateGID):
    ratio = validator_factory(hlib.input.NotEmpty(), hlib.input.Int(), hlib.input.OneOf([2, 3, 4]))
    amount = validator_factory(hlib.input.NotEmpty(), hlib.input.Int())
    src = ValidateResource()
    dst = ValidateResource()

  @require_write
  @require_login
  @validate_by(schema = ValidateExchange)
  @api
  def exchange(self, gid = None, ratio = None, amount = None, src = None, dst = None):
    g = require_on_game(gid)

    g.my_player.exchange_resources(ratio, src, dst, amount)

  class ValidateInvention(GenericValidateGID):
    resource1 = ValidateResource()
    resource2 = ValidateResource()

  @require_write
  @require_login
  @validate_by(schema = ValidateInvention)
  @api
  def invention(self, gid = None, resource1 = None, resource2 = None):
    g = require_on_turn(gid)

    g.apply_invention(resource1, resource2)

  class ValidateMonopoly(GenericValidateGID):
    resource = ValidateResource()

  @require_write
  @require_login
  @validate_by(schema = ValidateMonopoly)
  @api
  def monopoly(self, gid = None, resource = None):
    g = require_on_turn(gid)

    g.apply_monopoly(resource)

  @require_write
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def roll_dice(self, gid = None):
    g = require_on_turn(gid)

    g.roll_dice()

  class ValidatePassTurnFirst(GenericValidateGID):
    allow_extra_fields = True

  @require_write
  @require_login
  @validate_by(schema = ValidatePassTurnFirst)
  @api
  def pass_turn_first(self, gid = None, first_village = None, first_path = None):
    return hruntime.root.game.do_pass_turn(gid, first_village = first_village, first_path = first_path)

  @require_write
  @require_login
  @validate_by(schema = ValidatePassTurnFirst)
  @api
  def pass_turn_second(self, gid = None, second_village = None, second_path = None):
    return hruntime.root.game.do_pass_turn(gid, second_village = second_village, second_path = second_path)
