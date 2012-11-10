"""
Data layer objects and method

@author:			Milos Prchlik
@contact:			U{happz@happz.cz}
@license:			DPL (U{http://www.php-suit.com/dpl})
"""

import hlib
import hlib.database
import hlib.datalayer
import hlib.engine
import hlib.log

import lib.chat
import games

# pylint: disable-msg=F0401
import hruntime

from hlib.datalayer import DummyUser

# --- Database records -----------------------------------------------
class Server(hlib.datalayer.Server):
  def __init__(self):
    hlib.datalayer.Server.__init__(self)

    self.chat_posts		= lib.chat.ChatPosts()

  def __getattr__(self, name):
    if name == 'total_games_count':
      return len(hruntime.dbroot.games) + len(hruntime.dbroot.games_archived)

    return hlib.datalayer.Server.__getattr__(self, name)

class Stats(hlib.database.DBObject):
  def __init__(self):
    hlib.database.DBObject.__init__(self)

    self.settlers = None

class Trumpet(hlib.database.DBObject):
  def __init__(self):
    hlib.database.DBObject.__init__(self)

    self.PasswordRecoveryMail = hlib.database.SimpleMapping()
    self.Board = hlib.database.SimpleMapping()
    self.VacationTermination = hlib.database.SimpleMapping()

class Root(hlib.datalayer.Root):
  def __init__(self):
    hlib.datalayer.Root.__init__(self)

    self.server			= Server()
    self.colors			= hlib.database.SimpleList()
    self.games			= hlib.database.IndexedMapping()
    self.games_archived		= hlib.database.SimpleMapping()
    self.tournaments		= hlib.database.IndexedMapping()
    self.tournaments_archived	= hlib.database.SimpleMapping()
    self.trumpet = hlib.database.SimpleMapping()
    self.stats   = Stats()
    self.trumpet = Trumpet()

    self.dummy_owner = None

class Vacation(hlib.database.DBObject):
  def __init__(self):
    hlib.datalayer.DBObject.__init__(self)

    self.start = None
    self.length = None
    self.killed = None

class User(hlib.datalayer.User):
  AFTER_PASS_TURN_STAY = 0
  AFTER_PASS_TURN_NEXT = 1
  AFTER_PASS_TURN_CURR = 2

  VACATION_STATE_NOP     = 0
  VACATION_STATE_ENTERED = 1

  def __init__(self, name, password, email):
    hlib.datalayer.User.__init__(self, name, password, email)

    self.elo		= 0
    self.after_pass_turn = User.AFTER_PASS_TURN_NEXT
    self.last_board	= 0
    self.board_skin	= 'real'
    self.vacation	= 604800
    self.autoplayer	= False
    self.sound		= False
    self.table_length   = 20

    self.vacations      = hlib.database.IndexedMapping()
    self.colors		= hlib.database.SimpleMapping()

    # Caches
    self._v_used_colors		= None

  def __getattr__(self, name):
    if name == 'is_autoplayer':
      return self.autoplayer == True

    if name == 'has_vacation':
      return self.last_vacation != None

    if name == 'has_prepared_vacation':
      return self.has_vacation and hruntime.time < self.last_vacation.start

    if name == 'last_vacation':
      return None if self.vacation == 0 or len(self.vacations) == 0 else self.vacations.last()

    if name == 'is_on_vacation':
      return self.has_vacation and self.last_vacation.killed == None and self.last_vacation.start <= hruntime.time and hruntime.time <= self.last_vacation.start + self.last_vacation.length

    return hlib.datalayer.User.__getattr__(self, name)

  def color(self, color_space, new_color = None):
    if color_space.kind not in self.colors:
      self.colors[color_space.kind] = hlib.database.StringMapping()

      if new_color:
        self.colors[color_space.kind][self.name] = new_color.name

      else:
        self.colors[color_space.kind][self.name] = color_space.DEFAULT_COLOR_NAME

    if new_color != None:
      self.colors[color_space.kind][self.name] = new_color.name
      self._v_used_colors = None

    return color_space.colors[self.colors[color_space.kind][self.name]]

  def used_colors(self, color_space):
    if not hasattr(self, '_v_used_colors') or self._v_used_colors == None:
      self._v_used_colors = {}

    if color_space.kind not in self._v_used_colors:
      self._v_used_colors[color_space.kind] = [self.color(color_space).name]

    if color_space.kind in self.colors:
      self._v_used_colors[color_space.kind] += self.colors[color_space.kind].values()

    return self._v_used_colors[color_space.kind]

  def vacation_revoke(self):
    if self.has_prepared_vacation:
      self.vacation += self.last_vacation.length
      self.vacations.pop()

  def vacation_kill(self):
    if self.is_on_vacation:
      self.last_vacation.killed = hruntime.time

  def vacation_prepare(self, start, end):
    if end <= start:
      raise hlib.error.BaseError('You can not finish vacation before it begin')

    if start < hruntime.time:
      raise hlib.error.BaseError('Start time can not be in past')

    length = end - start
    if self.vacation < length:
      raise hlib.error.BaseError('You do not have enough vacation available')

    self.vacation -= length

    v = Vacation()
    v.start = start
    v.length = length

    self.vacations.push(v)

  def vacation_add_game(self):
    self.vacation = max(self.vacation + 86400, 2592000)

