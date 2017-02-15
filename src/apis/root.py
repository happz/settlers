from . import api, API_SUCCESS, API_FAIL, JWT_encode, APIHandler
from lib.datalayer import User

class RootHandler(APIHandler):
    @api('/site-status', requiresAuth = False, allowInMaintenance = True)
    def handle_site_status(self, request, dbroot):
        return API_SUCCESS({
            'maintenance': dbroot.server.maintenance_mode
        })


    @api('/ping')
    def handle_ping(self, request, dbroot, user = None):
        return API_SUCCESS()


    @api('/login', allowInMaintenance = True, requiresAuth = False, schema = {
            'username': 'username',
            'password': 'password'
        }
    )
    def handle_login(self, request, dbroot, username = None, password = None):
        if username not in dbroot.users:
            return API_FAIL('Invalid username or password')

        user = dbroot.users[username]

        if dbroot.server.maintenance_mode is True and user.maintenance_access is not True:
            return API_FAIL('Not allowed while server runs in maintenance mode')

        if user.password != password:
            return API_FAIL('Invalid username or password')

        request.bus.publish('user.logged-in', user = user)

        return API_SUCCESS({
            'jwt':  JWT_encode(user),
            'user': user.toAPI(current = True)
        })


    @api('/loginas', allowInMaintenance = True, requiresAuth = False, schema = {
             'username': 'username',
             'password': 'password',
             'loginas':  'username'
        })
    def handle_loginas(self, request, dbroot, username = None, password = None, loginas = None):
        if username not in dbroot.users:
            return API_FAIL('Invalid username or password')

        user = dbroot.users[username]

        if user.password != password:
            return API_FAIL('Invalid username or password')

        if loginas not in dbroot.users:
            return API_FAIL('Invalid username or password')

        if user.admin is not True:
            return API_FAIL('You are not administrator')

        loginas = dbroot.users[loginas]

        return API_SUCCESS({
            'jwt': JWT_encode('loginas'),
            'user': loginas.toAPI(current = True)
        })


    @api('/register', readOnly = False, requiresAuth = False, schema = {
        'username': 'username',
        'password': 'password',
        'email':    'email'
    })
    def handle_register(self, request, dbroot, username = None, password = None, email = None):
        if username in dbroot.users:
            return API_FAIL('Username already registered')

        user = User(username, password, email)
        dbroot.users[user.name] = user

        request.bus.publish('user.registered', user = user)

        return API_SUCCESS()


    @api('/recent', worker = 'game-lists')
    def handle_recent(self, request, dbroot, user = None):
        response = {}

        # Free games
        cnt = sum([1 for game in request.handler.game_list_cache.active_games(dbroot, user) if game.is_free and not game.is_personal_free(user)])
        if cnt > 0:
            response['freeGamesCount'] = cnt

        return API_SUCCESS(response)
