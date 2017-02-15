"""
System statistics
"""

__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import sys
import threading
import types

from collections import OrderedDict

import hlib.error
import hlib.locks

import hruntime

class StatsDict(OrderedDict):
  def __init__(self, *args, **kwargs):
    OrderedDict.__init__(self, *args, **kwargs)

    self.lock = hlib.locks.RLock(name = 'Stats')

  def __get_last_dict(self, *keys):
    with self.lock:
      d = self
      for k in keys[0:-1]:
        d = d[k]

      return d

  def get(self, *keys):
    return self.__get_last_dict(*keys)[keys[-1]]

  def inc(self, *keys):
    self.__get_last_dict(*keys)[keys[-1]] += 1

  def add(self, *args):
    keys = args[0:-1]
    value = args[-1]

    self.__get_last_dict(*keys)[keys[-1]] += value

  def set(self, *args):
    keys = args[0:-1]
    value = args[-1]

    self.__get_last_dict(*keys)[keys[-1]] = value

  def remove(self, *keys):
    del self.__get_last_dict(*keys)[keys[-1]]
        
  def swap(self, *args):
    keys = args[0:-1]
    value = args[-1]

    d = self.__get_last_dict(*keys)
    old_data = d[keys[-1]]
    d[keys[-1]] = value
    return old_data

  def snapshot(self, d_in = None):
    if d_in == None:
      d_in = self

    d_out = OrderedDict()

    for k, v in list(d_in.items()):
      if k == '__fmt__':
        pass

      elif isinstance(v, dict):
        v = self.snapshot(d_in = v)

      elif isinstance(v, (list, tuple)):
        v = [self.snapshot(d_in = r) for r in v]

      elif hasattr(v, '__call__'):
        v = v(d_in)

      d_out[k] = v

    return d_out

  def __enter__(self):
    self.lock.acquire()
    return self

  def __exit__(self, *args):
    self.lock.release()
    return False

stats = StatsDict()

stats_fmt = {
  'Engine':			{
    'Start time':		'%i',
    'Current time':		'%i',
  }
}

def iter_collection(collection):
  if isinstance(collection, dict):
    keys = collection.keys()
  else:
    keys = range(0, len(collection))

  for k in keys:
    d = {'ID': k}
    d.update(collection[k])
    yield d
