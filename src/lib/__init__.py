"""
Simple and common functions

@version:                       1.2

@author:                        Milos Prchlik 
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import hashlib
import os
import os.path
import types
import sys

import hlib
import hruntime  # @UnresolvedImport

class UserToPlayerMap(object):
  def __init__(self, container):
    super(UserToPlayerMap, self).__init__()

    self.container = container

  def __getitem__(self, user):
    username = user if type(user) in types.StringTypes else user.name

    for p in self.container.players.values():
      if username == p.user.name:
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

def version_stamp(path):
  while path[0] == '/':
    path = path[1:]

  path = os.path.join(hruntime.app.config['dir'], path)

  try:
    stat = os.stat(path)

  except OSError:
    print >> sys.stderr, 'Missing file: "%s"' % path
    return ''

  else:
    return '?_version_stamp=' + str(int(stat.st_mtime))
