__author__                      = 'Milos Prchlik'
__copyright__                   = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__                     = 'happz@happz.cz'
__license__                     = 'http://www.php-suit.com/dpl'

import threading

import hlib.api
import hlib.database
import hlib.error

import lib
import lib.chat

# pylint: disable-msg=F0401
import hruntime

class PlayableError(hlib.error.BaseError):
  pass

class WrongPasswordError(PlayableError):
  def __init__(self, *args, **kwargs):
    kwargs.update({
      'msg':			'Wrong password',
      'reply_status':		401,
      'dont_log':		True
    })

    super(WrongPasswordError, self).__init__(*args, **kwargs)

class AlreadyStartedError(PlayableError):
  def __init__(self, *args, **kwargs):
    kwargs.update({
      'msg':			'Already started',
      'reply_status':		401
    })

    super(AlreadyStartedError, self).__init__(*args, **kwargs)

class AlreadyJoinedError(PlayableError):
  def __init__(self, *args, **kwargs):
    kwargs.update({
      'msg':			'Already joined',
      'reply_status':		402
    })

    super(AlreadyJoinedError, self).__init__(*args, **kwargs)

class CannotBeArchivedError(PlayableError):
  def __init__(self, *args, **kwargs):
    kwargs.update({
      'msg':			'Can not be archived yet',
      'reply_status':		402
    })

    super(CannotBeArchivedError, self).__init__(*args, **kwargs)

class Player(hlib.database.DBObject):
  def __init__(self, user):
    hlib.database.DBObject.__init__(self)

    self.user			= user
    self.confirmed		= True
    self.last_board		= 0

  def __getattr__(self, name):
    if name == 'is_on_turn':
      return False

    return hlib.database.DBObject.__getattr__(self, name)

  def to_api(self):
    return {
      'user':			hlib.api.User(self.user),
      'is_confirmed':		self.confirmed,
      'is_on_turn':		self.is_on_turn
    }

  def to_state(self):
    return {
      'user':			hlib.api.User(self.user)
    }

class Playable(hlib.database.DBObject):
  def __init__(self, flags):
    hlib.database.DBObject.__init__(self)

    self.flags			= flags

    self.id			= None
    self.name			= flags.name
    self.owner			= flags.owner
    self.password		= flags.password
    self.limit			= flags.limit
    self.round			= 0
    self.kind			= flags.kind
    self.last_pass		= hruntime.time

    self.chat_posts		= lib.chat.ChatPosts()

    self.events			= hlib.database.IndexedMapping()

    self._v_user_to_player	= None

    if not flags.password or flags.password == '':
      self.password = None

    else:
      self.password = lib.pwcrypt(flags.password)

  def __getattr__(self, name):
    if name == 'user_to_player':
      if not hasattr(self, '_v_user_to_player') or self._v_user_to_player == None:
        self._v_user_to_player = lib.UserToPlayerMap(self)

      return self._v_user_to_player

    if name == 'my_player':
      return self.user_to_player[hruntime.user]

    if name == 'is_password_protected':
      return self.password != None and len(self.password) > 0

    if name == 'archive_deadline':
      if self.is_active:
        raise CannotBeArchivedError()

      atime = self.last_pass

      for p in self.players.values():
        chat_lister = self.chat_class(self, accessed_by = p)
        if chat_lister.unread > 0:
          raise CannotBeArchivedError()

        atime = max(atime, p.last_board)

      return atime + (86400 * 7)

    if name == 'can_be_archived':
      try:
        if hruntime.time > self.archive_deadline:
          return True

      except CannotBeArchivedError, e:
        return False

      return False

    return hlib.database.DBObject.__getattr__(self, name)

  def has_player(self, user):
    return user in self.user_to_player

  def to_api(self):
    ret = {
      'id':			self.id,
      'kind':			self.kind,
      'name':			self.name,
      'round':			self.round,
      'is_finished':		self.is_finished,
      'is_present':		self.has_player(hruntime.user),
      'has_password':		self.is_password_protected,
      'chat_posts':		self.chat.unread if self.chat.unread > 0 else False,
      'players':		[p.to_api() for p in self.players.values()]
    }

    try:
      ret['archive_deadline']	= self.archive_deadline
    except CannotBeArchivedError:
      ret['archive_deadline']	= False

    return ret

  def to_state(self):
    return {
      'name':			self.name,
      'round':			self.round,
      'players':		[p.to_state() for p in self.players.values()],
      'events':			[e.to_api() for e in self.events.values() if e.hidden != True]
    }

class PlayableLists(object):
  def __init__(self):
    super(PlayableLists, self).__init__()

    self._lock          = threading.RLock()

    self._active        = {}
    self._inactive      = {}
    self._archived      = {}

  def __get_f_list(self, name, user):
    cache = getattr(self, '_' + name)

    with self._lock:
      if user not in cache:
        update = getattr(self, 'get_' + name)
        cache[user] = update(user)

      return self.get_objects(cache[user])

  def get_objects(self, l):
    return []

  def get_active(self, user):
    return []

  def get_inactive(self, user):
    return []

  def get_archived(self, user):
    return []

  def f_active(self, user):
    return self.__get_f_list('active', user)

  def f_inactive(self, user):
    return self.__get_f_list('inactive', user)

  def f_archived(self, user):
    return self.__get_f_list('archived', user)

  def snapshot(self, l):
    with self._lock:
      return getattr(self, '_' + l).copy()

  # Cache invalidation
  def _inval_user(self, user):
    with self._lock:
      try:
        del self._active[user]
      except KeyError:
        pass

      try:
        del self._inactive[user]
      except KeyError:
        pass

      try:
        del self._archived[user]
      except KeyError:
        pass

    return True

  def inval_players(self, p):
    with self._lock:
      for player in p.players.values():
        self._inval_user(player.user)

    return True

  def inval_all(self, l):
    with self._lock:
      setattr(self, '_' + l, {})

  # Shortcuts
  def created(self, p):
    self.inval_all('active')

    hruntime.cache.remove_for_all_users('recent_events')

    return True

  def started(self, p):
    self.inval_all('active')

    hruntime.cache.remove_for_all_users('recent_events')

    return True

  def finished(self, p):
    with self._lock:
      self.inval_players(p)

    for player in p.players.values():
      hruntime.cache.remove(p.user, 'recent_events')

    return True

  def archived(self, p):
    with self._lock:
      self.inval_players(p)

    for player in p.players.values():
      hruntime.cache.remove(p.user, 'recent_events')

    return True
