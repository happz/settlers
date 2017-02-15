import os
import tabulate
import threading
import time

if __name__ == '__main__':
  import hlib.runtime

import hruntime

__original_Lock = threading.Lock
__original_RLock = threading.RLock

LOCK_LIST = []

class LockStats(object):
  def __init__(self, name, klass, calls):
    super(LockStats, self).__init__()

    self.name = name
    self.klass = klass
    self.calls = calls

class LockWrapper(object):
  def __init__(self, lock_class, name = None, *args, **kwargs):
    super(LockWrapper, self).__init__()

    self._lock = lock_class(*args, **kwargs)

    self.name = name if name else self._lock.__class__.__name__
    self.calls = []

    global LOCK_LIST
    LOCK_LIST.append(self)

  def acquire(self, *args, **kwargs):
    s = time.time()
    try:
      return self._lock.acquire(*args, **kwargs)
    finally:
      self.calls.append((True, s, time.time(), hruntime.tid))

  __enter__ = acquire

  def release(self, *args, **kwargs):
    s = time.time()
    try:
      return self._lock.release(*args, **kwargs)
    finally:
      self.calls.append((False, s, time.time(), hruntime.tid))

  def __exit__(self, t, v, tb):
    self.release()

  def get_stats(self):
    return LockStats(self.name, self._lock.__class__.__name__, self.calls)

if os.environ.get('DEBUG_LOCKS', False):
  def _Lock(*args, **kwargs):
    return LockWrapper(__original_Lock, *args, **kwargs)

  def _RLock(*args, **kwargs):
    return LockWrapper(__original_RLock, *args, **kwargs)

else:
  def _Lock(name = None, *args, **kwargs):
    return __original_Lock(*args, **kwargs)

  def _RLock(name = None, *args, **kwargs):
    return __original_RLock(*args, **kwargs)

Lock = _Lock
RLock = _RLock

def show_stats():
  print 'Locks stats'

  for lock in LOCK_LIST:
    print 'Lock: %s - %s calls' % (lock.name, len(lock.calls))

def save_stats(file_path):
  print 'Save lock stats'

  import pickle

  stats = []

  for lock in LOCK_LIST:
    stats.append(lock.get_stats())
    print 'Lock: %s - %s calls' % (lock.name, len(lock.calls))

  with open(file_path, 'w') as f:
    pickle.dump(stats, f)

def load_stats(file_path):
  import pickle

  with open(file_path, 'r') as f:
    return pickle.load(f)

def print_stats(lock):
  starts = []

  time_acquire = 0.0
  time_release = 0.0
  lock_hold = 0.0
  acquire_calls = 0
  release_calls = 0

  threads = {}

  for call in lock.calls:
    if call[3] not in threads:
      threads[call[3]] = {
        'Acquired': 0,
        'Released': 0,
        'Hold': 0.0,
        'Acquired time': 0.0,
        'Released time': 0.0
      }

    if call[0] == True:
      starts.insert(0, call)

      time_acquire += (call[2] - call[1])
      acquire_calls += 1

      threads[call[3]]['Acquired'] += 1
      threads[call[3]]['Acquired time'] += (call[2] - call[1])
    else:
      start = starts.pop(0)

      time_release += (call[2] - call[1])
      lock_hold += (call[2] - start[2])
      release_calls += 1

      threads[call[3]]['Released'] += 1
      threads[call[3]]['Released time'] += (call[2] - call[1])
      threads[call[3]]['Hold'] += (call[2] - start[2])

  table = []
  for thread_name, thread_data in threads.items():
    table.append([thread_name, thread_data['Hold'], thread_data['Hold'] / thread_data['Acquired'] if thread_data['Acquired'] > 0.0 else 0.0, thread_data['Acquired'], thread_data['Acquired time'], thread_data['Released'], thread_data['Released time']])

  print 'Lock "%s" (%s class)' % (lock.name, lock.klass)
  print tabulate.tabulate(table, headers = ['Name', 'Hold (s)', 'Hold per qcquire', 'Acquired', 'Acquire (s)', 'Released', 'Release (s)'], floatfmt = '.8f', missingval = '?')

def print_all_stats(stats):
  for lock in stats:
    print_stats(lock)
    print '\n---------------------------------------------------------------------------\n'

if __name__ == '__main__':
  import sys

  if len(sys.argv) != 2:
    sys.exit()

  stats = load_stats(sys.argv[1])
  print_all_stats(stats)

