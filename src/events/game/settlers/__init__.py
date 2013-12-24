from events.game import Event, UserEvent
import hlib.api

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

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
      return self.thief != None and self.thief == hruntime.user

    if name == 'am_i_victim':
      return self.victim != None and self.victim == hruntime.user

    return Event.__getattr__(self, name)

  def to_api(self):
    d = Event.to_api(self)

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

  def to_api(self):
    d = UserEvent.to_api(self)

    d['src'] = resources_to_api(self.src)
    d['dst'] = resources_to_api(self.dst)

    return d

class Monopoly(ThiefEvent):
  def __init__(self, resources = None, **kwargs):
    ThiefEvent.__init__(self, **kwargs)

    self.resources		= resources

  def to_api(self):
    d = ThiefEvent.to_api(self)

    d['resources'] = resources_to_api(self.resources)

    return d

class ThiefPlaced(UserEvent):
  def __init__(self, field = None, **kwargs):
    UserEvent.__init__(self, **kwargs)

    self.field		= field

class NewDiceLine(Event):
  pass

LongestPathBonusEarned.register()
MightestChilvaryBonusEarned.register()
ResourceStolen.register()
ResourcesStolen.register()
DiceRolled.register()
VillageBuilt.register()
TownBuilt.register()
PathBuilt.register()
ResourcesReceived.register()
ResourcesExchanged.register()
Monopoly.register()
ThiefPlaced.register()
NewDiceLine.register()
