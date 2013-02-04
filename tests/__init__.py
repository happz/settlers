from hlib.tests import *

class DummyUser(object):
  def __init__(self, name):
    super(DummyUser, self).__init__()

    self.name = name

class DummyPlayer(object):
  def __init__(self, user):
    super(DummyPlayer, self).__init__()

    self.user = user

class DummyGame(object):
  def __init__(self):
    super(DummyGame, self).__init__()

    self.players = {}
