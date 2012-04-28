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

class TournamentCreated(Event):
  pass

class TournamentFinished(Event):
  pass

class TournamentCanceled(Event):
  pass

class TournamentStarted(Event):
  pass

class PlayerJoined(UserEvent):
  pass

class ChatPost(UserEvent):
  pass

import hlib

hlib.register_event(TournamentCreated)
hlib.register_event(TournamentFinished)
hlib.register_event(TournamentCanceled)
hlib.register_event(TournamentStarted)
hlib.register_event(PlayerJoined)
hlib.register_event(ChatPost)
