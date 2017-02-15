__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import hlib.database
import hlib.i18n

from database import DBObject

# pylint: disable-msg=F0401
import hruntime # @UnresolvedImport

class Root(DBObject):
  def __init__(self):
    DBObject.__init__(self)

    self.server		= None
    self.localization	= hlib.i18n.Localization(languages = ['cz'])
    self.trumpet	= hlib.database.SimpleMapping()
    self.users		= hlib.database.StringMapping()

class Server(DBObject):
  def __init__(self):
    DBObject.__init__(self)

    self.events			= hlib.database.IndexedMapping()
    self.maintenance_mode	= False

  def __getattr__(self, name):
    if name == 'online_users':
      return hruntime.app.sessions.online_users

    return DBObject.__getattr__(self, name)

class Event(DBObject):
  def __init__(self, stamp, hidden):
    DBObject.__init__(self)

    self.id		= None
    self.stamp		= stamp
    self.hidden		= hidden

class DummyUser(object):
  def __init__(self, name):
    super(DummyUser, self).__init__()

    self.name		= unicode(name)

  def __hash__(self):
    return hash(self.name)

class User(DBObject):
  def __init__(self, name, password, email):
    DBObject.__init__(self)

    self.name		= unicode(name)
    self.password	= unicode(password)
    self.admin		= False
    self.date_format = '%d/%m/%Y %H:%M:%S'
    self.email		= unicode(email)
    self.maintenance_access	= False

    self.cookies	= hlib.database.SimpleMapping()

    self.events		= hlib.database.IndexedMapping()

    self.api_tokens	= hlib.database.SimpleList()

  def __eq__(self, other):
    if not isinstance(other, User):
      return False

    return self.name == other.name

  def __ne__(self, other):
    if not isinstance(other, User):
      return True

    return self.name != other.name

  def __cmp__(self, other):
    return cmp(self.name, other.name)

  def __hash__(self):
    return hash(self.name)

  def __getattr__(self, name):
    if name == 'is_admin':
      return self.admin == True

    if name == 'is_online':
      return self.name in hruntime.app.sessions.online_users

    return DBObject.__getattr__(self, name)

  def reset_api_tokens(self):
    self.api_tokens = hlib.database.SimpleList()
