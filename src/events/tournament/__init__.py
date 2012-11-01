"""
Tournament-wide events.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import hlib.events

class Event(hlib.events.Event):
  def __init__(self, tournament, **kwargs):
    hlib.events.Event.__init__(self, **kwargs)

    self.tournament		= tournament
    self.round			= tournament.round

class UserEvent(Event):
  def __init__(self, user = None, **kwargs):
    Event.__init__(self, **kwargs)

    self.user			= user

class Created(Event):
  pass

class Finished(Event):
  pass

class Canceled(Event):
  pass

class Started(Event):
  pass

class PlayerJoined(UserEvent):
  pass

class ChatPost(UserEvent):
  pass

import hlib

hlib.register_event(Created)
hlib.register_event(Finished)
hlib.register_event(Canceled)
hlib.register_event(Started)
hlib.register_event(PlayerJoined)
hlib.register_event(ChatPost)
