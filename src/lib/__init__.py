"""
Simple and common functions

@version:                       1.2

@author:                        Milos Prchlik 
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import hashlib
import sys

class UserToPlayerMap(object):
  def __init__(self, container):
    super(UserToPlayerMap, self).__init__()

    self.container = container

  def __getitem__(self, user):
    for p in self.container.players.itervalues():
      if user.name == p.user.name:
        return p

    return None

  def __contains__(self, key):
    return self[key] != None

def pwcrypt(passwd):
  # pylint: disable-msg=E1101
  return hashlib.md5(passwd).hexdigest()
