import tests.appserver
from tests.web import *

import hlib.database

import random
import string

from nose.tools import make_decorator

def create_simple_game(root):
  from testconfig import config

  root = root['root']

  root.games = hlib.database.IndexedMapping()

  games.create_system_game('settlers', label = None, owner = root.users[config['web']['username']], limit = 3, turn_limit = 604800, opponent1 = 'Dummy User #1', opponent2 = 'Dummy User #2')

def requires_game(creator):
  def _requires_game(fn):
    fn.__requires_game_creator = creator

    def __requires_game(*args, **kwargs):
      cls = args[0]

      cls._appserver.execute_in_db(fn.__requires_game_creator)

      fn(*args, **kwargs)
    __requires_game_page = make_decorator(fn)(__requires_game)
    return __requires_game
  return _requires_game

def requires_game_page(gid):
  def _requires_game_page(fn):
    fn.__requires_game_page = gid or 0

    def __requires_game_page(*args, **kwargs):
      cls = args[0]

      cls.goto(urlparse.urljoin(cls.get_root_url(), '/game?gid=%i#board' % fn.__requires_game_page))

      fn(*args, **kwargs)
    __requires_game_page = make_decorator(fn)(__requires_game_page)
    return __requires_game_page
  return _requires_game_page

class RemainingCardsBadgeTest(WebTestCase):
  @classmethod
  def setup_class(cls):
    super(RemainingCardsBadgeTest, cls).setup_class()

    cls._appserver = tests.appserver.AppServer(*tests.appserver.AppServer.fetch_config('default_appserver'))
    cls._appserver.start()

  @classmethod
  def teardown_class(cls):
    if cls._appserver:
      cls._appserver.stop()

    super(RemainingCardsBadgeTest, cls).teardown_class()

  @requires_login
  @requires_game(create_simple_game)
  @requires_game_page(None)
  def test_remaining_cards_badge(self):
    pass

class TestCase(WebTestCase):
  pass
