__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import random

import hlib.database

import lib.datalayer
import tournaments.engines

__all__ = []

class Player(tournaments.Player):
  FIELDS = ['winning_points', 'success', 'points', 'place_1', 'place_2', 'place_3']

  def __init__(self, tournament, user):
    tournaments.Player.__init__(self, tournament, user)

    for field in Player.FIELDS:
      setattr(self, field, 0.0)
      setattr(self, 'curr_' + field, 0.0)

    self.rand = 0.0

  def reset_current(self):
    for field in self.FIELDS:
      setattr(self, 'curr_' + field, 0.0)

    self.rand = random.randrange(0, 1000000)

  def save_current(self):
    for field in Player.FIELDS:
      setattr(self, field, getattr(self, field) + getattr(self, 'curr_' + field))

    # pylint: disable-msg=E1101
    self.success /= 2.0

  def __str__(self):
    # pylint: disable-msg=E1101
    return '%i:\t%.2f\t%.2f\t%i\t%i\t%i\t%i' % (self.user.id, self.winning_points, self.success, self.points, self.place_1, self.place_2, self.place_3)

def __sort_players(a, b):
  if a.winning_points > b.winning_points:
    return 1

  if b.winning_points > a.winning_points:
    return -1

  if a.success > b.success:
    return 1
  if b.success > a.success:
    return -1

  if a.points > b.points:
    return 1
  if b.points > a.points:
    return -1

  if a.place_1 > b.place_1:
    return 1
  if b.place_1 > a.place_1:
    return -1

  if a.place_2 > b.place_2:
    return 1
  if b.place_2 > a.place_2:
    return -1

  if a.place_3 > b.place_3:
    return 1
  if b.place_3 > a.place_3:
    return -1

  if a.rand > b.rand:
    return 1
  if b.rand > a.rand:
    return -1

  return 0

def sort_players(players):
  return sorted(players, cmp = __sort_players, reverse = True)

class Engine(tournaments.engines.Engine):
  player_class = Player

  def randomize_players(self):
    for p in self.tournament.players.values():
      p.rand = random.randrange(0, 1000000)

  def create_groups(self):
    t = self.tournament

    # refresh random marks on players
    self.randomize_players()

    groups = hlib.database.SimpleList()

    players = sort_players(t.players.values())

    for i in range(0, t.num_players / t.flags.limit):
      group_players = hlib.database.SimpleList()

      for j in range(0, t.flags.limit):
        group_players.append(players[i * t.flags.limit + j])

      group = tournaments.Group(i, t, t.round, group_players)
      groups.append(group)

    return groups

  def rate_game(self, g):
    up = self.tournament.user_to_player

    ## winning points
    players = sorted([p for p in g.players.values() if p != g.forhont_player], key = lambda x: x.points)
    points = [p.points for p in players]

    up[g.forhont_player.user].curr_winning_points = 4.0

    if points[0] == points[1]:
      if g.limit == 4:
        if points[1] == points[2]:
          up[players[0].user].curr_winning_points = 2.0
          up[players[1].user].curr_winning_points = 2.0
          up[players[2].user].curr_winning_points = 2.0
          ##

        else:
          up[players[0].user].curr_winning_points = 3.0
          up[players[1].user].curr_winning_points = 2.0
          up[players[2].user].curr_winning_points = 1.0
          ##

      else:
        up[players[0].user].curr_winning_points = 2.5
        up[players[1].user].curr_winning_points = 2.5
        ##

    else:
      up[players[0].user].curr_winning_points = 3.0

      if g.limit == 4:
        if points[1] == points[2]:
          up[players[1].user].curr_winning_points = 1.5
          up[players[2].user].curr_winning_points = 1.5
          ##

        else:
          up[players[1].user].curr_winning_points = 2.0
          up[players[2].user].curr_winning_points = 1.0
          ##

      else:
        up[players[2].user].curr_winning_points = 2.0

    ## success rate
    sum_points = float(sum([p.points for p in g.players.values()]))
    for p in g.players.values():
      up[p.user].curr_success = float(p.points) / sum_points

    ## points
    for p in g.players.values():
      up[p.user].curr_points = p.points

    ## places
    players = [g.forhont_player] + sorted([p for p in g.players.values() if p != g.forhont_player], key = lambda x: x.points)
    up[players[0].user].curr_place_1 = 1
    up[players[1].user].curr_place_2 = 1
    up[players[2].user].curr_place_3 = 1

  def rate_group(self, group):
    t = self.tournament

    for game in group.games.values():
      for player in game.players.values():
        t.user_to_player[player.user].reset_current()

      self.rate_game(game)
      for player in game.players.values():
        t.user_to_player[player.user].save_current()

tournaments.engines.engines['swiss'] = Engine
