import hlib.database
import hlib.error

class Engine(object):
  player_class = None

  def __init__(self, tournament):
    super(Engine, self).__init__()

    self.tournament		= tournament

  def create_groups(self):
    raise hlib.error.UnimplementedError(Engine)

  def round_finished(self):
    raise hlib.error.UnimplementedError(Engine)

engines = {}