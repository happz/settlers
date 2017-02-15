import pprint
import sys
import traceback
from twisted.web import server, resource
from twisted.internet import reactor, endpoints, threads, defer
from twisted.web.server import NOT_DONE_YET
from twisted.python.threadpool import ThreadPool
import colorama
import functools

colorama.init()

from twisted.logger import Logger, FileLogObserver, formatEventAsClassicLogText, LogLevelFilterPredicate, LogLevel, FilteringLogObserver
logLevelFilterPredicate = LogLevelFilterPredicate(defaultLogLevel=LogLevel.debug)

def _colorize(fore, s):
    return (fore + s + colorama.Style.RESET_ALL)

_LOG_COLORS = {
    LogLevel.warn:  functools.partial(_colorize, colorama.Fore.RED),
    LogLevel.info: functools.partial(_colorize, colorama.Fore.WHITE),
    LogLevel.debug: functools.partial(_colorize, colorama.Fore.YELLOW)
}
def formatEvent(event):
    s = formatEventAsClassicLogText(event)

    level = event.get("log_level", None)
    if level is not None:
        s = _LOG_COLORS[level](s)

    return s

log = Logger(observer = FilteringLogObserver(observer = FileLogObserver(sys.stdout, formatEvent), predicates = [logLevelFilterPredicate]))

import ZODB.DB
import ZODB.FileStorage
import transaction

from json import dumps, loads
import jwt

import hlib.database
import games
import time
import threading
from collections import deque

from lib.bus import Bus
import lib.datalayer
import lib.mail

class DontCommit(Exception):
    def __init__(self, response):
        super(DontCommit, self).__init__('Do not commit current transaction')

        self.response = response

#
# Input Validation
#
from cerberus import Validator, rules_set_registry

class ValidationError(Exception):
    pass

class ApiValidator(Validator):
    def _validate_isJWT(self, isJWT, field, value):
        """
        {'type': 'boolean'}
        """

        if isJWT and not bool(value):
            self._error(field, "Must be an JWT")

    def _validate_isEmail(self, isEmail, field, value):
        """
        {'type': 'boolean'}
        """

        if isEmail and not bool(value):
            self._error(field, 'Invalid e-mail format')

    # /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

rules_set_registry.add('jwt', {
    'type': 'string',
    'isJWT': True,
    'required': True,
    'empty': False
})
rules_set_registry.add('email', {
    'type': 'string',
    'isEmail': True,
    'required': True,
    'empty': False
})
rules_set_registry.add('username', {
    'type': 'string',
    'minlength': 2,
    'maxlength': 32,
    'required': True
})
rules_set_registry.add('password', {
    'type': 'string',
    'minlength': 2,
    'maxlength': 256,
    'required': True
})
rules_set_registry.add('game-kind', {
    'type': 'string',
    'empty': False,
    'regex': '^settlers$',
    'required': True
})
rules_set_registry.add('color', {
    'type': 'string',
    'empty': False,
    'regex': '^green|dark_green|black|pink|purple|dark_blue|brown|orange|light_blue$',
    'required': True
})


def JWT_encode(user):
    return jwt.encode({'username': user.name}, 'secret', algorithm = 'HS256')

def JWT_decode(encoded):
    return jwt.decode(encoded, 'secret', algorithms=['HS256'])

def API_SUCCESS(response = None):
    response = response or {}
    response['success'] = True

    return response

def API_FAIL(msg):
    return {
      'success': False,
      'error': msg
    }

class APIHandler(object):
    _HANDLERS = {}

    def __init__(self):
        for handler in dir(self):
            if not handler.startswith('handle_'):
                continue

            handler = getattr(self, handler)

            APIHandler._HANDLERS[handler._URI] = handler


class Logging(object):
    def __init__(self, name):
        self._name = name

        self.exitContext()

    def attachTo(self, obj):
        obj.DEBUG = self.DEBUG
        obj.INFO = self.INFO
        obj.WARN = self.WARN
        obj.ERROR = self.ERROR

    def enterContext(self, ctx):
        self._prefix = '[%s #%s]: ' % (self._name, ctx)

    def exitContext(self):
        self._prefix = '[%s]: ' % self._name

    def DEBUG(self, msg):
        return log.debug(self._prefix + msg)

    def INFO(self, msg):
        return log.info(self._prefix + msg)

    def WARN(self, msg):
        return log.warn(self._prefix + msg)

    def ERROR(self, msg):
        return log.error(self._prefix + msg)


class WorkerThread(threading.Thread):
    def __init__(self, name, db, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.daemon = True

        self._log = Logging(name)
        self._log.attachTo(self)

        self._name = name
        self._db = db

        self.quit = False
        self.queue = deque()

    def run(self, *args, **kwargs):
        self.DEBUG('initializing DB connection and root')

        self._dbconn, self._dbroot = self._db.connect()

        while self.quit is not True:
            if not self.queue:
                time.sleep(0)
                continue

            task, args, kwargs, callback = self.queue.popleft()

            result = task(*args, **kwargs)

            if callback is not None:
                callback(result)

    def enqueueTask(self, task, *args, **kwargs):
        d = defer.Deferred()

        def onResult(result):
            reactor.callFromThread(d.callback, result)

        self.queue.append((task, args, kwargs, onResult))

        return d

    def enqueuePriorityTask(self, task, *args, **kwargs):
        self.queue.append((task, args, kwargs, None))

# Decorates API handler's "backend" function - function that gets
# deferred into a worker thread, and returns API response which is
# then written to the request by "frontend" handler machinery.
def api(uri,
        schema = None,
        readOnly = True,
        requiresAuth = True,
        requiresAdmin = False,
        allowInMaintenance = False,
        worker = None):
    def _api(func, *args, **kwargs):
        updated_schema = schema or {}

        if requiresAuth is True or requiresAdmin is True:
            updated_schema['jwt'] = 'jwt'

        validator = ApiValidator(updated_schema) if updated_schema else None

        # This runs in worker thread, in DB context
        def __api(self, request):
            current_thread = threading.current_thread()
            current_thread._log.enterContext(request.requestId)

            db, dbroot = current_thread._db, current_thread._dbroot
            DEBUG, WARN, ERROR = current_thread.DEBUG, current_thread.WARN, current_thread.ERROR

            DEBUG('API request, URI=%s' % request.uri)

            db.start_transaction()

            #db_stats_prev = dict(db._db.cacheDetail())

            ret = None
            user = None
            start = None

            args = (self, request, dbroot)
            kwargs = {}

            try:
                if validator is not None:
                    DEBUG('perform validation')

                    validated = validator.validated(loads(request.content.read()))
                    if validated is None:
                        for field, error in validator.errors.iteritems():
                            WARN('  %s: %s' % (field, error))

                        raise DontCommit(API_FAIL({
                            field: error[0] for field, error in validator.errors.iteritems()
                        }))

                    for k in sorted(validated.iterkeys()):
                        DEBUG('  %s=%s' % (k, validated[k]))

                    kwargs = validated.copy()

                else:
                    DEBUG('no input, no validation')

                    if requiresAdmin is True:
                        ret = API_FAIL('You need admin privileges for this action')

                if 'jwt' in kwargs:
                    jwt = JWT_decode(kwargs['jwt'])
                    del kwargs['jwt']

                    username = jwt['username']
                    if username not in dbroot.users:
                        ret = API_FAIL('Invalid auth token')

                    else:
                        kwargs['user'] = user = dbroot.users[username]

                        user.touch()

                        DEBUG('user=%s' % user.name)

                        if requiresAdmin is True and user.admin is not True:
                            ret = API_FAIL('You need admin privileges for this action')

                if dbroot.server.maintenance_mode is True:
                    DEBUG('maintenance mode enabled')

                    if allowInMaintenance is True:
                        DEBUG('  request allowed in maintenance mode')
                        pass

                    elif user is not None and user.maintenance_access is True:
                        DEBUG('  user is allowed to access server in maintenance mode')
                        pass

                    else:
                        DEBUG('  denied')
                        ret = API_FAIL('Not allowed while server runs in maintenance mode')

                if ret is None:
                    DEBUG('calling the real handler: %s' % func.func_name)
                    start = time.time()
                    ret = func(*args, **kwargs)
                    assert ret is not None

            except DontCommit as e:
                end = time.time()

                DEBUG('rollback requested')

                db.rollback()
                ret = e.response

            except Exception as e:
                end = time.time()

                ERROR(e.message)
                traceback.print_exc()

                db.rollback()
                ret = 'Exception raised: %s' % e.__class__.__name__

            else:
                end = time.time()

                if readOnly is True:
                    DEBUG('read-only request')

                    db.rollback()

                elif ret['success'] is False:
                    DEBUG('failed request')

                    db.rollback()

                else:
                    DEBUG('commit not denied')

                    db.commit()

            if start is not None:
                DEBUG('processing finished: %.4f' % (end - start))

            if user is not None:
                ret.update({
                    'jwt':  JWT_encode(user),
                    'user': user.toAPI(current = True)
                })

            dbStats = db.cacheStats(current_thread._dbconn)
            DEBUG('DB stats: %d non-ghost objects' % dbStats['nonGhostCount'])

            current_thread._log.exitContext()
            return ret

        __api._URI = uri
        __api._worker = worker

        return __api

    return _api

class Handler(resource.Resource):
    isLeaf = True

    def __init__(self, db):
        resource.Resource.__init__(self)

        self._request_id = 0

        self._log = Logging('dispatch')
        self._log.attachTo(self)

        self.db = db
        self.bus = Bus('main-bus', log)
        self.bus.log = log

        self._workers = {}
        for worker_type in ('default', 'game-lists'):
            worker = WorkerThread(worker_type, db)
            worker.start()
            self._workers[worker_type] = worker

        self._dispatch_table = APIHandler._HANDLERS

        self.game_list_cache = games.GameListCache(self.bus, self._workers['game-lists'])

        def onUserRegistered(bus, user = None):
            lib.mail.sendMail(['osadnici@happz.cz', user.email], 'Novy hrac', 'Zaregistroval se novy hrac: %s (%s)' % (user.name, user.email))

        self.bus.subscribe('user.registered', onUserRegistered)

    def availableURIs(self):
        return sorted(self._dispatch_table.keys())

    def render_GET(self, request):
        return self._handleRequest(request)

    def render_POST(self, request):
        return self._handleRequest(request)

    def render_OPTIONS(self, request):
        self._addAPIHeaders(request)
        return ''

    def _addAPIHeaders(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With')
        request.setHeader('Content-Type', 'application/json')

    def _finishRequest(self, response, request):
        self._log.enterContext(request.requestId)

        self.DEBUG('finishing request')

        request.write(dumps(response))
        request.finish()

    def _handleRequest(self, request):
        self._request_id += 1
        request.requestId = self._request_id

        self._log.enterContext(self._request_id)

        self.INFO('URI=%s' % request.uri)

        request.db = self.db
        request.bus = self.bus
        request.handler = self

        self._addAPIHeaders(request)

        try:
            handler = self._dispatch_table[request.uri]

        except KeyError:
            self.WARN('Unhandled URI: uri="%s"' % request.uri)

            self._log.exitContext()
            return dumps(API_FAIL('No such action'))

        def errback(failure):
            import sys
            failure.printTraceback(file = sys.stderr)

            self._finishRequest('', request)

        worker = self._workers['default'] if handler._worker is None else self._workers[handler._worker]

        defer = worker.enqueueTask(handler, request)
        defer.addCallback(self._finishRequest, request)
        defer.addErrback(errback)

        self.DEBUG('handler deferred to a worker thread [%s]' % worker._name)

        self._log.exitContext()
        return NOT_DONE_YET
