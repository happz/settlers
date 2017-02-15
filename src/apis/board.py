from . import api, API_SUCCESS, APIHandler
import time
from lib import dictUpdate
from lib.chat import add_post

class BoardHandler(APIHandler):
    @api('/board', schema = {
        'start': {
            'type': 'integer',
            'required': True
        },
        'length': {
            'type': 'integer',
            'required': True
        }
    })
    def handle_board(self, request, dbroot, user = None, start = None, length = None):
        posts = dbroot.server.chat_posts.get_posts(start, length)

        user.last_board = max(user.last_board, posts[-1].id)

        return API_SUCCESS({
            'posts': [
                dictUpdate(post.toAPI().copy(), {
                    'isRead': post.id <= user.last_board
                }) for post in reversed(posts)
            ]
        })


    @api('/board/add', readOnly = False, schema = {
        'text': {
            'type': 'string',
            'required': True,
            'empty': False
        }
    })
    def handle_board_add(self, request, dbroot, user = None, text = None):
        add_post(request.bus, dbroot.server, user, time.time(), text)

        return API_SUCCESS()
