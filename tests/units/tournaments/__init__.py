import lib.datalayer
import games
import games.settlers
import tournaments

import hruntime

from tests import *

def create_tournament(name = 'Dummy tournament', desc = 'Dummy description',
                      kind = 'settlers', owner = None, engine = 'randomized',
                      password = None, num_players = 12, limit_rounds = 4,
                      limit = 3):
  gm = games.game_module(kind)

  tkwargs = {
    'name': name,
    'desc': desc,
    'kind': kind,
    'owner': owner,
    'engine': engine,
    'password': password,
    'num_players': num_players,
    'limit_rounds': limit_rounds
  }

  tflags = tournaments.TournamentCreationFlags(**tkwargs)
  tflags.owner = hruntime.dbroot.users['User #0'] = DummyUser('User #0')
  tflags.limit = num_players

  gkwargs = {
    'kind': kind,
    'limit': limit
  }

  gflags = gm.GameCreationFlags(**gkwargs)
  gflags.opponents = []
  gflags.desc = ''
  gflags.password = None
  gflags.owner = None

  return tournaments.Tournament.create_tournament(tflags, gflags)

def create_and_populate_tournament(**kwargs):
  T = create_tournament(**kwargs)

  for i in range(1, kwargs.get('num_players', 12)):
    u = hruntime.dbroot.users['User #%i' % i] = DummyUser('User #%i' % i)
    T.join_player(u, None)

  return T

class Tests(TestCase):
  def test_sanity(self):
    hruntime.dbroot = lib.datalayer.Root()
    hruntime.dbroot.users['SYSTEM'] = DummyUser('SYSTEM')

    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 12,
      'game.GameCreated': 8,
      'game.PlayerJoined': 4,
      'game.PlayerInvited': 8
    }

    with EventPatcherWithCounter(patched_events):
      T = create_and_populate_tournament()
