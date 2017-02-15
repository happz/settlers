"""
Chat object providing simple forum representation.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

from .datalayer import DBObject, IndexedMapping

class ChatPost(DBObject):
  def __init__(self, entity, user, stamp, message):
    DBObject.__init__(self)

    self.id		= None
    self.entity		= entity
    self.user		= user
    self.stamp		= stamp
    self.message	= message

  def _createAPIData(self):
    return {
      'id': self.id,
      'author': self.user.toAPI(),
      'stamp': self.stamp,
      'text': self.message
    }

  def toAPI(self):
      return self._createAPIData()

class ChatPosts(IndexedMapping):
    def __getattr__(self, name):
        if name == 'total':
            raise NotImplemented()

        if name == 'length':
            raise NotImplemented()

        return IndexedMapping.__getattr__(self, name)

    def get_posts(self, start, length):
        l = len(self)

        if l == 0:
            return []

        _start = l - start
        _end = l - start - length

        if start != 0:
            _start -= 1

        return self.values(min = _end, max = _start)

    def newerThan(self, index):
        if len(self) == 0:
            return 0

        return self.max_key() - index

def add_post(bus, storage, user, stamp, text):
    cp = ChatPost(storage, user, int(stamp), text)
    storage.chat_posts.push(cp)

    bus.publish('board.new-post', user = user, storage = storage, post = cp)
