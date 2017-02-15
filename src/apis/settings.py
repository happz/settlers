from . import APIHandler, api, API_SUCCESS, API_FAIL, log, DontCommit
from games import game_module

class SettingsHandler(APIHandler):
    @api('/settings/email', readOnly = False, schema = {
        'email': 'email'
    })
    def handle_settings_email(self, request, dbroot, user = None, email = None):
        user.email = email
        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/settings/after_pass_turn', readOnly = False, schema = {
        'afterPassTurn': {
            'type': 'integer',
            'min': 0,
            'max': 2
        }
    })
    def handle_settings_after_pass_turn(self, request, dbroot, user = None, afterPassTurn = None):
        user.after_pass_turn = afterPassTurn
        request.bus.publish('user.modified', user)

        return API_SUCCESS()

    @api('/settings/per_page', readOnly = False, schema = {
        'perPage': {
            'type': 'integer',
            'min': 10,
            'max': 60
        }
    })
    def handle_settings_per_page(self, request, dbroot, user = None, perPage = None):
        user.table_length = perPage
        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/settings/boardskin', readOnly = False, schema = {
        'skin': {
            'type': 'string',
            'empty': False,
            'regex': '^(real|simple)$'
        }
    })
    def handle_settings_boardskin(self, request, dbroot, user = None, skin = None):
        user.board_skin = skin
        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/settings/password', readOnly = False, schema = {
        'passowrd': {
            'type': 'string',
            'empty': False,
            'minlength': 32,
            'maxlength': 32
        }
    })
    def handle_settings_password(self, request, dbroot, user = None, password = None):
        user.password = password
        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/settings/sound', readOnly = False, schema = {
        'enabled': {
            'type': 'boolean'
        }
    })
    def handle_settings_sound(self, request, dbroot, user = None, enabled = None):
        user.sound = enabled
        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/settings/color', readOnly = False, schema = {
        'game': 'game-kind',
        'color': 'color'
    })
    def handle_settings_color(self, request, dbroot, user = None, game = None, color = None):
        gm = game_module(game)

        if color not in gm.COLOR_SPACE.colors:
            raise DontCommit(API_FAIL('No such color'))

        color = gm.COLOR_SPACE.colors[color]

        if color.name not in gm.COLOR_SPACE.unused_colors(user):
            raise DontCommit(API_FAIL('You can not use this color'))

        user.color(gm.COLOR_SPACE, new_color = color)

        request.bus.publish('user.modified', user)

        return API_SUCCESS()

    @api('/settings/opponent/colors', schema = {
        'game': 'game-kind'
    })
    def handle_settings_opponent_colors(self, request, dbroot, user = None, game = None):
        gm = game_module(kind)

        opponent_colors = user.colors.get(game, {})

        return API_SUCCESS({
            username: opponent_colors[username] for username in opponent_colors.iterkeys() if username != user.name
        })


    @api('/settings/opponent/colors/add', readOnly = False, schema = {
        'game': 'game-kind',
        'opponent': 'username'
    })
    def handle_settings_opponent_colors_add(self, request, dbroot, user = None, game = None, opponent = None):
        if opponent not in dbroot.users:
            raise DontCommit(API_FAIL('No such user'))

        opponent = dbroot.users[opponent]
        gm = game_module(game)

        if color not in gm.COLOR_SPACE.colors:
            raise DontCommit(API_FAIL('No such color'))

        color = gm.COLOR_SPACE.colors[color]

        if opponent == hruntime.user:
            raise DontCommit(API_FAIL('You can not set color for yourself'))

        unused_colors = gm.COLOR_SPACE.unused_colors(user)

        if color.name not in unused_colors:
            raise DontCommit(API_FAIL('You can not use this color'))

        if len(unused_colors) <= 3:
            raise DontCommit(API_FAIL('You have no free colors to use'))

        if game not in user.colors:
            user.colors[game] = hlib.database.StringMapping()

        user.colors[game][opponent.name] = color.name

        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/settings/opponent/colors/remove', readOnly = False, schema = {
        'game': 'game-kind',
        'opponent': 'username'
    })
    def handle_settings_opponent_colors_remove(self, request, dbroot, user = None, game = None, opponent = None):
        if game in user.colors and opponent in user.colors[game]:
            del user.colors[game][opponent]

        request.bus.publish('user.modified', user)

        return API_SUCCESS()
