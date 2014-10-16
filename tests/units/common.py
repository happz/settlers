import lib

import hashlib
import random
import string

from tests import *

class test_UserToPlayerMap(TestCase):
  def setUp(self):
    super(test_UserToPlayerMap, self).setUp()

    username = randstr()

    self.du = DummyUser(username)
    self.dp = DummyPlayer(self.du)
    self.dg = DummyGame()
    self.dg.players[0] = self.dp
    self.upm = lib.UserToPlayerMap(self.dg)

  def test_contains(self):
    IN('Main user is not in map', self.upm, self.du)

  def test_get(self):
    EQ('Player does not match map result', self.upm[self.du], self.dp)

class test_pwcrypt(TestCase):
  def test_random(self):
    s = randstr()
    cs = hashlib.md5(s.encode('ascii', 'replace')).hexdigest()

    EQ('Hash {actual} does not match raw library value {expected}',
       cs,
       lib.pwcrypt(s))
