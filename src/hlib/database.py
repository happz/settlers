__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import sys

import ZODB.DB
import ZODB.ActivityMonitor
import ZODB.POSException
import transaction
import BTrees
import persistent
import threading

from collections import OrderedDict

import hlib.console
import hlib.error
import hlib.locks
import hlib.log
from hlib.stats import stats as STATS

import hruntime # @UnresolvedImport

class Command_Database(hlib.console.Command):
  def __init__(self, console, parser):
    super(Command_Database, self).__init__(console, parser)

    self.parser.add_argument('--list', '-l', action = 'store_const', dest = 'action', const = 'list')

    self.parser.add_argument('--update-stats', action = 'store_const', dest = 'action', const = 'update-stats')
    self.parser.add_argument('--enable-lt', action = 'store_const', dest = 'action', const = 'enable-lt')
    self.parser.add_argument('--disable-lt', action = 'store_const', dest = 'action', const = 'disable-lt')
    self.parser.add_argument('--pack', action = 'store_const', dest = 'action', const = 'pack')
    self.parser.add_argument('--gc', action = 'store_const', dest = 'action', const = 'gc')

    self.parser.add_argument('--name', action = 'store', dest = 'name')

  def __get_db_by_name(self, args):
    if 'name' not in args:
      self.console.err_required_arg('name')

    for app in self.console.engine.apps.values():
      if app.db.name == args.name:
        return app.db

    raise hlib.console.CommandException('Unknown db \'%s\'' % args.name)

  def handler(self, args):
    if args.action == 'list':
      return {'databases': [{'name': app.db.name, 'address': str(app.db.address)} for app in self.console.engine.apps.values()]}

    if args.action == 'enable-lt':
      return self.__get_db_by_name(args.name).set_transaction_logging(True)

    if args.action == 'disable-lt':
      return self.__get_db_by_name(args.name).set_transaction_logging(False)

    if args.action == 'pack':
      return self.__get_db_by_name(args.name).pack()

    if args.action == 'gc':
      return self.__get_db_by_name(args.name).globalGC()

    if args.action == 'update-stats':
      return self.__get_db_by_name(args.name).update_stats()

    return {'args': str(args)}

class CommitFailedError(hlib.error.BaseError):
  pass

class Storage(object):
  # pylint: disable-msg=W0613
  @staticmethod
  def open(address):
    return None

class Storage_MySQL(Storage):
  @staticmethod
  def open(address):
    try:
      import relstorage.storage
      import relstorage.adapters.mysql

      adapter = relstorage.adapters.mysql.MySQLAdapter(host = address.host,
                                                       user = address.user,
                                                       passwd = address.password,
                                                       db     = address.path)

      return relstorage.storage.RelStorage(adapter)

    except Exception, e:
      raise hlib.error.BaseError(msg = e.args[1], exception = e, exc_info = sys.exc_info())

class Storage_File(Storage):
  @staticmethod
  def open(address):
    import ZODB.FileStorage

    return ZODB.FileStorage.FileStorage(address.path)

storage_classes = {
  'RelStorage': Storage_MySQL,
  'FileStorage': Storage_File
}

class DBAddress(object):
  _fields = {
    'storage':    0,
    'substorage': 1,
    'user':       2,
    'password':   3,
    'host':       4,
    'path':       5
  }

  def __init__(self, line):
    super(DBAddress, self).__init__()

    self.fields = line.split(':')

  def __getattr__(self, name):
    if name in self._fields.keys():
      return self.fields[self._fields[name]]

  def __str__(self):
    return ':'.join(['%s=%s' % (k, getattr(self, k)) for k in self._fields.keys()])

class DB(object):
  def __init__(self, name, address, **kwargs):
    super(DB, self).__init__()

    self.name		= name
    self.address	= address
    self.db		= None
    self.root		= None

    self.log_transaction_handler = self.__nolog_transaction
    self.log_transaction_lock = hlib.locks.RLock(name = 'Transaction logging setup')

    self.kwargs		= kwargs

    self.stats_name	= 'Database (%s)' % self.name

    # pylint: disable-msg=W0621
    STATS.set(self.stats_name, OrderedDict([
      ('Loads', 0),
      ('Stores', 0),
      ('Commits', 0),
      ('Rollbacks', 0),
      ('Failed commits', 0),
      ('Connections', {}),
      ('Caches', {})
    ]))

    import events
    events.Hook('engine.ThreadFinished', self.on_thread_finished)
    events.Hook('engine.RequestFinished', self.on_request_finished)

  def on_thread_finished(self, _):
    self.update_stats()

  def on_request_finished(self, _):
    self.update_stats()

  @property
  def is_opened(self):
    return self.db != None

  def set_transaction_logging(self, enabled = False):
    with self.log_transaction_lock:
      if enabled:
        self.log_transaction_handler = self.__log_transaction
      else:
        self.log_transaction_handler = self.__nolog_transaction

  def open(self):
    storage = storage_classes[self.address.storage].open(self.address)
    self.db = ZODB.DB(storage, **self.kwargs)

    self.db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

  def close(self):
    self.db.close()
    self.db = None

  def connect(self):
    connection = self.db.open()
    self.root = connection.root()

    return (connection, self.root)

  def log_transaction(self, *args, **kwargs):
    # Transaction logging is broken - because of locking - lock is required even for NOP action :(
    return

    with self.log_transaction_lock:
      self.log_transaction_handler(*args, **kwargs)

  def __log_transaction(self, state, *args, **kwargs):
    hlib.log.log_transaction(transaction.get(), state, *args, tid = hruntime.tid, **kwargs)

  def __nolog_transaction(self, *args, **kwargs):
    pass

  def start_transaction(self):
    self.log_transaction("pre-create")

    transaction.abort()
    transaction.begin()

    self.log_transaction('post-create')

  def commit(self):
    try:
      with STATS:
        STATS.inc(self.stats_name, 'Commits')

      self.log_transaction('pre-commit')
      transaction.commit()
      self.doom()
      self.log_transaction('post-commit')

    except ZODB.POSException.ConflictError, e:
      self.log_transaction('post-commit-fail')

      with STATS:
        STATS.inc(self.stats_name, 'Failed commits')

      print >> sys.stderr, 'Conflict Error:'
      print >> sys.stderr, '  class_name: ' + str(e.class_name)
      print >> sys.stderr, '  msg: ' + str(e.message)
      print >> sys.stderr, '  data: ' + str(e.args)
      print >> sys.stderr, '  info: ' + str(e.serials)

      #print traceback.format_exc()
      #print e

      return False

    return True

  def doom(self):
    hruntime.dont_commit = True

    self.log_transaction('pre-doom')
    transaction.doom()
    self.log_transaction('post-doom')

  def rollback(self):
    with STATS:
      STATS.inc(self.stats_name, 'Rollbacks')

    self.log_transaction('pre-abort')
    transaction.abort()
    self.doom()
    self.log_transaction('post-abort')

  def pack(self):
    self.db.pack()

  def minimize_cache(self):
    self.db.minimizeCache()

  def localGC(self):
    hruntime.dbconn.cacheGC()
    hruntime.dbconn.cacheMinimize()

  def poolGC(self):
    return
    self.db._a()
    self.db.pool.availableGC()
    self.db.historical_pool.availableGC()
    self.db._r()

  def globalGC(self):
    return
    self.db._a()
    self.db.pool.availableGC()
    self.db.historical_pool.availableGC()
    self.db._r()

  def update_stats(self):
    data = self.db.getActivityMonitor().getActivityAnalysis(divisions = 1)[0]
    connections = {}
    caches = {}

    i = 0
    for data in self.db.connectionDebugInfo():
      connections[i] = {
        'Opened': data['opened'],
        'Info': data['info'],
        'Before': data['before']
      }
      i += 1

    for data in self.db.cacheDetailSize():
      caches[data['connection']] = {
        'Connection': data['connection'],
        'Non-ghost size': data['ngsize'],
        'Size': data['size']
      }

    STATS.set(self.stats_name, 'Load', data['loads'] if 'loads' in data else 0)
    STATS.set(self.stats_name, 'Stores', data['stores'] if 'stores' in data else 0)
    STATS.set(self.stats_name, 'Connections', connections)
    STATS.set(self.stats_name, 'Caches', caches)

class DBObject(persistent.Persistent):
  def __init__(self, *args, **kwargs):
    persistent.Persistent.__init__(self, *args, **kwargs)

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
    hruntime.db.log_transaction('pre-conflict-resolve')

    # just log and fail
    resolved = True
    resultState = savedState.copy()

    try:
      print >> sys.stderr, 'DB Conflict detected:'
      if hruntime.user:
        print >> sys.stderr, '  User: %s' % hruntime.user.name.encode('ascii', 'replace')

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
      hruntime.db.log_transaction('post-conflict-resolve')
      if not resolved:
        raise ZODB.POSException.ConflictError

      return resultState

class IndexedMapping(DBObject):
  def __init__(self, first_key = None, *args, **kwargs):
    DBObject.__init__(self, *args, **kwargs)

    self.data = BTrees.IOBTree.IOBTree()

    if first_key == None:
      self.first_key = 0

    else:
      self.first_key = first_key

  def __len__(self):
    return len(self.data)

  def __iter__(self):
    return iter(self.data)

  def __setitem__(self, key, value):
    self.data[key] = value

  def __getitem__(self, key):
    return self.data[key]

  def __delitem__(self, key):
    del self.data[key]

  def __contains__(self, key):
    return key in self.data

  def iteritems(self):
    return self.data.iteritems()

  def iterkeys(self):
    return self.data.iterkeys()

  def itervalues(self):
    return self.data.itervalues()

  def keys(self, *args, **kwargs):
    return self.data.keys(*args, **kwargs)

  def values(self, *args, **kwargs):
    return self.data.values(*args, **kwargs)

  def items(self, *args, **kwargs):
    return self.data.items(*args, **kwargs)

  def push(self, o):
    if len(self.data) == 0:
      i = self.first_key

    else:
      i = self.data.maxKey() + 1

    o.id = i
    self.data[i] = o

  def pop(self):
    i = self.data.maxKey()
    del self.data[i]

  def last(self):
    return self.data[self.data.maxKey()]

from BTrees.IOBTree import IOBTree as TreeMapping  # @UnusedImport
from BTrees.OOBTree import OOBTree as StringMapping
ObjectMapping = StringMapping

from persistent.list import PersistentList as SimpleList  # @UnusedImport
from persistent.mapping import PersistentMapping as SimpleMapping  # @UnusedImport

from BTrees.Length import Length  # @UnusedImport
