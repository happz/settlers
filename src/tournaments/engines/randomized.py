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
      groups.append(tournaments.Group(i / 3, T, T.round, players[i:i + T.game_flags.limit]))

    return groups

  def round_finished(self):
    T = self.tournament

    for group in T.groups:
      for game in group.completed_games:
        players = sorted(game.players.values()[:], key = lambda x: x.points, reverse = True)

        points = T.game_flags.limit
        for i, p in enumerate(players):
          T.players[p.user.name].points += points
          if i == len(players) - 1:
            continue
          if p.points != players[i + 1].points:
            points -= 1

tournaments.engines.engines['randomized'] = Engine
