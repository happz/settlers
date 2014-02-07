__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2014, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import random

import tournaments.engines

class Engine(tournaments.engines.Engine):
  player_class = tournaments.Player

  def create_groups(self):
    T = self.tournament
    players = [p for p in T.players.values()]
    groups = []

    random.shuffle(players)

    for i in range(0, len(players), T.game_flags.limit):
      groups.append(tournaments.Group(i, T, T.round, players[i:i + T.game_flags.limit]))

    return groups

  def rank_players(self):
    pass

tournaments.engines.engines['randomized'] = Engine
