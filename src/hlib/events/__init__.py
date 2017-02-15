__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import collections

import hlib
import hlib.datalayer

import hruntime  # @UnresolvedImport

_EVENTS = {}
_HOOKS = {}

class Event(hlib.datalayer.Event):
  dont_store = False
  dont_log = True

  def __init__(self, hidden = False):
    hlib.datalayer.Event.__init__(self, hruntime.time, hidden)

  @classmethod
  def ename(cls):
    return '.'.join([] + (cls.__module__.startswith('hlib') and cls.__module__.split('.')[2:] or cls.__module__.split('.')[1:]) + [cls.__name__])

  @classmethod
  def register(cls):
    _EVENTS[cls.ename()] = cls

  @classmethod
  def is_registered(cls):
    return cls.ename() in _EVENTS

  @classmethod
  def unregister(cls):
    if cls.ename() in _EVENTS:
      del _EVENTS[cls.ename()]

  def to_api(self):
    return {
      'id':		self.id,
      'stamp':		self.stamp,
      'hidden':		self.hidden,
      'ename':		self.__class__.ename()
    }

class Hook(object):
  def __init__(self, event, callback, name = None, post = True, args = None, kwargs = None):
    super(Hook, self).__init__()

    self.event = event
    self.callback = callback
    self.name = name if name != None else super(Hook, self).__repr__()
    self.callback = callback
    self.post    = post
    self.args           = args or []
    self.kwargs         = kwargs or {}

    self.register()

    # Test framework uses this to save old callback
    # when patching event hooks
    self.saved_callbacks = []

  def register(self):
    if self.event not in _HOOKS:
      _HOOKS[self.event] = collections.OrderedDict()

    _HOOKS[self.event][self.name] = self

  def is_registered(self):
    return self.event in _HOOKS and self.name in _HOOKS[self.event]

  def unregister(self):
    if self.name in _HOOKS[self.event]:
      del _HOOKS[self.event][self.name]

  def __call__(self, event):
    _args = self.args + [event]

    # pylint: disable-msg=W0142
    return self.callback(*_args, **self.kwargs)

  def __repr__(self):
    return 'Hook(%s, %s, name = "%s")' % (self.event, self.callback, self.name)

def trigger(name, holder, post = True, **kwargs):
  """
  Raise new event.

  @type name:      C{string}
  @param name:      Events name
  @type kwargs:      C{dictionary}
  @param kwargs:    Arguments to pass to event's constructor
  @rtype:      L{events.Event}
  @return:      Newly created event object
  """

  # pylint: disable-msg=W0142
  e = _EVENTS[name]
  e = e(**kwargs)

  if e.dont_store != True:
    holder.events.push(e)

  if e.dont_log != True and hasattr(e, 'app') and e.app != None:
    e.app.log_event(e)

  if name not in _HOOKS:
    return

  for hook in _HOOKS[name].values():
    if hook.post == post:
      hook(e)
