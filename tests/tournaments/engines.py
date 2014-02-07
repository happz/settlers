import tests
import tests.tournaments

import tournaments

class Tests(tests.TestCase):
  def test_engine_create_groups(self):
    for engine in tournaments.engines.engines.keys():
      T = tests.tournaments.create_and_populate_tournament(engine = engine)
