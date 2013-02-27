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
    for p in self.container.players.values():
      if user == p.user:
        return p

    return None

  def __delitem__(self, key):
    raise AttributeError('UserToPlayerMap is read-only instance')

  def __setitem__(self, key, value):
    raise AttributeError('UserToPlayerMap is read-only instance')

  def __len__(self):
    return len(self.container.players)

  def __contains__(self, key):
    return self[key] != None

def pwcrypt(passwd):
  # pylint: disable-msg=E1101
  return hashlib.md5(passwd.encode('ascii', 'replace')).hexdigest()
