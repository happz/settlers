__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import functools
import http_parser.util
import ipaddr
import os
import os.path
import StringIO
import sys
import threading
import time
import urllib
import UserDict

try:
  import http_parser.parser as HTTPParser
except ImportError:
  import http_parser.pyparser as HTTPParser

import hlib.cache
import hlib.compress
import hlib.console
import hlib.database
import hlib.events
import hlib.handlers
import hlib.http
import hlib.http.cookies
import hlib.locks
import hlib.log
import hlib.scheduler
import hlib.server

from collections import OrderedDict
from hlib.stats import stats as STATS

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

ENGINES = []
ENGINES_LOCK = hlib.locks.RLock(name = 'Engines')

class Command_Engine(hlib.console.Command):
  def __init__(self, console, parser, engine):
    super(Command_Engine, self).__init__(console, parser)

    self.engine = engine

    self.parser.add_argument('--save-sessions', action = 'store_const', dest = 'action', const = 'save-sessions')

  def handler(self, args):
    if args.action == 'save-sessions':
      for app in self.engine.apps.values():
        if app.sessions != None:
          app.sessions.save_sessions()

class AppChannels(object):
  CHANNEL_TYPES = ['access', 'error', 'transactions', 'events']

  def __init__(self):
    super(AppChannels, self).__init__()

    self.access = []
    self.error = []
    self.transactions = []
    self.events = []

    self.all_channels = []

    self.state = dict(map(lambda x: (x, True), AppChannels.CHANNEL_TYPES))

  def add(self, output, *channels):
    for c in channels:
      getattr(self, output).append(c)
      self.all_channels.append(c)

  def reopen(self):
    map(lambda c: c.reopen(), self.all_channels)

  def close(self):
    map(lambda c: c.close(), self.all_channels)

  def enabled(self, channel_type, *args):
    if len(args) == 1:
      self.state[channel_type] = bool(args[0])

    return self.state[channel_type] == True

  access_enabled = property(lambda self: self.enabled('access'), lambda self, state: self.enabled('access', state))
  error_enabled = property(lambda self: self.enabled('error'), lambda self, state: self.enabled('error', state))
  transactions_enabled = property(lambda self: self.enabled('transaction'), lambda self, state: self.enabled('transactions', state))
  events_enabled = property(lambda self: self.enabled('events'), lambda self, state: self.enabled('events', state))

class Application(object):
  """
  This class represents one of our applications. Binds together database access, logging channels and tree of handlers.
  """

  def __init__(self, name, root, db, config, channels = None, cache = None, config_file = None):
    """
    @type name:			C{string}
    @param name:		Name of application. Any string at all.
    @type root:			L{handlers.GenericHandler}
    @param root:		Root of tree of handlers.
    @type db:			L{database.DB}
    @param db:			Database access.
    """

    super(Application, self).__init__()

    import hlib.api
    import hlib.cache

    self.engines = []

    self.name = name
    self.root = root
    self.db = db
    self.config = config

    self.config_file = config_file

    self.cache = cache or hlib.cache.Cache('Global', self)
    self.channels = channels or AppChannels()
    self.sessions = None
    self.api_tokens = hlib.api.ApiTokenCache(self.name, self)

    for channel_type in self.channels.CHANNEL_TYPES:
      key = 'log.' + channel_type + '.enabled'
      self.channels.enabled(channel_type, key in self.config and self.config[key])

    hlib.events.trigger('app.Started', None, app = self)

  def __repr__(self):
    return '<engine.Application(\'%s\', %s, %s, <config>)>' % (self.name, self.root, self.db)

  @staticmethod
  def default_config(app_path):
    return {
      'dir': app_path,
      'title': None,
      'label': None,

      'cache.enabled': False,

      'templates.dirs': [os.path.join(app_path, 'src', 'templates'), os.path.join(os.path.dirname(hlib.__file__), 'templates')],
      'templates.tmp_dir': os.path.join(app_path, 'compiled'),

      'pages': os.path.join(app_path, 'pages'),

      'mail.server': 'localhost',

      'log.access.enabled': True,
      'log.access.format': '{date} {time} {request_line} {response_status} {response_length} {request_ip} {request_user}',
      'log.access.channels': '<default log>',

      'log.error.enabled': True,
      'log.error.channels': '<default log>, <stderr>',

      'log.transactions.enabled': True,
      'log.transactions.channels': '<default log>',

      'log.events.enabled': True,
      'log.events.channels': '<default log>, <stderr>',

      'sessions.time': 2 * 86400,
      'sessions.cookie_name': 'hlib_sid',

      'static.enabled': False,
      'static.root': '/tmp'
    }

  def get_handler(self, requested):
    def __static_fallback():
      if self.config.get('static.enabled', False):
        import hlib.handlers.static

        return hlib.handlers.static.StaticHandler().generate

      import hlib.http
      raise hlib.http.NotFound()

    h = self.root

    for token in requested.split('?')[0].split('/')[1:]:
      if len(token) == 0:
        break

      if hasattr(h, token):
        h = getattr(h, token)
        continue

      return __static_fallback()

    if isinstance(h, hlib.handlers.GenericHandler):
      if not hasattr(h, 'index'):
        return __static_fallback()

      h = h.index

    return h

  def __log(self, msg, channels, flush = False):
    for c in channels:
      c.log_message(msg)

    if flush:
      c.flush()

  def log_access(self):
    if not self.channels.access_enabled:
      return

    params = hlib.log.log_params()

    self.__log(self.config['log.access.format'].format(**params), self.channels.access)

  def log_event(self, event):
    if not self.channels.error_enabled:
      return

    self.__log('%s: %s' % (event.__class__.ename(), event.to_api()), self.channels.events)

class HeaderMap(UserDict.UserDict):
  """
  Dictionary-like object storing HTTP headers and their values.

  All header names are converted to first-letter-capitalized format on all operations (get/set/delete). Used by L{engine.Request} and L{engine.Response}.

  @todo:			Support more than 1 header simultaneously (for Cookie header, etc.)
  """

  def __contains__(self, name):
    return UserDict.UserDict.__contains__(self, name.title())

  def __getitem__(self, name):
    return UserDict.UserDict.__getitem__(self, name.title())

  def __setitem__(self, name, value):
    UserDict.UserDict.__setitem__(self, name.title(), value)

  def __delitem__(self, name):
    UserDict.UserDict.__delitem__(self, name.title())

class MultipartPiece(object):
  def __init__(self):
    super(MultipartPiece, self).__init__()

    self.headers = HeaderMap()
    self.data = None

class Request(object):
  def __init__(self, socket, client_address, server):
    super(Request, self).__init__()

    self.socket = socket
    self.client_address = client_address
    self.server	= server

    self.input = []
    self.parts = []
    self.parser = HTTPParser.HttpParser()

    self.base	= None
    self.cookies = {}
    self.handler = None
    self.headers = HeaderMap()
    self.http_version = None
    self.method = None
    self.params = {}
    self.params_valid = False
    self.requested = None
    self.requested_line = None

    self.api_token = None

    self.ctime = time.time()
    self.read_bytes = 0
    self.written_bytes = 0

    self._ips		= None

  requires_login = property(lambda self: hlib.handlers.tag_fn_check(self.handler, 'require_login', False))
  requires_admin = property(lambda self: hlib.handlers.tag_fn_check(self.handler, 'require_admin', False))
  requires_write = property(lambda self: hlib.handlers.tag_fn_check(self.handler, 'require_write', False))
  requires_hosts = property(lambda self: hlib.handlers.tag_fn_check(self.handler, 'require_hosts', False))

  is_prohibited = property(lambda self: hlib.handlers.tag_fn_check(self.handler, 'prohibited', False))
  is_tainted = property(lambda self: hruntime.session != None and hasattr(hruntime.session, 'tainted') and hruntime.session.tainted != False)
  is_authenticated = property(lambda self: hruntime.session != None and hasattr(hruntime.session, 'authenticated') and hruntime.session.authenticated == True)

  @property
  def ips(self):
    try:
      if 'X-Forwarded-For' not in self.headers:
        return [ipaddr.IPAddress(self.client_address[0])]

      entries = [e.strip() for e in self.headers['X-Forwarded-For'].split(',')]
      filtered_entries = []

      while len(entries) > 0:
        entry = entries.pop(0)
        if len(entry.split('.')) < 4:
          if len(entries) <= 0:
            print >> sys.stderr, 'Failed to pop from entries: "%s"' % self.headers['X-Forwarded-For']
            break
          entry = entry + entries.pop(0)
        filtered_entries.append(entry)

      entries = [e.strip() for e in self.headers['X-Forwarded-For'].split(',')]

      if len(entries) != len(filtered_entries):
        print >> sys.stderr, 'Bad X-Forwarded-For: "%s" vs "%s"' % (str(entries), str(filtered_entries))

      return [ipaddr.IPAddress(self.client_address[0])] + ([ipaddr.IPAddress(ip.strip()) for ip in filtered_entries])

    except ValueError, e:
      print >> sys.stderr, '----- ----- Invalid IP address ----- -----'
      print >> sys.stderr, e
      print >> sys.stderr, 'Client address:', self.client_address
      print >> sys.stderr, 'X-Forwarded-For:', self.headers['X-Forwarded-For']
      return []

  def read_data(self):
    while True:
      data = self.socket.recv(1024)

      if not data:
        break

      len_recv = len(data)
      len_parsed = self.parser.execute(data, len_recv)

      if len_recv != len_parsed:
        raise hlib.http.BadRequest()

      if self.parser.is_partial_body():
        self.input.append(self.parser.recv_body())

      self.read_bytes += len_recv

      if self.parser.is_message_complete():
        break

  def parse_data(self):
    if not self.parser.is_headers_complete():
      raise hlib.http.BadRequest()

    if not self.parser.is_message_complete():
      raise hlib.http.BadRequest()

    self.input = http_parser.util.b('').join(self.input).strip()

    self.requested_line = '%s %s' % (self.parser.get_method(), self.parser.get_path())
    self.requested = self.parser.get_path()

    for key, value in self.parser.get_headers().items():
      self.headers[key] = value

    if 'Host' in self.headers:
      self.base = self.headers['Host']

    self.method = self.parser.get_method().lower()

    if self.method not in ['get', 'post', 'head', 'options']:
      raise hlib.http.UnknownMethod(self.method)

    def __parse_param(s):
      l = s.strip().split('=')
      if len(l) < 2:
        raise hlib.http.BadRequest()

      n = l[0].strip()
      v = urllib.unquote_plus('='.join(l[1:]).strip())

      return (n, v)

    def __parse_params(ps):
      for param in ps.split('&'):
        n, v = __parse_param(param)

        self.params[n] = v

    # Parse cookies
    if 'Cookie' in self.headers:
      for cookie in self.headers['Cookie'].split(';'):
        n, v = __parse_param(cookie)
        self.cookies[n] = hlib.http.cookies.Cookie(n, value = v, server = self.server, max_age = hruntime.app.config['sessions.time'])

    for cookie in self.cookies.values():
      if cookie.name.startswith('SpryMedia_DataTables'):
        cookie.delete()

    # Parse GET params
    if len(self.parser.get_query_string()) > 0:
      __parse_params(self.parser.get_query_string())

    # Parse POST params
    if 'Content-Type' in self.headers:
      ct = self.headers['Content-Type']

      if ct.startswith('application/x-www-form-urlencoded'):
        if len(self.input) <= 0:
          pass
          #raise http.BadRequest('Content-Type == x-www-form-urlencoded and empty body')
        else:
          __parse_params(self.input)

      elif ct.startswith('multipart/form-data'):
        i = ct.find('boundary=')
        if i < 0:
          raise hlib.http.BadRequest('Content-Type == multipart/form-data and no boundary')
        boundary = '--' + ct[i + len('boundary='):]

        start = self.input.find(boundary, 0)
        if start < 0:
          raise hlib.http.BadRequest('Inconsistent boundary')

        end = self.input.find(boundary, start + 1)
        if end < 0:
          raise hlib.http.BadRequest('Inconsistent boundary')

        stream = StringIO.StringIO(self.input[start:end])
        piece = MultipartPiece()

        while True:
          l = stream.readline().strip()
          if len(l) <= 0:
            break

          if l == boundary:
            continue

          k = l.split(':')
          if len(k) != 2:
            raise hlib.http.BadRequest('Malformed header in multipart piece: "%s"' % l)
          piece.headers[k[0].strip()] = k[1].strip()

        piece.data = stream.read()
        self.parts.append(piece)

    # Restore session if any
    sid_cookie_name = hruntime.app.config['sessions.cookie_name']
    if sid_cookie_name in self.cookies:
      cookie = self.cookies[sid_cookie_name]

      if hruntime.app.sessions.exists(cookie.value):
        session = hruntime.app.sessions.load(cookie.value)

      else:
        session = hlib.http.session.Session.create()

    else:
      session = hlib.http.session.Session.create()

    if session.check():
      hruntime.session = session
    else:
      session.destroy()
      hruntime.session = None

class Response(object):
  def __init__(self):
    super(Response, self).__init__()

    self.cookies		= {}
    self.status                 = 200
    self.headers                = HeaderMap()
    self.location		= None
    self.time			= hruntime.time

    self.api_response = None

    self._output                = None
    self.output_length		= None

    self._raw_output		= None
    self.raw_output_length	= None

    self.output			= None
    self.raw_output		= None

    self.source_file = None

  def __getattr__(self, name):
    if name == 'output':
      return self._output

    if name == 'raw_output':
      return self._raw_output

    raise AttributeError(name)

  def __setattr__(self, name, value):
    if name == 'output':
      self._output = value

      if value == None:
        self.output_length = None
      else:
        self.output_length = len(value)

    if name == 'raw_output':
      self._raw_output = value

      if value == None:
        self.raw_output_length = None
      else:
        self.raw_output_length = len(value)

    super(Response, self).__setattr__(name, value)

  def dumps(self):
    req = hruntime.request

    self.headers['Connection'] = 'close'
    self.headers['Access-Control-Allow-Origin'] = '*'
    self.headers['Access-Control-Allow-Headers'] = 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'

    if 'Host' in req.headers:
      self.headers['Host'] = req.headers['Host']

    if hruntime.session != None:
      hruntime.session.save()

      sid_cookie_name = hruntime.app.config['sessions.cookie_name']
      if sid_cookie_name not in req.cookies or req.cookies[sid_cookie_name].value != hruntime.session.sid:
        session_cookie = hlib.http.cookies.Cookie(sid_cookie_name, value = hruntime.session.sid, server = req.server, max_age = hruntime.app.config['sessions.time'])
      else:
        session_cookie = req.cookies[sid_cookie_name]

      self.cookies[sid_cookie_name] = session_cookie

    for name, cookie in self.cookies.iteritems():
      self.headers['Set-Cookie'] = '%s=%s; Max-Age=%s; Path=%s' % (cookie.name, urllib.quote(cookie.value), cookie.max_age, cookie.path)

    if self.source_file:
      self.output = self.source_file.read()
      self.source_file.close()

    if self.output:
      if hasattr(req.server.config, 'compress') and req.server.config.compress == True:
        compressed = hlib.compress.compress(self.output)

        self.raw_output = self.output

        self.output = compressed

        self.headers['Content-Encoding'] = 'gzip'

      self.headers['Content-Length'] = self.output_length
    else:
      self.headers['Content-Length'] = 0

    lines = [
      'HTTP/1.1 %i %s' % (self.status, hlib.http.HTTP_CODES[self.status])
    ]

    for name, value in self.headers.iteritems():
      lines.append('%s: %s' % (name, value))

    lines.append('')

    if self.output != None and req.method != 'head':
      lines.append(self.output)

    return '\r\n'.join(lines) + '\r\n'

class DataBaseGCTask(hlib.scheduler.Task):
  def __init__(self):
    super(DataBaseGCTask, self).__init__('database-gc', self.database_gc, min = range(5, 60, 20))

  def database_gc(self, engine = None, app = None):
    if app.db != None and app.db.is_opened:
      app.db.globalGC()

class DatabasePackTask(hlib.scheduler.Task):
  def __init__(self):
    super(DatabasePackTask, self).__init__('database-pack', self.database_pack, hour = range(0, 23, 12))

  def database_pack(self, engine = None, app = None):
    if app.db != None and app.db.is_opened:
      app.db.pack()

class SaveSessionsTask(hlib.scheduler.Task):
  def __init__(self):
    super(SaveSessionsTask, self).__init__('save-sessions', self.save_sessions, min = range(10, 60, 20))

  def save_sessions(self, engine = None, app = None):
    if app.sessions != None:
      app.sessions.save_sessions()

class PurgeSessionsTask(hlib.scheduler.Task):
  def __init__(self):
    super(PurgeSessionsTask, self).__init__('purge-sessions', self.purge_sessions, min = range(0, 60, 5))

  def purge_sessions(self, engine = None, app = None):
    if app.sessions != None:
      app.sessions.purge()

class Engine(object):
  """
  Engine binds servers together.

  Right now there is no need to have more than 1 engine in application. Maybe some day...
  """

  def __init__(self, name, server_configs):
    super(Engine, self).__init__()

    self.name = name
    self.quit_event = threading.Event()

    self.servers = []
    self.apps = {}
    self.hooks = {}

    self.scheduler = hlib.scheduler.SchedulerThread(self)
    self.scheduler.start()

    self.scheduler.add_task(DataBaseGCTask(), None)
    self.scheduler.add_task(PurgeSessionsTask(), None)
    self.scheduler.add_task(SaveSessionsTask(), None)

    i = 0
    for sc in server_configs:
      self.apps[sc['app'].name] = sc['app']
      sc['app'].engines.append(self)

      server = hlib.server.Server(self, 'server-%i' % i, sc)
      self.servers.append(server)

      i += 1

    self.stats_name	= self.name

    STATS.set(self.stats_name, OrderedDict([
      ('Current time', lambda s: hruntime.time),
      ('Current requests', lambda s: len(s['Requests'])),

      ('Start time', time.time()),
      ('Uptime', lambda s: time.time() - s['Start time']),

      ('Total bytes read', 0),
      ('Total bytes written', 0),
      ('Total requests', 0),
      ('Total time', 0),

      ('Bytes read/second', lambda s: s['Total bytes read'] / s['Uptime'](s)),
      ('Bytes written/second', lambda s: s['Total bytes written'] / s['Uptime'](s)),
      ('Bytes read/request', lambda s: (s['Total requests'] and (s['Total bytes read'] / float(s['Total requests'])) or 0.0)),
      ('Bytes written/request', lambda s: (s['Total requests'] and (s['Total bytes written'] / float(s['Total requests'])) or 0.0)),
      ('Requests/second', lambda s: float(s['Total requests']) / s['Uptime'](s)),

      ('Requests', {}),

      ('Missing handlers', 0),
      ('RO requests', 0),
      ('Forced RO requests', 0),
      ('Failed commits', 0),
    ]))

    self.console = hlib.console.Console('main console', self, sys.stdin, sys.stdout)
    self.console.register_command('db', hlib.database.Command_Database)
    self.console.register_command('server', hlib.server.Command_Server)
    self.console.register_command('engine', Command_Engine, self)

    with ENGINES_LOCK:
      ENGINES.append(self)

  def on_log_reload(self, _):
    for app in self.apps.values():
      print 'Reopening channels for app %s' % app.name

      app.channels.reopen()

  def on_system_reload(self, _):
    for server in self.servers:
      server.stop()

    for app in self.apps.values():
      app.channels.close()

      if not app.db:
        continue

      app.db.close()
      app.db = None

  def on_thread_start(self, e):
    """
    Default hlib handler for C{engine.ThreadStarted} event.

    Set up thread enviroment (L{hruntime} variables) and open database connection.

    @type e:			L{events.engine.ThreadStarted}
    @param e:			Current event.
    """

    hruntime.reset_locals()

    hruntime.app = e.server.app
    hruntime.db = e.server.app.db
    hruntime.root = e.server.app.root

    thread_stats_setter = functools.partial(STATS.set, hruntime.service_server.pool.stats_name, 'Threads', hruntime.tid)
    thread_stats_setter('Total bytes read', 0)
    thread_stats_setter('Total bytes written', 0)
    thread_stats_setter('Total requests', 0)
    thread_stats_setter('Total time', 0)

    dbconn, dbroot = hruntime.db.connect()
    hruntime.db.start_transaction()

    hruntime.dbconn = dbconn
    hruntime.dbroot = dbroot

    if 'root' in dbroot:
      hruntime.dbroot = dbroot['root']
      hruntime.db.rollback()

  def on_thread_finished(self, _):
    """
    Default hlib handler for C{engine.ThreadFinished} event.
    """

    hruntime.dbconn.close()
    hruntime.db.poolGC()

  def on_request_connected(self, _):
    hruntime.clean()
    hruntime.db.start_transaction()

    hruntime.dont_commit = True

    with STATS:
      STATS.inc(self.stats_name, 'Total requests')

    STATS.set(self.stats_name, 'Requests', hruntime.tid, OrderedDict([
      ('Bytes read',     0),
      ('Bytes written',  0),
      ('Client',         hlib.server.ips_to_str(hruntime.request.ips)),
      ('Start time',     hruntime.time),
      ('Requested line', None),
      ('User',           None)
    ]))

  def on_request_accepted(self, _):
    STATS.set(self.stats_name, 'Requests', hruntime.tid, 'Client', hlib.server.ips_to_str(hruntime.request.ips))
    STATS.set(self.stats_name, 'Requests', hruntime.tid, 'Requested', hruntime.request.requested_line)

    hruntime.db.log_transaction('requested-set', requested = hruntime.request.requested)

  def on_request_started(self, _):
    """
    Default hlib handler for C{engine.RequestStarted} event.

    Prepare enviroment for (and based on) new request. Reset L{hruntime} properties to default values, start new db transaction, and check basic access controls for new request.

    @raise http.Prohibited:	Raised when requested resource is marked as prohibited (using L{handlers.prohibited})
    @raise http.Redirect:	Raised when requested resource is admin-access only (using L{handlers.require_admin}). Also can be raised by internal call to L{auth.check_session}.
    """

    req = hruntime.request

    if req.requires_write != True:
      hruntime.db.doom()

    if req.requires_hosts:
      hosts_allowed = req.requires_hosts()
      hosts_present = req.ips

      def __check_host(h):
        for host_allowed in hosts_allowed:
          if type(host_allowed) in (ipaddr.IPv4Address, ipaddr.IPv6Address) and h == host_allowed:
            return True
          if type(host_allowed) in (ipaddr.IPv4Network, ipaddr.IPv6Network) and h in host_allowed:
            return True

        return False

      if len(hosts_present) <= 0:
        # handler has require_hosts but client present no address => fail
        passed = False

      elif len(hosts_present) == 1:
        passed = __check_host(hosts_present[0])

      elif len(hosts_present) > 1:
        passed = __check_host(hosts_present[1])

      if passed != True:
        hruntime.db.doom()
        raise hlib.http.Prohibited()

    if req.requires_login:
      io_regime = hlib.handlers.tag_fn_check(req.handler, 'ioregime', None)
      if not io_regime:
        hruntime.db.doom()
        raise hlib.http.Prohibited()

      io_regime.check_session()
      hruntime.db.log_transaction('user-assigned')

      STATS.set(self.stats_name, 'Requests', hruntime.tid, 'User', hruntime.user.name)

    if req.is_prohibited:
      hruntime.db.doom()
      raise hlib.http.Prohibited()

    if hruntime.dbroot.server.maintenance_mode == True and req.requires_login and hruntime.user.maintenance_access != True:
      hruntime.db.doom()
      raise hlib.http.Redirect('/maintenance/')

    if req.requires_admin and not hruntime.user.is_admin:
      hruntime.db.doom()
      raise hlib.http.Redirect('/admin/')

    hruntime.dont_commit = False

  def on_request_finished(self, _):
    """
    Default hlib handler for C{engine.RequestFinished} event.

    Clean up after finished request. Log access into access log, commit (or rollback) database changes.
    """

    hruntime.app.log_access()

    req = hruntime.request
    t = time.time() - req.ctime

    def db_stats_incer(*args):
      with STATS:
        STATS.inc(self.stats_name, *args)

    if not hruntime.request.handler:
      hruntime.db.rollback()
      db_stats_incer('Missing handlers')
      return

    if hruntime.request.requires_write != True:
      hruntime.db.rollback()
      db_stats_incer('RO requests')
      return

    if hruntime.dont_commit != False:
      hruntime.db.rollback()
      db_stats_incer('Forced RO requests')
      return

    if hruntime.db.commit() == True:
      return

    db_stats_incer('Failed commits')
    hruntime.db.rollback()

  def on_request_closed(self, _):
    """
    Default hlib handler for C{engine.RequestFinished} event.

    Clean up after finished request, and update statistics.
    """

    req = hruntime.request
    t = time.time() - req.ctime

    thread_stats_adder = functools.partial(STATS.add, hruntime.service_server.pool.stats_name, 'Threads', hruntime.tid)
    engine_stats_adder = functools.partial(STATS.add, self.stats_name)

    thread_stats_adder('Total bytes read', req.read_bytes)
    thread_stats_adder('Total bytes written', req.written_bytes)
    thread_stats_adder('Total time', t)

    with STATS:
      engine_stats_adder('Total bytes read', req.read_bytes)
      engine_stats_adder('Total bytes written', req.written_bytes)
      engine_stats_adder('Total time', t)

      STATS.remove(self.stats_name, 'Requests', hruntime.tid)

  def on_engine_halted(self, _):
    """
    Default hlib handler for C{engine.Halted} event.

    For now, just dump statistics and language coverage data.
    """

    hlib.locks.save_stats('lock_debug-%s.dat' % os.getpid())

  def start(self):
    for s in self.servers:
      s.start()

    self.servers[0].start_console(self.console)

    self.hooks = {
      'system.LogReload': hlib.events.Hook('system.LogReload', self.on_log_reload),
      'system.SystemReload': hlib.events.Hook('system.SystemReload', self.on_system_reload),
      'engine.ThreadStarted': hlib.events.Hook('engine.ThreadStarted', self.on_thread_start),
      'engine.ThreadFinished': hlib.events.Hook('engine.ThreadFinished', self.on_thread_finished),
      'engine.RequestConnected': hlib.events.Hook('engine.RequestConnected', self.on_request_connected),
      'engine.RequestAccepted': hlib.events.Hook('engine.RequestAccepted', self.on_request_accepted),
      'engine.RequestStarted': hlib.events.Hook('engine.RequestStarted', self.on_request_started),
      'engine.RequestFinished': hlib.events.Hook('engine.RequestFinished', self.on_request_finished),
      'engine.RequestClosed': hlib.events.Hook('engine.RequestClosed', self.on_request_closed),
      'engine.Halted': hlib.events.Hook('engine.Halted', self.on_engine_halted)
    }

    self.quit_event.clear()

    hlib.events.trigger('engine.Started', None, engine = self)

    try:
      while True:
        self.quit_event.wait(100)

        if self.quit_event.is_set():
          break

        time.sleep(0) # yield

    except KeyboardInterrupt:
      self.stop()

  def stop(self):
    for server in self.servers:
      server.stop()

    hlib.events.trigger('engine.Halted', None, engine = self)

    for hook in self.hooks.values():
      hook.unregister()

    self.quit_event.set()

import hlib.events.engine  # @UnusedImport
import hlib.events.app     # @UnusedImport
import hlib.events.system  # @UnusedImport
