import threading
import hlib.error

class GamesStats(object):
  @staticmethod
  def items(key = None, reverse = False, window = None):
    # pylint: disable-msg=W0613
    raise hlib.error.UnimplementedError(obj = GamesStats)

  @staticmethod
  def refresh_stats():
    raise hlib.error.UnimplementedError(obj = GamesStats)
