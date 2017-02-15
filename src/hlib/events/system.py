__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

from hlib.events import Event

class UserEvent(Event):
  def __init__(self, user = None, **kwargs):
    Event.__init__(self, **kwargs)

    self.user		= user

class UserLoggedIn(UserEvent):
  dont_store = True

class UserLoggedOut(UserEvent):
  dont_store = True

class ChatPost(UserEvent):
  pass

class UserRegistered(UserEvent):
  dont_store = True

class LogReload(Event):
  dont_store = True

class SystemReload(Event):
  dont_store = True

UserLoggedIn.register()
UserLoggedOut.register()
UserRegistered.register()
ChatPost.register()
LogReload.register()
SystemReload.register()
