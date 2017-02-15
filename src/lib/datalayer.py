"""
Data layer objects and method

@author:			Milos Prchlik
@contact:			U{happz@happz.cz}
@license:			DPL (U{http://www.php-suit.com/dpl})
"""

import os.path
import threading
import time
import urllib

import persistent
import ZODB.POSException
import BTrees

import hlib.database
import hlib.datalayer
import hlib.events
import hlib.locks

import lib.chat


class DBObject(persistent.Persistent):
  def __getattr__(self, name):
    raise AttributeError(name)

  def __resolve_conflict_diff(self, oldState, savedState, newState):
    diff = []

    for key in oldState.keys():
      value = oldState[key]
      if value != savedState[key] or value != newState[key]:
        diff.append(key)

    return diff

  def __resolve_conflict(self, key, oldState, savedState, newState, resultState):
    return False

  def _p_resolveConflict(self, oldState, savedState, newState):
    # just log and fail
    resolved = True
    resultState = savedState.copy()

    try:
      print >> sys.stderr, 'DB Conflict detected:'

      diff = self.__resolve_conflict_diff(oldState, savedState, newState)
      print >> sys.stderr, '  Conflicting keys: %s' % ', '.join(diff)

      for key in diff:
        if self.__resolve_conflict(key, oldState, savedState, newState, resultState) == True:
          continue

        print >> sys.stderr, '  Key %s unresolved' % key
        resolved = False
        break

    except Exception, e:
      print >> sys.stderr, 'DB Conflict resolution failed'
      print >> sys.stderr, e

    finally:
      if not resolved:
        raise ZODB.POSException.ConflictError

      return resultState

class IndexedMapping(DBObject):
    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()

    def __setitem__(self, *args, **kwargs):
        return self._data.__setitem__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self._data.__getitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self._data.__delitem__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self._data.__contains__(*args, **kwargs)

    def iteritems(self, *args, **kwargs):
        return self._data.iteritems(*args, **kwargs)

    def iterkeys(self, *args, **kwargs):
        return self._data.iterkeys(*args, **kwargs)

    def itervalues(self, *args, **kwargs):
        return self._data.itervalues(*args, **kwargs)

    def items(self, *args, **kwargs):
        return self._data.items(*args, **kwargs)

    def keys(self, *args, **kwargs):
        return self._data.keys(*args, **kwargs)

    def values(self, *args, **kwargs):
        return self._data.values(*args, **kwargs)

    def max_key(self, *args, **kwargs):
        return self._data.maxKey()

    def __init__(self, first_key = None, *args, **kwargs):
        DBObject.__init__(self, *args, **kwargs)

        self._data = BTrees.IOBTree.IOBTree()
        self._first_key = first_key or 0

    def __setstate__(self, *args, **kwargs):
        DBObject.__setstate__(self, *args, **kwargs)

        if not hasattr(self, '_data'):
            self._data = self.data
            del self.data

        if not hasattr(self, '_first_key'):
            self._first_key = self.first_key
            del self.first_key

    def push(self, o):
        index = self._first_key if len(self) == 0 else (self.max_key() + 1)

        o.id = index
        self[index] = o

    def pop(self):
        del self[self.max_key()]

    def last(self):
        return self[self.max_key()]

def SystemUser():
  if not hasattr(SystemUser, 'user_instance'):
    SystemUser.user_instance = hlib.datalayer.DummyUser('__system__')

  return SystemUser.user_instance

# --- Database records -----------------------------------------------
counters_lock = hlib.locks.RLock(name = 'Counters lock')

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

hlib.events.Hook('game.GameCreated', lambda e:     not hruntime.dbroot.counters.games.change(1) \
                                                                  and not hruntime.dbroot.counters.games_active.change(1) \
                                                                  and not hruntime.dbroot.counters.games_free.change(1))
hlib.events.Hook('game.GameStarted',   lambda e: hruntime.dbroot.counters.games_free.change(-1))
hlib.events.Hook('game.GameFinished', lambda e:     not hruntime.dbroot.counters.games_active.change(-1) \
                                                                  and not hruntime.dbroot.counters.games_inactive.change(1))
hlib.events.Hook('game.GameArchived',  lambda e: hruntime.dbroot.counters.games_archived.change(1))

hlib.events.Hook('tournament.Created',   lambda e:     not hruntime.dbroot.counters.tournaments.change(1) \
                                                                  and not hruntime.dbroot.counters.tournaments_active.change(1) \
                                                                  and not hruntime.dbroot.counters.tournaments_free.change(1))
hlib.events.Hook('tournament.Started',  lambda e: hruntime.dbroot.counters.tournaments_free.change(-1))
hlib.events.Hook('tournament.Finished',  lambda e:     not hruntime.dbroot.counters.tournaments_active.change(-1) \
                                                                  and not hruntime.dbroot.counters.tournaments_inactive.change(1))
hlib.events.Hook('tournament.Archived',  lambda e: hruntime.dbroot.counters.tournaments_archived.change(1))

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

class User(DBObject):
    AFTER_PASS_TURN_STAY = 0
    AFTER_PASS_TURN_NEXT = 1
    AFTER_PASS_TURN_CURR = 2

    VACATION_STATE_NOP     = 0
    VACATION_STATE_ENTERED = 1

    def __init__(self, name, password, email):
        DBObject.__init__(self)

        self.name           = unicode(name)
        self.password       = unicode(password)
        self.admin          = False
        self.date_format = '%d/%m/%Y %H:%M:%S'
        self.email          = unicode(email)
        self.maintenance_access     = False

        self.events         = hlib.database.IndexedMapping()

        self.elo		= 0
        self.after_pass_turn = User.AFTER_PASS_TURN_NEXT
        self.last_board	= 0
        self.board_skin	= 'real'
        self.autoplayer	= False
        self.sound		= False
        self.table_length   = 20

        self.colors		= hlib.database.SimpleMapping()

        self.seen_board	= False

        self._v_last_access = None

    def __setstate__(self, *args, **kwargs):
        DBObject.__setstate__(self, *args, **kwargs)

        self._v_last_access = None

    def __eq__(self, other):
        if not isinstance(other, User):
            return False

        return self.name == other.name

    def __ne__(self, other):
        if not isinstance(other, User):
            return True

        return self.name != other.name

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.name)

    def touch(self):
        self._v_last_access = time.time()

    def _createAPIDataCurrent(self):
        return {
            'username':      self.name,
            'email':         self.email,
            'afterPassTurn': self.after_pass_turn,
            'perPage':       self.table_length,
            'sound':         self.sound,
            'colors':        {
                game: self.colors[game][self.name] for game in self.colors.iterkeys()
            },
            'isAdmin':       self.admin
        }

    def _createAPIDataCommon(self):
        return {
            'name': self.name,
            'isOnline': self.is_online
        }

    def toAPI(self, current = False):
        if current is True:
            return self._createAPIDataCurrent()

        else:
            return self._createAPIDataCommon()

    def __getattr__(self, name):
        if name == 'is_online':
            if self._v_last_access is None:
                return False

            return True if (time.time() - self._v_last_access) <= 30 * 60 else False

        return DBObject.__getattr__(self, name)

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
