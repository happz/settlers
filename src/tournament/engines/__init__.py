class PlayerRanking(object):
  def __init__(self, user, record):
    super(PlayerRanking, self).__init__()

    self.record = record
    self.user = user

class TournamentEngine(object):
  def __init__(self, tournament):
    super(TournamentEngine, self).__init__()

    self.tournament = tournament

  def prebegin(self):
    pass

  def create_games(self):
    return []

  def rank_players(self, games):
    return None
