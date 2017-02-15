import sys
import threading
import time

class Runtime(object):
  PROPERTIES = ['user', 'db', 'dbconn', 'dbroot', 'root', 'server', 'dont_commit', 'ui_form', 'app', 'request', 'response', 'session', 'i18n',
                'tid', 'service_engine', 'service_server', 'service_thread']

  RESET_PROPERTIES = ['user', 'dbconn', 'dbroot', 'server', 'dont_commit', 'ui_form', 'request', 'response', 'session', 'i18n']

  def reset_locals(self):
    for p in self.RESET_PROPERTIES:
      setattr(self.data, p, None)

    self._stamp = None

  def init_locals(self):
    if hasattr(self.data, 'init_done') and self.data.init_done == True:
      return

    for p in self.PROPERTIES:
      setattr(self.data, p, None)

    self.data.init_done = True

  def __init__(self):
    """
    @type properties:      C{list} of C{string}s
    @param properties:    List of names of properties this module holds. Properties that are handled by C{__getattr__}/C{__setattr__} method are NOT included.
    """

    super(Runtime, self).__init__()

    self.data = threading.local()

  def __getattribute__(self, name):
    if name == 'localtime':
      return time.localtime(self.time)

    if name == 'cache':
      return self.app.cache

    # pylint: disable-msg=W0212
    if name == 'time':
      if not hasattr(self.data, 'stamp') or self.data._stamp == None:
        self.data._stamp = int(time.time())

      return self.data._stamp

    if name == 'PROPERTIES':
      return super(Runtime, self).__getattribute__(name)

    if name in self.PROPERTIES:
      self.init_locals()
      return getattr(self.data, name)

    return super(Runtime, self).__getattribute__(name)

  def __setattr__(self, name, value):
    if name == 'time':
      # pylint: disable-msg=W0212
      self._stamp = None
      return

    if name in self.PROPERTIES:
      self.init_locals()
      setattr(self.data, name, value)
      return

    super(Runtime, self).__setattr__(name, value)

  def clean(self):
    self.user      = None
    self.dont_commit    = False
    self.ui_form    = None
    self.time      = None

sys.modules['hruntime'] = Runtime()
