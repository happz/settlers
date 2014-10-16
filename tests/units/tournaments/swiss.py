import tests
import tests.units.tournaments

import lib.datalayer
import games
import games.settlers
import tournaments

import functools

import hruntime

from tests.units.tournaments import create_tournament, create_and_populate_tournament

from tests import *

def print_players(players):
  for p in players:
    print '{:>8} {}'.format(p.user.name, p.summary_stats)
    for rs in p.round_stats:
      print '         {}'.format(rs)

def print_tournament(T):
  print '--------------------------------------------------------'
  print '%i split per %i' % (T.flags.limit, T.game_flags.limit)
  for rid, round in T.rounds.items():
    for group in round:
      for game in group.games:
        print 'round #{:>2}, group #{:>2}, game {}'.format(str(rid), str(group.id), ' - '.join(['{:>8} ({})'.format(p.user.name, p.points) for p in game.players.values()]))
  print '--------------------------------------------------------'

class Tests(tests.TestCase):
  @classmethod
  def setup_class(cls):
    super(Tests, cls).setup_class()

    hruntime.dbroot = lib.datalayer.Root()
    hruntime.dbroot.users['SYSTEM'] = tests.DummyUser('SYSTEM')

  def test_player(self):
    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 1,
    }

    with EventPatcherWithCounter(patched_events):
      T = create_tournament(engine = 'swiss')

      owner_player = T.players['User #0']

      EQ('Swiss engine should have different player class: expected={expected}, actual={actual}',
         tournaments.engines.swiss.Player,
         T.engine.player_class,
         owner_player.__class__)

  def test_player_stats(self):
    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 1,
    }

    with EventPatcherWithCounter(patched_events):
      T = create_tournament(engine = 'swiss')
      owner_player = T.players['User #0']

      EMPTY('No round stats are expected, {actual} found',
            owner_player.round_stats)
      EMPTY('No finished stats are expected, {actual} found',
            owner_player.finished_stats)
      NONE('Last stats should be None, {actual} returned',
           owner_player.last_stats)
      NONE('Summary stats are not set to None but are {actual} instead',
           owner_player._v_summary_stats)
      ANY('Summary stats not returned when Player is asked for, {actual} returned',
          owner_player.summary_stats)
      EQ('Cached instance differs from returned: cached {expected} but {actual} returned',
         owner_player._v_summary_stats, owner_player.summary_stats)
      CLASS('Summary stats have unexpected class {actual}',
            tournaments.engines.swiss.RoundStats,
            owner_player.summary_stats)

      owner_player.start_round_stats()

      NEMPTY('At least one round stats expected, none found',
             owner_player.round_stats)
      EMPTY('No finished stats are expected, {actual} found',
            owner_player.finished_stats)
      EQ('Last stats are not the same as existing round stats: {expected} vs {actual}',
         owner_player.round_stats[0], owner_player.last_stats)

      wps = owner_player.last_stats.winning_points = randint()

      EQ('Change of last stats did not appear in actual round stats, {expected} expected but {actual} found',
         owner_player.last_stats.winning_points,
         owner_player.round_stats[0].winning_points)

      owner_player.reset_summary_stats()
      owner_player.last_stats.finished = True

      NONE('Summary stats are not set to None but are {actual} instead',
           owner_player._v_summary_stats)
      ANY('Summary stats not returned when Player is asked for, {actual} returned',
          owner_player.summary_stats)
      EQ('Cached instance differs from returned: cached {expected} but {actual} returned',
         owner_player._v_summary_stats, owner_player.summary_stats)
      LEQ('One finished stats expected, {actual} found',
          owner_player.finished_stats,
          1)
      EQ('Summary stats dont reflect round stats, WPS expected to be {expected} but {actual} found',
         owner_player.last_stats.winning_points,
         owner_player.summary_stats.winning_points)

  def test_sanity(self):
    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 12,
      'game.GameCreated':   8,
      'game.PlayerJoined':  4,
      'game.PlayerInvited': 8
    }

    with EventPatcherWithCounter(patched_events):
      create_and_populate_tournament(engine = 'swiss')

  def __test_bye_players(self, num_players, limit):
    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 10,
      'game.GameCreated': 6,
      'game.PlayerJoined': 3,
      'game.PlayerInvited': 7
    }

    with EventPatcherWithCounter(patched_events):
      T = create_and_populate_tournament(engine = 'swiss', num_players = num_players, limit = limit)
      print_tournament(T)

  def test_bye_players_16_4(self):
    self.__test_bye_players(16, 4)

  def test_bye_players_15_4(self):
    self.__test_bye_players(15, 4)

  def test_bye_players_14_4(self):
    self.__test_bye_players(14, 4)

  def test_bye_players_13_4(self):
    self.__test_bye_players(13, 4)

  def __test_real_tournament(self, num_players):
    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': num_players,
      'tournament.Finished': 1,
      'game.GameCreated': 48,
      'game.PlayerJoined': 24,
      'game.PlayerInvited': 68
    }

    def __inject_results():
      for group in T.current_round:
        G = group.games[0]
        winner = randint(len(G.players) - 1)

        for i in range(0, len(G.players)):
          p = G.players[i]
          if i == winner:
            p.points = 10
            G.forhont = i
          else:
            p.points = randint(2, 9)

        G.type = games.Game.TYPE_FINISHED

    print

    with EventPatcherWithCounter(patched_events):
      T = create_and_populate_tournament(engine = 'swiss', num_players = num_players, limit = 4)

      while T.stage != tournaments.Tournament.STAGE_FINISHED:
        __inject_results()

        T.next_round()
        print_tournament(T)
        print_players(T.engine.sort_players(T.players.values()[:]))

      EQ('Tournament round is {actual} instead of {expected}',
         4, T.round)
      EQ('Tournament stage is {actual} instead of {expected}',
         tournaments.Tournament.STAGE_FINISHED, T.stage)

  def test_real_tournament_48(self):
    self.__test_real_tournament(48)

  def test_real_tournament_47(self):
    self.__test_real_tournament(47)

  def test_real_tournament_46(self):
    self.__test_real_tournament(46)

  def test_real_tournament_45(self):
    self.__test_real_tournament(45)

  def test_real_tournament_44(self):
    self.__test_real_tournament(44)

  @SKIP
  def test_real_tournament_compare(self):
    real_results = [
      [
        {
          'Eva Norkov': 7,
          'Richard Janosk': 7,
          'Marie Janduskov': 10,
        },
        {
          'Vclav Soukup': 5,
          'Petra Hlavckov': 10,
          'Toms Kos': 5,
        },
        {
          'Jan Heller': 6,
          'Milan Norek': 10,
          'Ondrej Matrka': 7,
          'Mla Belsk': 7,
        },
        {
          'Milan Voshlo': 6,
          'Martin Kuk': 5,
          'Radek Cibulka': 5,
          'Vera Hellerov': 10,
        },
        {
          'Petr Chalupa': 6,
          'Toms Hlavc_': 6,
          'Jitka Plesniv': 9,
          'Stanislav Hlavat': 10,
        },
        {
          'Milos Cerovsk': 10,
          'Hana Micicov': 6,
          'Honza Klimes': 5,
          'Petr Micica': 8,
        },
        {
          'Jan Malina': 6,
          'Michal Malina': 10,
          'Jakub Vantko': 9,
          'Luks Jandusk': 9,
        },
        {
          'Monika Vantkov-Bendov': 6,
          'Simona Rehkov': 4,
          'Jir Hlavcek': 10,
          'Martin Telka': 4,
        },
        {
          'Petr Pelikn': 5,
          'Jindra Semlerov': 5,
          'Marek Zstera': 10,
          'Zbynek Filipi': 8,
        },
        {
          'Pavel Semler': 10,
          'Kristna Mkov': 6,
          'Mojmr Krejcha': 4,
          'Radek Perlovsk': 5,
        },
        {
          'Petr Koubovsk': 9,
          'Jakub Murn': 7,
          'Matej Siska': 5,
          'Martina Trmotov': 10,
        },
        {
          'Dana Belsk': 8,
          'Vclav Hammerbauer': 10,
          'Vclav Hach': 6,
          'Martin Plesniv': 7,
        }
      ],
      [
        {
          'Eva Norkov': 9,
          'Monika Vantkov-Bendov': 7,
          'Vclav Hammerbauer': 10,
        },
        {
          'Vera Hellerov': 6,
          'Luks Jandusk': 10,
          'Jindra Semlerov': 5,
        },
        {
          'Jan Heller': 9,
          'Jan Malina': 6,
          'Dana Belsk': 10,
          'Marie Janduskov': 7,
        },
        {
          'Milan Voshlo': 5,
          'Petr Pelikn': 7,
          'Mojmr Krejcha': 10,
          'Martina Trmotov': 9,
        },
        {
          'Milan Norek': 6,
          'Petr Micica': 10,
          'Petr Koubovsk': 4,
          'Martin Plesniv': 6,
        },
        {
          'Ondrej Matrka': 6,
          'Milos Cerovsk': 10,
          'Kristna Mkov': 9,
          'Jakub Murn': 9,
        },
        {
          'Martin Kuk': 6,
          'Michal Malina': 7,
          'Matej Siska': 10,
          'Vclav Soukup': 5,
        },
        {
          'Petr Chalupa': 9,
          'Simona Rehkov': 8,
          'Pavel Semler': 10,
          'Zbynek Filipi': 6,
        },
        {
          'Mla Belsk': 10,
          'Jakub Vantko': 8,
          'Marek Zstera': 5,
          'Radek Perlovsk': 5,
        },
        {
          'Radek Cibulka': 8,
          'Stanislav Hlavat': 10,
          'Vclav Hach': 4,
          'Toms Kos': 6,
        },
        {
          'Toms Hlavc_': 8,
          'Hana Micicov': 8,
          'Jir Hlavcek': 10,
          'Richard Janosk': 5,
        },
        {
          'Jitka Plesniv': 6,
          'Honza Klimes': 7,
          'Martin Telka': 4,
          'Petra Hlavckov': 10,
        },
      ],
      [
        {
          'Eva Norkov': 7,
          'Mojmr Krejcha': 7,
          'Matej Siska': 10,
          'Toms Kos': 4,
        },
        {
          'Jan Heller': 10,
          'Toms Hlavc_': 4,
          'Jakub Murn': 7,
          'Martin Plesniv': 4,
        },
        {
          'Milan Voshlo': 5,
          'Jan Malina': 9,
          'Zbynek Filipi': 10,
        },
        {
          'Milan Norek': 5,
          'Marek Zstera': 10,
          'Martina Trmotov': 6,
          'Marie Janduskov': 9,
        },
        {
          'Ondrej Matrka': 10,
          'Jindra Semlerov': 6,
          'Radek Perlovsk': 8,
          'Richard Janosk': 8,
        },
        {
          'Martin Kuk': 7,
          'Honza Klimes': 4,
          'Simona Rehkov': 10,
          'Petr Pelikn': 4,
        },
        {
          'Petr Chalupa': 5,
          'Jakub Vantko': 10,
          'Kristna Mkov': 6,
          'Petr Koubovsk': 5,
        },
        {
          'Mla Belsk': 8,
          'Milos Cerovsk': 3,
          'Luks Jandusk': 10,
          'Petra Hlavckov': 4,
        },
        {
          'Radek Cibulka': 7,
          'Jitka Plesniv': 7,
          'Hana Micicov': 3,
          'Monika Vantkov-Bendov': 10,
        },
        {
          'Vera Hellerov': 7,
          'Michal Malina': 8,
          'Petr Micica': 10,
          'Dana Belsk': 6,
        },
        {
          'Stanislav Hlavat': 8,
          'Jir Hlavcek': 10,
          'Pavel Semler': 6,
          'Vclav Hammerbauer': 8,
        },
        {
          'Martin Telka': 9,
          'Vclav Soukup': 7,
          'Vclav Hach': 10,
        },
      ],
      [
        {
          'Eva Norkov': 5,
          'Ondrej Matrka': 7,
          'Dana Belsk': 8,
          'Martina Trmotov': 10,
        },
        {
          'Jan Heller': 8,
          'Vera Hellerov': 10,
          'Simona Rehkov': 4,
          'Mojmr Krejcha': 7,
        },
        {
          'Milan Voshlo': 7,
          'Hana Micicov': 7,
          'Vclav Soukup': 10,
          'Martin Plesniv': 7,
        },
        {
          'Milan Norek': 6,
          'Jitka Plesniv': 8,
          'Zbynek Filipi': 7,
          'Vclav Hach': 10,
        },
        {
          'Martin Kuk': 10,
          'Toms Hlavc_': 7,
          'Jindra Semlerov': 9,
          'Toms Kos': 7,
        },
        {
          'Petr Chalupa': 6,
          'Radek Cibulka': 4,
          'Jakub Murn': 7,
          'Richard Janosk': 10,
        },
        {
          'Mla Belsk': 8,
          'Monika Vantkov-Bendov': 10,
          'Kristna Mkov': 3,
          'Marie Janduskov': 7,
        },
        {
          'Milos Cerovsk': 7,
          'Michal Malina': 10,
          'Pavel Semler': 8,
          'Marek Zstera': 7,
        },
        {
          'Jan Malina': 10,
          'Honza Klimes': 7,
          'Radek Perlovsk': 7,
        },
        {
          'Stanislav Hlavat': 8,
          'Jakub Vantko': 10,
          'Matej Siska': 7,
          'Petra Hlavckov': 8,
        },
        {
          'Petr Micica': 7,
          'Luks Jandusk': 6,
          'Jir Hlavcek': 10,
          'Vclav Hammerbauer': 5,
        },
        {
          'Petr Pelikn': 10,
          'Martin Telka': 6,
          'Petr Koubovsk': 8,
        },
      ],
    ]

    def __inject_results():
      for i in range(0, len(real_results[T.round - 1])):
        group = T.current_round[i]
        real_group = real_results[T.round - 1][i]

        # Set points
        for real_name, real_result in real_group.items():
          for p in group.games[0].players.values():
            if p.user.name == real_name:
              p.points = real_result

        # Set winner
        forhont_name = None
        forhont_result = 0
        for real_name, real_result in real_group.items():
          if real_result > forhont_result:
            forhont_name = real_name
            forhont_result = real_result

        for i in range(0, len(group.games[0].players)):
          if group.games[0].players[i].user.name == forhont_name:
            group.games[0].forhont = i
            break

        # Finish game
        group.games[0].type = games.Game.TYPE_FINISHED

    def __compare_roster():
      digests = []
      real_digests = []

      for i in range(0, len(T.current_round)):
        player_names = [p.user.name for p in T.current_round[i].games[0].players.values()]
        digests.append('-'.join(sorted(player_names)))

      for i in range(0, len(real_results[T.round - 1])):
        real_digests.append('-'.join(sorted(real_results[T.round - 1][i].keys())))

      for digest in digests:
        IN('Digest {member} is not present in real digests {seq}', real_digests, digest)

      for digest in real_digests:
        IN('Real digest {member} is not present in digests {seq}', digests, digest)

    patched_events = {
      'tournament.Created': 2,
      'tournament.PlayerJoined': 46,
      'game.GameCreated': 48,
      'game.PlayerJoined': 24,
      'game.PlayerInvited': 68
    }

    with EventPatcherWithCounter(patched_events):
      T = create_and_populate_tournament(engine = 'swiss', num_players = 46, limit = 4)                                                                                                                          

      # Rename players in real results to match their instances in tournament
      real_name_map = {}

      for i in range(0, len(real_results[0])):
        group = T.rounds[1][i]
        real_group = real_results[0][i]

        j = 0
        for real_name, real_result in real_group.items():
          real_name_map[group.games[0].players[j].user.name] = real_name
          j += 1

      for p in T.players.values():
        p.user.rename(hruntime.dbroot.users, real_name_map[p.user.name])

      __compare_roster()
      __inject_results()

      # 2nd round
      T.next_round()
      __compare_roster()
      __inject_results()

      # 3rd round
      T.next_round()
      #__compare_roster()
      __inject_results()

      # 4th round
      T.next_round()
      #__compare_roster()
      __inject_results()

      # last shift
      T.next_round()
