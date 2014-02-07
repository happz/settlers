import tests

import games
import games.settlers
import tournaments



def create_and_populate_tournament(name = 'Dummy tournament', desc = 'Dummy description', kind = 'settlers',
                                   owner = None, engine = 'randomized', password = None, num_players = 12,
                                   num_round = 4, limit = 3):

  gm = games.game_module(kind)

  tkwargs = {
    'name': name,
    'desc': desc,
    'kind': kind,
    'owner': owner,
    'engine': engine,
    'password': password,
    'num_players': num_players,
    'num_round': num_round
  }

  tflags = tournaments.TournamentCreationFlags(**tkwargs)
  tflags.owner = 'User #0'
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

  T = tournaments.Tournament.create_tournament(tflags, gflags)

  for i in range(0, num_players):
    u = tests.DummyUser('User #%i' % i)
    T.join_player(tests.DummyUser('User #%i' % i), None)

  return T

class Tests(tests.TestCase):
  def test_sanity(self):
    T = create_and_populate_tournament()

