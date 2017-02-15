import games.stats

class PlayerStats(games.stats.PlayerStats):
    def __init__(self, *args, **kwargs):
        super(PlayerStats, self).__init__(*args, **kwargs)

        self.points = 0
        self.finished_points = 0
        self.games = 0
        self.finished = 0
        self.wons = 0
        self.points_per_game = 0.0
        self.forhont = 0

    def toAPI(self):
        return {
            'user': self.user.toAPI(),
            'pointsInFinished': self.finished_points,
            'games': self.games,
            'finishedGames': self.finished,
            'wonGames': self.wons,
            'pointsPerGame': self.points_per_game,
            'forhont': self.forhont
        }


class SettlersStatistics(games.stats.GameStatistics):
    def get_fresh_stats(self, dbroot):
        players = {}

        def __process_game(g):
            for p in g.players.values():
                username = p.user.name

                try:
                    if username not in players:
                        players[username] = s = PlayerStats(p.user)
                    else:
                        s = players[username]

                except AttributeError:
                    continue

                s.points += p.points
                s.games += 1

                if g.is_finished:
                    s.finished += 1
                    s.finished_points += p.points

                    if g.winner_player == p:
                        s.wons += 1

                elif g.is_canceled or g.is_suspended:
                    pass

                else:
                    if p.id == g.forhont:
                        s.forhont += 1

        oldest_pass = time.time() - (52 * 7 * 24 * 60 * 60)

        for g in dbroot.games.values():
            if g.last_pass < oldest_pass:
                continue

            if g.is_canceled:
                continue

            __process_game(g)

        for g in dbroot.games_archived.values():
            if g.last_pass < oldest_pass:
                continue

            if g.is_canceled:
                continue

            __process_game(g)

        players_to_skip = []

        for username, stats in players.iteritems():
            if stats.finished >= 20:
                continue

            players_to_skip.append(username)

        for username in players_to_skip:
            del players[username]

        return players.values()
