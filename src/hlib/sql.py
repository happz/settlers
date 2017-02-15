"""
Dummy SQL module for simple acces to external relational databases

MySQL-only support by now.
"""

__author__              = 'Milos Prchlik'
__copyright__           = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__             = 'happz@happz.cz'
__license__             = 'http://www.php-suit.com/dpl'

import MySQLdb

class DataBaseConnection(object):
  def __init__(self, db, cursor):
    super(DataBaseConnection, self).__init__()

    self.db		= db
    self.cursor		= cursor

  def commit(self):
    self.query('COMMIT')

  def rollback(self):
    self.query('ROLLBACK')

  def query(self, q):
    self.cursor.execute(q)
    return self.cursor.fetchall()

  def close(self):
    self.cursor.close()

class DataBase(object):
  def __init__(self, **kwargs):
    super(DataBase, self).__init__()

    self.conn		= None
    self.kwargs		= kwargs

  def open(self):
    self.conn = MySQLdb.connect(charset = 'utf8', use_unicode = True, **self.kwargs)

  def connect(self):
    c = DataBaseConnection(self, self.conn.cursor())

    c.query('SET AUTOCOMMIT = 0')
    c.query('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE')
    c.query('START TRANSACTION')

    return c

  def start_transaction(self):
    pass

  def commit(self):
    pass

  def rollback(self):
    pass
