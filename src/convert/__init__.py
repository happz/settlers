import hlib

# pylint: disable-msg=F0401
import hruntime

CONVERTORS = {}

class SQLRow(object):
  pass

class Convertor(object):
  def __init__(self, name, db, **kwargs):
    super(Convertor, self).__init__()

    self.db		= db
    self.name		= name

    for k, v in kwargs.iteritems():
      setattr(self, k, v)

  def commit(self):
    hruntime.db.commit()

  def parse_row(self, r, names):
    o = SQLRow()

    for i in range(0, len(names)):
      setattr(o, names[i], r[i])

    return o

  def convert_item(self, record):
    pass

  def run(self, query, names):
    q = query % ', '.join(['`%s`' % n for n in names])

    rs = self.db.query(q)
    for r in rs:
      r = self.parse_row(r, names)
      self.convert_item(r)

import convert.root
import convert.i18n
import convert.trumpet
import convert.user
import convert.global_chat
import convert._games
