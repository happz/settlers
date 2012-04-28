import convert

import lib.chat

# pylint: disable-msg=F0401
import hruntime

class Convertor(convert.Convertor):
  def __init__(self, *args, **kwargs):
    super(Convertor, self).__init__('global_chat', *args, **kwargs)

  def run(self):
    super(Convertor, self).run('SELECT %s FROM `settlers_forum`.`posts` ORDER BY `id` ASC', ['message', 'poster', 'posted', 'poster_id'])

  def convert_item(self, record):
    cp = lib.chat.ChatPost(hruntime.dbroot.server, convert.map_uid_to_user[int(record.poster_id)], int(record.posted), record.message)
    hruntime.dbroot.server.chat_posts.push(cp)

convert.CONVERTORS['global_chat'] = Convertor
