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

  def __evaluate_round(self, groups):
    T = self.tournament

    for group in groups:
      for game in group.completed_games:
        players = sorted(game.players.values()[:], key = lambda x: x.points, reverse = True)

        T.players[players[0].user.name].wins += 1

        points = T.game_flags.limit
        for i, p in enumerate(players):
          T.players[p.user.name].points += points
          if i == len(players) - 1:
            continue
          if p.points != players[i + 1].points:
            points -= 1

  def __evaluate_finals(self):
    T = self.tournament

    def __winner_sorter(x, y):
      if x.points < y.points:
        return -1
      if x.points > y.points:
        return 1
      if x.wins < y.wins:
        return -1
      if x.wins > y.wins:
        return 1
      return 0

    players = sorted(T.players.values()[:], cmp = __winner_sorter, reverse = True)
    T.winner_player = players[0]

  def round_finished(self):
    T = self.tournament

    self.__evaluate_round(T.current_round)

    if T.round == T.flags.limit_rounds:
      self.__evaluate_finals()

  def recalculate_all(self):
    T = self.tournament

    for p in T.players.values():
      p.points = p.wins = 0

    for groups in T.rounds.values():
      self.__evaluate_round(groups)

    self.__evaluate_finals()

tournaments.engines.engines['randomized'] = Engine
