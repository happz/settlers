"""
Data layer objects and method

@author:			Milos Prchlik
@contact:			U{happz@happz.cz}
@license:			DPL (U{http://www.php-suit.com/dpl})
"""

import threading

import hlib
import hlib.database
import hlib.datalayer
import hlib.engine
import hlib.log

import lib.chat
import games

# pylint: disable-msg=F0401
import hruntime

def SystemUser():
  if not hasattr(SystemUser, 'user_instance'):
    SystemUser.user_instance = hlib.datalayer.DummyUser('__system__')

  return SystemUser.user_instance

# --- Database records -----------------------------------------------
counters_lock = threading.RLock()

class Counters(hlib.database.DBObject):
  def __init__(self):
    hlib.database.DBObject.__init__(self)

    self.games			= hlib.database.Length()
    self.games_archived		= hlib.database.Length()
    self.games_active		= hlib.database.Length()
    self.games_free		= hlib.database.Length()
    self.games_inactive		= hlib.database.Length()

    self.tournaments		= hlib.database.Length()
    self.tournaments_archived	= hlib.database.Length()
    self.tournaments_active	= hlib.database.Length()
    self.tournaments_free	= hlib.database.Length()
    self.tournaments_inactive	= hlib.database.Length()

hlib.event.Hook('game.GameCreated', 'update_counters',  lambda e:     not hruntime.dbroot.counters.games.change(1) \
                                                                  and not hruntime.dbroot.counters.games_active.change(1) \
                                                                  and not hruntime.dbroot.counters.games_free.change(1))
hlib.event.Hook('game.GameStarted', 'update_counters',  lambda e: hruntime.dbroot.counters.games_free.change(-1))
hlib.event.Hook('game.GameFinished', 'update_counters', lambda e:     not hruntime.dbroot.counters.games_active.change(-1) \
                                                                  and not hruntime.dbroot.counters.games_inactive.change(1))
hlib.event.Hook('game.GameArchived', 'update_counters', lambda e: hruntime.dbroot.counters.games_archived.change(1))

hlib.event.Hook('tournament.Created', 'update_counters',  lambda e:     not hruntime.dbroot.counters.tournaments.change(1) \
                                                                  and not hruntime.dbroot.counters.tournaments_active.change(1) \
                                                                  and not hruntime.dbroot.counters.tournaments_free.change(1))
hlib.event.Hook('tournament.Started', 'update_counters',  lambda e: hruntime.dbroot.counters.tournaments_free.change(-1))
hlib.event.Hook('tournament.Finished', 'update_counters', lambda e:     not hruntime.dbroot.counters.tournaments_active.change(-1) \
                                                                  and not hruntime.dbroot.counters.tournaments_inactive.change(1))
hlib.event.Hook('tournament.Archived', 'update_counters', lambda e: hruntime.dbroot.counters.tournaments_archived.change(1))

class Server(hlib.datalayer.Server):
  def __init__(self):
    hlib.datalayer.Server.__init__(self)

    self.chat_posts		= lib.chat.ChatPosts()

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

    self.donors			= hlib.database.SimpleList()

    self.counters		= Counters()
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

    self.seen_board	= False

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

    return color_space.colors[self.colors[color_space.kind][self.name]]

  def used_colors(self, color_space):
    used_colors  = [self.color(color_space).name]
    used_colors += self.colors[color_space.kind].values()

    return used_colors

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
