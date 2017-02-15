__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import Queue
import time
import threading
import SocketServer
import sys
import traceback
import types

import hlib.console
import hlib.engine
import hlib.error
import hlib.events
import hlib.handlers
import hlib.locks
import hlib.log
import hlib.http

from collections import OrderedDict
from hlib.stats import stats as STATS

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

__all__ = []

class Command_Server(hlib.console.Command):
  def __init__(self, console, parser):
    super(Command_Server, self).__init__(console, parser)

    self.parser.add_argument('--list', '-l', action = 'store_const', dest = 'action', const = 'list')
    self.parser.add_argument('--kill-thread', action = 'store_const', dest = 'action', const = 'kill-thread')
    self.parser.add_argument('--flush-threads', action = 'store_const', dest = 'action', const = 'kill-threads')
    self.parser.add_argument('--info', '-i', action = 'store_const', dest = 'action', const = 'info')
    self.parser.add_argument('--threads', '-t', action = 'store_const', dest = 'action', const = 'threads')

    self.parser.add_argument('--name', action = 'store', dest = 'name')
    self.parser.add_argument('--count', action = 'store', dest = 'count', type = int)
    self.parser.add_argument('--thread', action = 'store', dest = 'thread')

  def __get_server_by_name(self, args):
    if 'name' not in args:
      self.console.err_required_arg('name')

    for server in self.console.engine.servers:
      if server.name == args.name:
        return server

    raise hlib.console.CommandException('Unknown server \'%s\'' % args.name)

  def handler(self, args):
    if args.action == 'list':
      return {'servers': [{'name': s.name} for s in self.console.engine.servers]}

    if args.action == 'flush-threads':
      return self.__get_server_by_name(args).pool.kill_threads(count = (int(args.count) if 'count' in args else None))

    if args.action == 'kill-thread':
      if 'thread' not in args:
        self.console.err_required_arg('thread')

      return self.__get_server_by_name(args).pool.kill_threads(thread_names = [args.thread])

    if args.action == 'info':
      server = self.__get_server_by_name(args)
      pool = server.pool

      return {
        'name': server.name,
        'engine': server.engine.name,
        '# of consoles': len(server.consoles),
        'queue.size': server.request_queue_size,
        'queue.timeout': server.timeout,
        'pool.current': pool.current_count,
        'pool.max': pool.limit,
        'pool.free': pool.free_count,
        'pool.queue': pool.queue.qsize(),
        'address': '%s:%s' % (server.config['host'], str(server.config['port']))
      }

    if args.action == 'threads':
      threads = threading.enumerate()

      return {
        'thread_cnt': len(threads),
        'threads': [
          {
            'name': thread.name,
            'ident': thread.ident,
            'daemon': 'yes' if thread.daemon == True else 'no'
          } for thread in threads
        ]
      }

    return {'args': str(args)}

def ips_to_str(ips):
  return ':'.join([str(ip) for ip in ips])

class MultipartPiece(object):
  def __init__(self):
    super(MultipartPiece, self).__init__()

    self.headers = hlib.engine.HeaderMap()
    self.data = None

class Thread(threading.Thread):
  def __init__(self, pool, name, *args, **kwargs):
    threading.Thread.__init__(self, *args, name = name, **kwargs)

    self.setDaemon(True)
    self.pool = pool

  def work(self):
    pass

  def run(self):
    hlib.events.trigger('engine.ThreadStarted', None, server = self.pool.server, thread = hruntime.service_thread)

    self.work()

    hlib.events.trigger('engine.ThreadFinished', None, server = self, thread = hruntime.service_thread)

class Producer(Thread):
  def __init__(self, *args, **kwargs):
    Thread.__init__(self, *args, **kwargs)

    self.result = None
    self.error = None

  def produce(self):
    pass

  @property
  def failed(self):
    return self.error != None

  def work(self):
    hruntime.clean()
    hruntime.db.start_transaction()

    hruntime.dont_commit = True

    try:
      self.result = self.produce()
    except Exception, e:
      hruntime.dont_commit = True
      self.error = e

    if hruntime.dont_commit != False:
      hruntime.db.rollback()
      return

    if hruntime.db.commit() == True:
      return

    hruntime.db.rollback()

class Worker(Thread):
  def __init__(self, *args, **kwargs):
    Thread.__init__(self, *args, **kwargs)

    self.lru_ips = []

  def work(self):
    POOL = self.pool
    SERVER = POOL.server

    while True:
      # Pick up new request from queue
      request = POOL.get_request()

      # If it's a QUIT request, just break loop
      if request.request_type == ThreadRequest.TYPE_QUIT:
        break

      # Create new request and response wrappers
      hruntime.request = req = hlib.engine.Request(request.request, request.client_address, SERVER)
      hruntime.response = res = hlib.engine.Response()

      # Called from exception cases - reset response, set status and log error if we get any.
      def __fail(status, exc = None):
        if exc:
          traceback.print_exc(file = sys.stderr)

          e = hlib.error.error_from_exception(exc)
          hlib.log.log_error(e)

        res.status = status
        res.output = None

      # Wrap everything into try-catch to catch exceptions raised by faults
      # in our exception handlers
      try:
        # Always check there is break at the end...
        while True:
          hlib.events.trigger('engine.RequestConnected', None)

          # In case of exception from read_data sending out response is probably gonna fail. IO error
          # is most likely to be cause of such exception. But we should try anyway.
          try:
            req.read_data()

          # pylint: disable-msg=W0703
          except Exception, e:
            __fail(500, exc = e)
            break

          # Call parse_data and try to catch all exceptions that may be caused
          # by malformed HTTP input or bad syntax. And lets say it's user's
          # fault, give him HTTP reply code 400.
          try:
            req.parse_data()

          # pylint: disable-msg=W0703
          except hlib.http.NotFound:
            __fail(404)
            break

          except Exception, e:
            __fail(400, exc = e)
            break

          hlib.events.trigger('engine.RequestAccepted', None)

          try:
            req.handler = hruntime.app.get_handler(req.requested)

          except hlib.http.NotFound, e:
            __fail(404)
            break

          try:
            io_regime = hlib.handlers.tag_fn_check(req.handler, 'ioregime', None)

          except Exception, e:
            __fail(500, e)
            break

          try:
            hlib.events.trigger('engine.RequestStarted', None)

            if not io_regime:
              raise hlib.http.UnknownMethod()

            res.output = io_regime.run_handler()

          except hlib.http.Prohibited:
            __fail(403)

          except hlib.http.NotFound:
            __fail(404)

          except hlib.http.UnknownMethod:
            __fail(405)

          except hlib.http.Redirect, e:
            if req.base:
              url = 'http://' + req.base
            else:
              url = ''

            url += e.location

            io_regime.redirect(url)

          except hlib.error.BaseError, e:
            hlib.log.log_error(e)

            res.status = 500

          except Exception, e:
            __fail(500, exc = e)

          # This one is pretty important ;)
          break

        output = res.dumps()

        hlib.events.trigger('engine.RequestFinished', None)

        try:
          request.request.sendall(output)

        # pylint: disable-msg=W0703
        except Exception, e:
          # Just log error, nothing else to do - it's too late
          __fail(0, exc = e)

        else:
          req.written_bytes += len(output)

        hlib.events.trigger('engine.RequestClosed', None)

      # pylint: disable-msg=W0703
      except Exception, e:
        saved_info = sys.exc_info()

        print >> sys.stderr, '----- ----- ----- Raw exception info ----- ----- -----'
        print >> sys.stderr, 'Exc info:', saved_info
        print >> sys.stderr, ''.join(traceback.format_exception(*saved_info))
        print >> sys.stderr, '----- ----- ----- Raw exception info ----- ----- -----'
        e = hlib.error.error_from_exception(e)
        hlib.log.log_error(e)

        SERVER.handle_error(request.request, request.client_address)

      finally:
        SERVER.shutdown_request(request.request)
        POOL.finish_request()

  def run(self):
    Thread.run(self)

    self.pool.remove_thread()

class ThreadRequest(object):
  TYPE_REQUEST = 0
  TYPE_QUIT = 1

  def __init__(self, request_type, thread = None, request = None, client_address = None):
    super(ThreadRequest, self).__init__()

    self.request_type = request_type
    self.thread = thread
    self.request = request
    self.client_address = client_address

  def __repr__(self):
    return 'ThreadRequest(%s, %s, %s, %s)' % (self.request_type, self.thread, self.request, self.client_address)

class ThreadPool(object):
  """
  Represents pool of threads, manages number of running threads and distributes new requests to waiting threads.
  """

  def __init__(self, server, limit = None):
    """
    @type server: L{server.Server}
    @param server: Server this pool belongs to.
    @type limit: C{int}
    @param limit: Maximal number of running threads. Default is C{None} which means "no limit".
    """

    super(ThreadPool, self).__init__()

    self.limit = limit
    self.server = server

    self.lock	= hlib.locks.RLock(name = 'ThreadPool lock')
    self.worker_index = 0
    self.current_count = 0
    self.free_count	= 0
    self.queue = Queue.Queue()

    self.threads = {}
    self.hooks = {}

    self.stats_name	= 'Pool (%s)' % self.server.name

    STATS.set(self.stats_name, OrderedDict([
      ('Queue size', lambda s: self.queue.qsize()),
      ('Current threads', lambda s: self.current_count),
      ('Free threads', lambda s: self.free_count),
      ('Total threads started', 0),
      ('Total threads finished', 0),
      ('Threads', {})
    ]))

  # Event handlers
  def on_thread_start(self, _):
    # Setup hruntime info, and set stats record

    hruntime.service_engine = self.server.engine
    hruntime.service_server = self.server
    hruntime.service_thread = threading.current_thread()
    hruntime.tid = hruntime.service_thread.name

    STATS.set(self.stats_name, 'Threads', hruntime.tid, OrderedDict([
      ('Start time', time.time()),
      ('Uptime', lambda s: time.time() - s['Start time']),
      ('Time per request', lambda s: (float(s['Total time']) / float(s['Total requests'])) if s['Total requests'] > 0 else 0.0)
    ]))

    with STATS:
      STATS.inc(self.stats_name, 'Total threads started')

  def on_thread_finished(self, _):
    # Update stats, nothing else is needed

    with STATS:
      STATS.inc(self.stats_name, 'Total threads finished')

    STATS.remove(self.stats_name, 'Threads', hruntime.tid)

  def on_request_connected(self, _):
    # Update stats, nothing else is needed

    STATS.inc(self.stats_name, 'Threads', hruntime.tid, 'Total requests')

  def add_request(self, request):
    with self.lock:
      if self.free_count == 0 and self.current_count < self.limit:
        self.add_thread()

    self.queue.put(request)

  def get_request(self):
    while True:
      request = self.queue.get()
      self.queue.task_done()

      if request.thread != None and request.thread != hruntime.tid:
        self.add_request(request)
        continue

      break

    with self.lock:
      self.free_count -= 1

    return request

  def finish_request(self):
    """
    Called by threads when request is finished.
    """

    with self.lock:
      self.free_count += 1

  def add_thread(self):
    """
    Starts new worker thread and adds it into pool.
    """

    with self.lock:
      t = Worker(self, 'worker-' + str(self.worker_index + 1))
      t.start()

      self.threads[t.name] = t

      self.worker_index += 1
      self.current_count += 1
      self.free_count += 1

  def remove_thread(self):
    """
    Remove thread from pool.
    """

    with self.lock:
      self.current_count -= 1
      self.free_count -= 1

      del self.threads[hruntime.tid]

  def kill_threads(self, count = None, thread_names = None):
    with self.lock:
      if thread_names == None:
        if count == None or count > self.current_count:
          count = self.current_count

        thread_names = self.threads.keys()
        for _ in range(0, count):
          self.add_request(ThreadRequest(ThreadRequest.TYPE_QUIT, thread = thread_names.pop()))

      else:
        for thread_name in thread_names:
          self.add_request(ThreadRequest(ThreadRequest.TYPE_QUIT, thread = thread_name))

  def start(self):
    self.hooks = {
      'engine.ThreadStarted': hlib.events.Hook('engine.ThreadStarted', self.on_thread_start),
      'engine.ThreadFinished': hlib.events.Hook('engine.ThreadFinished', self.on_thread_finished),
      'engine.RequestConnected': hlib.events.Hook('engine.RequestConnected', self.on_request_connected)
    }

  def stop(self):
    self.kill_threads()

    sleep = True
    while sleep:
      with self.lock:
        if len(self.threads) <= 0:
          sleep = False
          time.sleep(0)

    for hook in self.hooks.values():
      hook.unregister()

class Server(SocketServer.TCPServer):
  """
  This class represents one HTTP server.
  """

  def __init__(self, engine, name, config):
    """
    Instantiate Server object. Setup server properties, prepare sockets, etc... Pass C{args} and C{kwargs} to parenting class, these include server' bind address and port, and request handler class.

    Server does NOT start yet - L{start} method has to be called to really start server.

    @see:			http://docs.python.org/library/socketserver.html#asynchronous-mixins
    """

    self.engine	= engine
    self.name	= name
    self.config	= config
    self.server_thread = None
    self.allow_reuse_address = True

    SocketServer.TCPServer.__init__(self, (config['host'], config['port']), None)

    self.request_queue_size = self.config.get('queue.size', 10)
    self.timeout = self.config.get('queue.timeout', 60)

    self.pool	= ThreadPool(self, limit = self.config.get('queue.workers', 10))
    self.app = config['app']

    self.shutting_down = False

    self.consoles = {}

  @staticmethod
  def default_config():
    return {
      'host': 'localhost',
      'port': 8080,
      'compress': True,
      'queue.size': 10,
      'queue.timeout': 60,
      'queue.workers': 10,
      'app': None
    }

  def process_request(self, request, client_address):
    """
    Called by L{SocketServer} internals for every new request. Its only job is to call server' thread pool's C{add_request} method and create new thread request.

    @type request: L{socket._socketobject}
    @param request: Current request' socket.
    @type client_address: C{tuple}
    @param client_address: Tuple (C{string}, C{int}) of client' IP address, client' IP port.
    """

    if self.shutting_down:
      return

    self.pool.add_request(ThreadRequest(ThreadRequest.TYPE_REQUEST, request = request, client_address = client_address))

  def handle_timeout(self):
    self.pool.kill_threads(count = 1)

  def start_console(self, console):
    t = self.consoles[console.name] = (console, threading.Thread(target = console.cmdloop, name = 'Console thread "%s"' % console.name))
    t[1].daemon = True
    t[1].start()

  def stop_console(self, console):
    self.consoles[console.name][0].stop()
    del self.consoles[console.name]

  def start(self):
    """
    Begin listening on IP port and start accepting requests. Do it in separate (daemon) thread so we can return command to our caller.
    """

    self.pool.start()

    self.server_thread = threading.Thread(target = self.serve_forever, kwargs = {'poll_interval': 5})
    self.server_thread.daemon = True
    self.server_thread.start()

  def stop(self):
    self.shutting_down = True

    for console, _ in self.consoles.values():
      console.stop()

    self.shutdown()
    self.pool.stop()
    self.socket.close()
