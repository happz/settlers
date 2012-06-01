from events.game import Event, UserEvent
import hlib.api

# pylint: disable-msg=F0401
import hruntime

#
# Base classes
#

class ThiefEvent(Event):
  def __init__(self, thief = None, victim = None, **kwargs):
    Event.__init__(self, **kwargs)

    self.thief		= thief
    self.victim		= victim

  def __getattr__(self, name):
    if name == 'am_i_thief':
      return self.thief != None and self.thief.name == hruntime.user.name

    if name == 'am_i_victim':
      return self.victim != None and self.victim.name == hruntime.user.name

    return Event.__getattr__(self, name)

  def to_api(self):
    d = Event.to_api(self);

    d['thief'] = hlib.api.User(self.thief) if self.thief != None else None
    d['victim'] = hlib.api.User(self.victim) if self.victim != None else None

    d['am_i_thief'] = self.am_i_thief
    d['am_i_victim'] = self.am_i_victim

    return d

def resources_to_api(rs):
  d = {}

  for k in rs.keys():
    d[k] = rs[k]

  return d

#
# Event classes
#

class LongestPathBonusEarned(UserEvent):
  pass

class MightestChilvaryBonusEarned(UserEvent):
  pass

class ResourceStolen(ThiefEvent):
  def __init__(self, resource = None, **kwargs):
    ThiefEvent.__init__(self, **kwargs)

    self.resource = resource

  def to_api(self):
    d = ThiefEvent.to_api(self)

    d['resource'] = self.resource

    return d

class ResourcesStolen(ThiefEvent):
  def __init__(self, resources = None, **kwargs):
    ThiefEvent.__init__(self, **kwargs)

    self.resources		= resources

  def to_api(self):
    d = ThiefEvent.to_api(self)

    d['resources'] = resources_to_api(self.resources)

    return d

class DiceRolled(UserEvent):
  def __init__(self, dice = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.dice		= dice

class VillageBuilt(UserEvent):
  def __init__(self, node = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.node		= node

class TownBuilt(UserEvent):
  def __init__(self, node = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.node = node

class PathBuilt(UserEvent):
  def __init__(self, path = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.path		= path

class ResourcesReceived(UserEvent):
  def __init__(self, resources = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.resources		= resources


  def to_api(self):
    d = UserEvent.to_api(self)

    d['resources'] = resources_to_api(self.resources)

    return d

class ResourcesExchanged(UserEvent):
  def __init__(self, src = None, dst = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.src = src
    self.dst = dst

class Monopoly(ThiefEvent):
  def __init__(self, resources = None, **kwargs):
    ThiefEvent.__init__(self, **kwargs)

    self.resources		= resources

class ThiefPlaced(UserEvent):
  def __init__(self, field = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.field		= field

class NewDiceLine(Event):
  pass

import hlib

hlib.register_event(LongestPathBonusEarned)
hlib.register_event(MightestChilvaryBonusEarned)
hlib.register_event(ResourceStolen)
hlib.register_event(ResourcesStolen)
hlib.register_event(DiceRolled)
hlib.register_event(VillageBuilt)
hlib.register_event(TownBuilt)
hlib.register_event(PathBuilt)
hlib.register_event(ResourcesReceived)
hlib.register_event(ResourcesExchanged)
hlib.register_event(Monopoly)
hlib.register_event(ThiefPlaced)
hlib.register_event(NewDiceLine)
