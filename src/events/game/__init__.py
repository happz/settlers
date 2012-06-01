"""
Game-wide events.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import hlib.api
import hlib.events

#
# Base classes
#

class Event(hlib.events.Event):
  """
  Base class for game-wide events.
  """

  def __init__(self, hidden = False, game = None):
    hlib.events.Event.__init__(self, hidden = hidden)

    self.game		= game
    self.round		= game.round

  def to_api(self):
    d = hlib.events.Event.to_api(self)

    d['gid']		= self.game.id
    d['round']		= self.round

    return d

class UserEvent(Event):
  def __init__(self, user = None, **kwargs):
    Event.__init__(self, **kwargs)

    self.user		= user

  def to_api(self):
    d = Event.to_api(self)

    d['user'] = hlib.api.User(self.user)

    return d

class CardEvent(UserEvent):
  def __init__(self, card = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.card           = card

  def to_api(self):
    d = UserEvent.to_api(self)

    d['card'] = {
      'type':		self.card.type,
      'bought':		self.card.bought,
      'used':		self.card.used
    }

    return d

#
# Real events
#

class GameCreated(Event):
  pass

class GameFinished(Event):
  pass

class GameCanceled(UserEvent):
  REASON_MASSIVE  = 1
  REASON_ABSENTEE = 2
  REASON_EMPTY    = 3

  def __init__(self, reason = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.reason		= reason

  def to_api(self):
    d = UserEvent.to_api(self)

    d['reason'] = self.reason

    return d

class GameStarted(Event):
  pass

class PlayerJoined(UserEvent):
  pass

class ChatPost(UserEvent):
  pass

class PlayerMissed(UserEvent):
  def __init__(self, logged = False, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.logged		= logged

class Pass(Event):
  def __init__(self, prev = None, next = None, **kwargs):
    Event.__init__(self, **kwargs)

    self.prev		= prev
    self.next		= next

  def to_api(self):
    d = Event.to_api(self)

    d['prev'] = hlib.api.User(self.prev)
    d['next'] = hlib.api.User(self.next)

    return d

class PlayerInvited(UserEvent):
  pass

class CardUsed(CardEvent):
  pass

class CardBought(CardEvent):
  pass

import hlib

hlib.register_event(GameCreated)
hlib.register_event(GameFinished)
hlib.register_event(GameCanceled)
hlib.register_event(GameStarted)
hlib.register_event(PlayerJoined)
hlib.register_event(ChatPost)
hlib.register_event(PlayerMissed)
hlib.register_event(Pass)
hlib.register_event(PlayerInvited)
hlib.register_event(CardUsed)
hlib.register_event(CardBought)
