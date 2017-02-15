"""
Game-wide events.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import hlib.api
import hlib.events
#import hlib.serialize

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

  def serialize(self, container, *properties, **kwargs):
    properties = properties or [lambda x: ('gid', x.game.id), 'round']

    hlib.events.Event.serialize(self, container, **kwargs)
    container.extend(self, *properties)

class UserEvent(Event):
  def __init__(self, user = None, **kwargs):
    Event.__init__(self, **kwargs)

    self.user		= user

  def to_api(self):
    d = Event.to_api(self)

    if self.user:
      d['user'] = hlib.api.User(self.user)

    return d

  def serialize(self, container, *properties, **kwargs):
    Event.serialize(self, container, **kwargs)

    if self.user:
      container['user'] = hlib.serialize.Container()
      self.user.serialize(container['user'], **kwargs)

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

  def serialize(self, container, **kwargs):
    UserEvent.serialize(self, container, **kwargs)

    container['card'] = hlib.serialize.Container()
    container['card'].extend(self.card, 'type', 'bought', 'used')

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

  def serialize(self, container, **kwargs):
    UserEvent.serialize(self, container, **kwargs)

    container['reason'] = self.reason

class GameArchived(Event):
  pass

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

  def serialize(self, container, **kwargs):
    Event.serialize(self, container, **kwargs)

    container['prev'] = hlib.serialize.Container()
    self.prev.serialize(container['prev'], **kwargs)

    container['next'] = hlib.serialize.Container()
    self.next.serialize(container['next'], **kwargs)

class PlayerInvited(UserEvent):
  pass

class CardUsed(CardEvent):
  pass

class CardBought(CardEvent):
  pass

GameCreated.register()
GameFinished.register()
GameCanceled.register()
GameArchived.register()
GameStarted.register()
PlayerJoined.register()
ChatPost.register()
PlayerMissed.register()
Pass.register()
PlayerInvited.register()
CardUsed.register()
CardBought.register()
