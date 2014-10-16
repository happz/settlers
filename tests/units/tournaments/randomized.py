import tests.units.tournaments

import lib.datalayer
import games
import games.settlers
import tournaments

import hruntime

from tests import *
from tests.units.tournaments import create_and_populate_tournament

class Tests(TestCase):
  @classmethod
  def setup_class(cls):
    super(Tests, cls).setup_class()

    hruntime.dbroot = lib.datalayer.Root()
    hruntime.dbroot.users['SYSTEM'] = tests.DummyUser('SYSTEM')

  def test_sanity(self):
    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 12,
      'game.GameCreated': 8,
      'game.PlayerJoined': 4,
      'game.PlayerInvited': 8
    }

    with EventPatcherWithCounter(patched_events):
      T = create_and_populate_tournament(engine = 'randomized')
