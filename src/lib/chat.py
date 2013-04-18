"""
Chat object providing simple forum representation.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import time

import hlib
import hlib.api
import hlib.event
import hlib.format
import hlib.input
import hlib.log
import hlib.pageable

import hlib.database

# Validators
from hlib.input import validator_factory, CommonString, MaxLength, Int

# pylint: disable-msg=F0401
import hruntime

ValidateChatPost = validator_factory(CommonString(), MaxLength(65535))

class ChatPost(hlib.database.DBObject):
  PACK_OBJECTS = ['user', 'stamp', 'message']

  def __init__(self, entity, user, stamp, message):
    hlib.database.DBObject.__init__(self)

    self.id		= None
    self.entity		= entity
    self.user		= user
    self.stamp		= stamp
    self.message	= message

    self._v_formatted	= None

  @property
  def formatted(self):
    if not hasattr(self, '_v_formatted') or self._v_formatted == None:
      self._v_formatted = hlib.format.tagize(self.message)

    return self._v_formatted

  def to_api(self):
    return {
      'id':			self.id,
      'user':			hlib.api.User(self.user),
      'stamp':			self.stamp,
      'time':			time.strftime(self.user.date_format, time.localtime(self.stamp)),
      'message':		self.formatted,
      'raw_message': self.message
    }

class ChatPosts(hlib.database.IndexedMapping):
  def __getattr__(self, name):
    if name == 'total':
      return len(self)

    if name == 'length':
      return len(self)

    return hlib.database.IndexedMapping.__getattr__(self, name)

  def get_posts(self, start, length):
    if len(self) <= 0:
      return []

    l = len(self)
    _start = l - start
    _end = l - start - length

    if start != 0:
      _start -= 1

    return self.values(min = _end, max = _start)

class ChatPager(hlib.pageable.Pageable):
  def __init__(self, entity, accessed_by):
    super(ChatPager, self).__init__(default_length = 20)

    self._entity = entity
    self._accessed_by = accessed_by

  # pylint: disable-msg=W0212
  entity		= property(lambda self: self._entity and self._entity or hruntime.dbroot.server)
  accessed_by		= property(lambda self: self._accessed_by if self._accessed_by != None else hruntime.user)
  unread		= property(lambda self: 0 if self.total == 0 else max(list(self.entity.chat_posts.keys())) - self.accessed_by.last_board)
  total			= property(lambda self: len(self.entity.chat_posts))
  length		= property(lambda self: self.total)

  def trigger_event(self):
    pass

  def add(self, text = None):
    text = text or ''

    cp = ChatPost(self.entity, hruntime.user, hruntime.time, text)

    self.entity.chat_posts.push(cp)

    self.trigger_event()

  def update_last_access(self, new_last):
    # pylint: disable-msg=W0621
    import hlib.handlers
    hlib.handlers.enable_write()

    self.accessed_by.last_board = new_last

  # Pageable interface implementation
  def get_records(self, start, length):
    records = self.entity.chat_posts.get_posts(start, length)
    records = [cp for cp in reversed(records)]

    if len(records) > 0 and self.accessed_by.last_board < records[0].id:
      self.update_last_access(records[0].id)

    return (records, self.length)

class ChatPagerGame(ChatPager):
  def __init__(self, game, accessed_by = None):
    accessed_by = accessed_by or game.my_player
    super(ChatPagerGame, self).__init__(game, accessed_by)

  def update_last_access(self, new_last):
    super(ChatPagerGame, self).update_last_access(new_last)

    hruntime.cache.remove_for_users([p.user for p in self.accessed_by.game.players.values()], 'recent_events')

  def trigger_event(self):
    hlib.event.trigger('game.ChatPost', self.entity, hidden = True, user = hruntime.user, game = self.entity)

class ChatPagerTournament(ChatPager):
  def __init__(self, tour):
    super(ChatPagerTournament, self).__init__(tour, tour.my_player)

  def update_last_access(self, new_last):
    super(ChatPagerTournament, self).update_last_access(new_last)

    hruntime.cache.remove_for_users([p.user for p in self.accessed_by.tournament.players.values()], 'recent_events')

  def trigger_event(self):
    hlib.event.trigger('tournament.ChatPost', self.entity, hidden = True, user = hruntime.user, tournament = self.entity)

class ChatPagerGlobal(ChatPager):
  def __init__(self):
    super(ChatPagerGlobal, self).__init__(None, None)

  def trigger_event(self):
    hlib.event.trigger('system.ChatPost', self.entity, hidden = True, user = hruntime.user)
