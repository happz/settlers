import games.settlers
import handlers
import hlib
import lib.chat

import hlib.api
import hlib.error
import hlib.log

# Handlers
from handlers import page, require_login, require_write
from hlib.api import api

# Validators
from hlib.input import validator_factory, validate_by, SchemaValidator, CommonString, Password, NotEmpty, Int, OneOf, StringBool
from games import ValidateGID
from lib.chat import ValidateChatPost
from handlers.game import require_presence_in_game, require_on_turn, require_on_game
from games import GenericValidateGID

# pylint: disable-msg=F0401
import hruntime

ValidateNID = validator_factory(NotEmpty(), Int(), OneOf(range(0, 128)))
ValidatePID = validator_factory(NotEmpty(), Int(), OneOf(range(0, 128)))
ValidateResource = validator_factory(CommonString(), OneOf(['sheep', 'wood', 'rock', 'grain', 'clay']))

class GameOnTurnChecker(object):
  @staticmethod
  def check():
    return [g for g in games.f_active(hruntime.user) if not g.is_free and g.my_player != None and g.my_player.is_on_turn]

class Handler(handlers.GenericHandler):
  class ValidatNodehClick(GenericValidateGID):
    nid = ValidateNID()

  @require_write
  @require_login
  @validate_by(schema = ValidatNodehClick)
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

  @require_write
  @require_login
  @api
  def number_click(self, gid = None, nid = None):
    require_on_turn(gid)

    return hruntime.dbroot.games[gid].number_clicked(nid)

  class ValidateExchange(GenericValidateGID):
    ratio = validator_factory(NotEmpty, Int, OneOf([2, 3, 4]))
    amount = validator_factory(NotEmpty, Int)
    src = validator_factory(NotEmpty, Int, OneOf([0, 1, 2, 3, 4]))
    dst = validator_factory(NotEmpty, Int, OneOf([0, 1, 2, 3, 4]))

  @require_write
  @require_login
  @validate_by(schema = ValidateExchange)
  @api
  def exchange(self, gid = None, ratio = None, amount = None, src = None, dst = None):
    require_on_game(gid)

    hruntime.dbroot.games[gid].my_player.exchange_resources(ratio, src, dst, amount)

    return hlib.api.ApiReply(200)

  @require_write
  @require_login
  @api
  def invention(self, gid = None, resource1 = None, resource2 = None):
    require_on_turn(gid)

    return hruntime.dbroot.games[gid].apply_invention(resource1, resource2)

  @require_write
  @require_login
  @api
  def monopoly(self, gid = None, resource = None):
    require_on_turn(gid)

    return hruntime.dbroot.games[gid].apply_monopoly(resource)

  @require_write
  @require_login
  @validate_by(schema = GenericValidateGID)
  @api
  def roll_dice(self, gid = None):
    g = require_on_turn(gid)

    return g.roll_dice()

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
