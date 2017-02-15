__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import ConfigParser
import random
import unittest
import string
import sys
import types
import json
import time

from pprint import pprint

__all__ = [
  'TestCase',
  'T', 'F', 'EQ', 'NEQ', 'NONE', 'ANY', 'JEQ',
  'EX', 'R', 'SKIP', 'Z', 'PAUSE', 'CLASS',
  # Arrays
  'EMPTY', 'NEMPTY', 'LEQ', 'IN', 'NIN',
  # Randoms
  'randint', 'randstr',
  'EventPatcher', 'EventPatcherWithCounter',
  'pprint'
]

def PAUSE(msg, sec):
  print msg.format(delay = str(sec))

  time.sleep(sec)

#
# Basic asserts
#
def T(msg, *actual_values):
  for actual_value in actual_values:
    assert actual_value == True, msg.format(actual = str(actual_value))

def F(msg, *actual_values):
  for actual_value in actual_values:
    assert actual_value == False, msg.format(actual = str(actual_value))

def EQ(msg, expected, *actual_values):
  for actual_value in actual_values:
    assert expected == actual_value, msg.format(expected = str(expected), actual = str(actual_value))

def NEQ(msg, expected, *actual_values):
  for actual_value in actual_values:
    assert expected != actual_value, msg.format(expected = str(expected), actual = str(actual_value))

def Z(msg, *actual_values):
  EQ(msg, 0, *actual_values)

def JEQ(a, b):
  if type(a) in types.StringTypes:
    a = json.loads(a)
  if type(b) in types.StringTypes:
    b = json.loads(b)

  def __check_dict(d1, d2, prefix):
    for k, v1 in d1.items():
      assert k in d2, 'key \'%s%s\' not present' % (prefix, k)

      v2 = d2[k]

      if type(v1) in types.StringTypes and type(v2) in types.StringTypes:
        pass

      else:
        assert type(v1) == type(v2), 'type mismatch for key \'%s\': got %s, expected %s' % (k, type(v2), type(v1))

        if type(v1) == types.DictType:
          __check_dict(v1, v2, prefix + '.' + k + '.')
          continue

      assert v1 == v2, 'reply[%s] = \'%s\', expected \'%s\'' % (k, unicode(v2).encode('ascii', 'replace'), v1)

  __check_dict(a, b, '')
  __check_dict(b, a, '')

def NONE(msg, *actual_values):
  EQ(msg, None, *actual_values)

def ANY(msg, *actual_values):
  NEQ(msg, None, *actual_values)

# Arrays
def LEQ(msg, seq, expected):
  assert len(seq) == expected, msg.format(expected = str(expected), actual = str(len(seq)))

def EMPTY(msg, seq):
  assert len(seq) == 0, msg.format(expected = 0, actual = len(seq))

def NEMPTY(msg, seq):
  assert len(seq) > 0, msg.format(expected = 0, actual = len(seq))

def IN(msg, seq, member):
  assert member in seq, msg.format(member = str(member), seq = str(seq))

def NIN(member, seq):
  assert member not in seq

def EX(exc_cls, fn, *args, **kwargs):
  try:
    fn(*args, **kwargs)
  except exc_cls, e:
    return e
  else:
    assert False

def CLASS(msg, expected, *actual_values):
  for actual_value in actual_values:
    assert expected == actual_value.__class__, msg.format(expected = str(expected), actual = str(actual_value))

from nose.tools import raises as R  # @UnusedImport
from nose.tools import nottest as SKIP  # @UnusedImport

def randint(*limits):
  left  = 0
  right = 100

  if len(limits) == 1:
    right = int(limits[0])
  elif len(limits) == 2:
    left = int(limits[0])
    right = int(limits[1])

  return random.randint(left, right)

def randstr(length = 10):
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def cmp_json_dicts(reply, expect):
  def __check_dict(d1, d2, prefix):
    for k, v1 in d1.iteritems():
      assert k in d2, 'key \'%s.%s\' not present' % (prefix, k)

      v2 = d2[k]

      if type(v1) in types.StringTypes and type(v2) in types.StringTypes:
        pass

      else:
        assert type(v1) == type(v2), 'type mismatch for key \'%s\': got %s, expected %s' % (k, type(v2), type(v1))

        if type(v1) == types.DictType:
          __check_dict(v1, v2, prefix + '.' + k)
          continue

      assert v1 == v2, 'reply[%s] = \'%s\', expected \'%s\'' % (k, unicode(v2).encode('ascii', 'replace'), v1)

  try:
    __check_dict(expect, reply, '')
    __check_dict(reply, expect, '')

  except AssertionError, e:
    print >> sys.stderr, 'JSON reply: \'%s\'' % reply
    raise e

class EventPatcher(object):
  def __init__(self, events, callback = None):
    super(EventPatcher, self).__init__()

    def __fake_call_nop(event):
      pass

    self.events = events or []
    if type(events) in types.StringTypes:
      self.events = [self.events]

    self.callback = callback or __fake_call_nop

  def __enter__(self):
    import hlib.events

    for event_name, hooks in hlib.events._HOOKS.items():
      if event_name not in self.events:
        continue

      for hook in hooks.values():
        hook.saved_callbacks.append(hook.callback)
        hook.callback = self.callback

  def __exit__(self, *args):
    import hlib.events

    for event_name, hooks in hlib.events._HOOKS.items():
      if event_name not in self.events:
        continue

      for hook in hooks.values():
        hook.callback = hook.saved_callbacks.pop()

    return False

class EventPatcherWithCounter(EventPatcher):
  def __init__(self, events):
    def __event_reporter(e):
      self.events_triggered[e.ename()][0] += 1

    super(EventPatcherWithCounter, self).__init__(events.keys(), callback = __event_reporter)

    self.events_triggered = {}

    for event_name, expected_hits in events.items():
      self.events_triggered[event_name] = [0, expected_hits]

  def __exit__(self, *args):
    if not super(EventPatcherWithCounter, self).__exit__(*args):
      return False

    print self.events_triggered
    for event_name, values in self.events_triggered.items():
      EQ(values[1], values[0], msg = 'Event %s triggered {actual} times, {expected} expected' % event_name)

    return False

class DatabaseCache(object):
  _dbs = {}

  def __init__(self, config):
    super(DatabaseCache, self).__init__()

    self.config = config

  def db(self, name, addr):
    import hlib.database
    import os.path

    key = '%s-%s' % (name, addr)
    dbs = self.__class__._dbs

    if key not in dbs:
      addr = hlib.database.DBAddress(addr)
      addr.path = os.path.join(self.config.get('paths', 'tmpdir'), 'databases', addr.path)
      dbs[key] = hlib.database.DB(name, addr)
      dbs[key].set_transaction_logging(enabled = False)

    return dbs[key]

class TestCase(unittest.TestCase):
  @classmethod
  def setup_class(cls):
    pass

  @classmethod
  def teardown_class(cls):
    pass

  def __getattribute__(self, name):
    if name == 'config':
      from testconfig import config
      return config

    return super(TestCase, self).__getattribute__(name)
