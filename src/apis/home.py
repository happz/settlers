from . import APIHandler, API_SUCCESS, api

class HomeHandler(APIHandler):
    @api('/games', worker = 'game-lists')
    def handle_games(self, request, dbroot, user = None):
        response = {
            'active': [],
            'free': [],
            'inactive': []
        }

        for game in request.handler.game_list_cache.active_games(dbroot, user):
            api_data = game.toAPI(user, summary = True)

            if game.has_player(user) and game.my_player(user).is_on_turn or game.has_player(user) and not game.has_confirmed_player(user) or game.has_player(user):
                response['active'].append(api_data)
            else:
                response['free'].append(api_data)

        for game in request.handler.game_list_cache.inactive_games(dbroot, user):
            response['inactive'].append(game.toAPI(user, summary = True))

        return API_SUCCESS(response)


    @api('/games/archived', worker = 'game-lists')
    def handle_games_archived(self, request, dbroot, user = None):
        response = {
            'archived': []
        }

        for game in request.handler.game_list_cache.archived_games(dbroot, user):
            response['archived'].append(game.toAPI(user, summary = True))

        return API_SUCCESS(response)
