import hlib.database

class Engine(hlib.database.DBObject):
  player_class = None

  def __init__(self, tournament):
    hlib.database.DBObject.__init__(self)

    self.tournament		= tournament

  def create_groups(self):
    pass

  def rank_players(self, games):
    return None

engines = {}
