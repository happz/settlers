import os.path
import sys

import hruntime  # @UnresolvedImport

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
