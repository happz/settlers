import convert

import lib.datalayer

import hlib.database

# pylint: disable-msg=F0401
import hruntime

convert.map_uid_to_user		= {}

class Convertor(convert.Convertor):
  def __init__(self, *args, **kwargs):
    super(Convertor, self).__init__('user', *args, **kwargs)

  def convert_item(self, record):
    u = lib.datalayer.User(record.name, record.password, record.email)
    u.sound		= (record.sound == '1')
#    u.color		= record.color
    u.after_pass_turn	= int(record.after_pass_turn)
    u.date_format	= unicode(record.date_format)
    u.atime		= int(record.atime)
    u.last_board	= int(record.last_board)
    u.admin		= (record.admin == 'true')
    u.table_length	= int(record.tablesort_length)
    u.board_skin	= unicode(record.board_skin)
    u.vacation		= int(record.vacation)
    u.registered	= int(record.registered)

    hruntime.dbroot.users[u.name] = u

    convert.map_uid_to_user[int(record.id)] = u

  def run(self):
    hruntime.dbroot.users = hlib.database.StringMapping()

    super(Convertor, self).run('SELECT %s FROM `users`', ['name', 'password', 'email', 'sound', 'color', 'after_pass_turn', 'date_format', 'atime', 'last_board', 'admin', 'tablesort_length', 'board_skin', 'vacation', 'registered', 'id'])

convert.CONVERTORS['user'] = Convertor
