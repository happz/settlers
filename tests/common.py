import tests
from tests import TestCase

import lib

import hashlib
import random
import string

class test_UserToPlayerMap(TestCase):
  def setUp(self):
    super(test_UserToPlayerMap, self).setUp()

    username = tests.rand_string()

    self.du = tests.DummyUser(username)
    self.dp = tests.DummyPlayer(self.du)
    self.dg = tests.DummyGame()
    self.dg.players[0] = self.dp
    self.upm = lib.UserToPlayerMap(self.dg)

  def test_contains(self):
    assert self.du in self.upm

  def test_get(self):
    assert self.upm[self.du] == self.dp

class test_pwcrypt(TestCase):
  def test_random(self):
    s = tests.rand_string()
    cs = hashlib.md5(s.encode('ascii', 'replace')).hexdigest()

    assert cs == lib.pwcrypt(s)
