import hlib.database
import hlib.error

class Engine(object):
  player_class = None

  def __init__(self, tournament):
    super(Engine, self).__init__()

    self.tournament		= tournament

  def create_groups(self):
    raise hlib.error.UnimplementedError(obj = self)

  def round_finished(self):
    raise hlib.error.UnimplementedError(obj = self)

  def recalculate_all(self):
    raise hlib.error.UnimplementedError(obj = self)

engines = {}
