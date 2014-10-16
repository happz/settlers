import ConfigParser
import os
import os.path
import shutil
import signal
import subprocess
import sys
import time

from hlib.tests import *

trace_call_offset = 0

def trace_call(func):
  def __trace_call_prefix():
    return (' ' * 2 * trace_call_offset) + str(time.time()) + ' '

  def wrapper(*func_args, **func_kwargs):
    arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
    args = func_args[:len(arg_names)]
    defaults = func.func_defaults or ()
    args = args + defaults[len(defaults) - (func.func_code.co_argcount - len(args)):]
    params = zip(arg_names, args)
    args = func_args[len(arg_names):]
    if args: params.append(('args', args))
    if func_kwargs: params.append(('kwargs', func_kwargs))

    global trace_call_offset

    print __trace_call_prefix() + '>> ' + func.func_name + '(' + ', '.join('%s = %r' % p for p in params) + ' )'

    trace_call_offset += 1
    ret = func(*func_args, **func_kwargs)
    trace_call_offset -= 1

    print __trace_call_prefix() + '<< ' + func.func_name + ': ' + str(ret)

    return ret
  return wrapper

class DummyUser(object):
  free_id = 0

  def __init__(self, name):
    super(DummyUser, self).__init__()

    self.name = name

    self.id = DummyUser.free_id
    DummyUser.free_id += 1

  def rename(self, container, new_name):
    del container[self.name]
    container[new_name] = self
    self.name = new_name

class DummyPlayer(object):
  def __init__(self, user):
    super(DummyPlayer, self).__init__()

    self.user = user

class DummyGame(object):
  def __init__(self):
    super(DummyGame, self).__init__()

    self.players = {}
