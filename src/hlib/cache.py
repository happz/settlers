__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import functools
import sys
import threading

from collections import OrderedDict

import hlib.locks

from hlib.stats import stats as STATS

class Cache(object):
  def __init__(self, name, app):
    super(Cache, self).__init__()

    self.name = name
    self.app = app

    self.lock = hlib.locks.RLock(name = 'Cache')
    self.objects	= {}

    self.stats_name = 'Cache (%s - %s)' % (self.app.name, self.name)

    STATS.set(self.stats_name, OrderedDict([
      ('Total objects', lambda s: sum([len(chain) for chain in self.objects.values()])),
      ('Total chains', lambda s: len(self.objects)),
      ('Total size', lambda s: sum([sum([sys.getsizeof(v) for v in chain.values()]) for chain in self.objects.values()])),
      ('Hits', 0),
      ('Misses', 0),
      ('Inserts', 0),
      ('Chains', lambda s: self.to_stats())
    ]))

  def stats_inc(self, key):
    with STATS:
      STATS.inc(self.stats_name, key)

  def __chain_init(self, user):
    if user.name not in self.objects:
      self.objects[user.name] = {}

    return self.objects[user.name]

  def __check_caching_status(self, key):
    C = self.app.config

    if 'cache.enabled' not in C:
      return False

    if C['cache.enabled'] != True:
      return False

    ck = 'cache.dont_cache.' + key
    if ck not in C:
      return True

    if C[ck] != True:
      return True

    return False

  def get(self, user, key, default = None):
    if not self.__check_caching_status(key):
      return default

    with self.lock:
      chain = self.__chain_init(user)

      if key in chain:
        self.stats_inc('Hits')
      else:
        self.stats_inc('Misses')

      return chain.get(key, default)

  def set(self, user, key, value):
    if not self.__check_caching_status(key):
      return

    with self.lock:
      chain = self.__chain_init(user)

      chain[key] = value

    self.stats_inc('Inserts')

  def test_and_set(self, user, key, callback, *args, **kwargs):
    if not self.__check_caching_status(key):
      return callback(*args, **kwargs)

    with self.lock:
      chain = self.__chain_init(user)

      if key not in chain:
        self.stats_inc('Hits')
        chain[key] = callback(*args, **kwargs)
        self.stats_inc('Inserts')

      else:
        self.stats_inc('Hits')

      return chain[key]

  def remove(self, user, key):
    with self.lock:
      chain = self.__chain_init(user)

      if key in chain:
        del chain[key]

  def remove_for_users(self, users, key):
    with self.lock:
      for user in users:
        chain = self.__chain_init(user)

        if key in chain:
          del chain[key]

  def remove_for_all_users(self, key):
    with self.lock:
      for chain in self.objects.values():
        if key in chain:
          del chain[key]

  def to_stats(self):
    ret = {}

    with self.lock:
      for username, chain in self.objects.items():
        for key, value in chain.items():
          ret[username + ' - ' + key] = {'Type': str(type(value)).replace('<', '').replace('>', ''), 'Size': sys.getsizeof(value)}

    return ret
