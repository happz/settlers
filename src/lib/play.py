__author__                      = 'Milos Prchlik'
__copyright__                   = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__                     = 'happz@happz.cz'
__license__                     = 'http://www.php-suit.com/dpl'

import threading
import time

import hlib.api
import hlib.database
import hlib.error
import hlib.locks

import lib.chat

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

from functools import partial

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
    self.last_board		= -1

  def __getattr__(self, name):
    if name == 'is_on_turn':
        return False

    return hlib.database.DBObject.__getattr__(self, name)

  def touch(self):
      self._v_last_access = time.time()

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

  def _createAPIDataSummary(self, user):
      my_player = self.game.my_player(user)

      return {
          'user': self.user.toAPI(),
          'color': '',
          'isConfirmed': self.confirmed,
          'isOnTurn': self.is_on_turn,
          'isMyPlayer': False if my_player is None else (self.id == my_player.id),
          'id': self.id
      }

  def toAPI(self, user, summary = True):
      if summary is True:
          return self._createAPIDataSummary(user)

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

  def my_player(self, user):
      return self.user_to_player[user]

  def __getattr__(self, name):
    if name == 'user_to_player':
      if not hasattr(self, '_v_user_to_player') or self._v_user_to_player == None:
        self._v_user_to_player = lib.UserToPlayerMap(self)

      return self._v_user_to_player

    if name == 'is_password_protected':
      return self.password != None and len(self.password) > 0

    if name == 'atime':
      atime = self.last_pass

      for p in self.players.values():
        atime = max(atime, p.last_board)

      return atime

    if name == 'archive_deadline':
      if self.is_active:
        raise CannotBeArchivedError()

      for p in self.players.values():
        chat_lister = self.chat_class(self, accessed_by = p)
        if chat_lister.unread > 0:
          raise CannotBeArchivedError()

      return self.atime + (86400 * 7)

    if name == 'archive_deadline_hard':
      if self.is_active:
        raise CannotBeArchivedError()

      return self.atime + (864000 * 60)

    if name == 'can_be_archived':
      try:
        if self.is_active:
          raise CannotBeArchivedError()

        for p in self.players.values():
          chat_lister = self.chat_class(self, accessed_by = p)
          if chat_lister.unread > 0:
            raise CannotBeArchivedError()

        if hruntime.time > self.archive_deadline_hard:
          return True

        if hruntime.time > self.archive_deadline:
          return True

      except CannotBeArchivedError:
        return False

      return False

    return hlib.database.DBObject.__getattr__(self, name)

  def get_type(self):
    return None

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
      'players':		[p.to_api() for p in self.players.values()],
      'last_pass': self.last_pass
    }

    try:
      ret['archive_deadline']	= self.archive_deadline
    except CannotBeArchivedError:
      ret['archive_deadline']	= False

    return ret

  def _createAPIData_Summary(self, user):
      return {
          'id': self.id,
          'kind': self.kind,
          'name': self.name,
          'round': self.round,
          'limit': self.limit,
          'hasPassword': self.is_password_protected,
          'players': [ player.toAPI(user, summary = True) for player in self.players.itervalues() ],
          'isPresent': self.has_player(user),
          'isInvited': self.has_player(user) and not self.has_confirmed_player(user),
          'isFinished': self.is_finished
      }

  def toAPI(self, user, summary = True):
    if summary is True:
      return self._createAPIData_Summary(user)

    else:
      return {}

  def to_state(self):
    return {
      'name':			self.name,
      'round':			self.round,
      'limit':			self.limit,
      'players':		[p.to_state() for p in self.players.values()],
      'events':			[e.to_api() for e in self.events.values() if e.hidden != True]
    }

class PlayableListCache(object):
    def __init__(self, bus, workerThread):
        self._bus = bus
        self._workerThread = workerThread

        self._active = {}
        self._inactive = {}
        self._archived = {}

    def _get_filtered_list(self, cache, creator, dbroot, user):
        if user not in cache:
            cache[user] = creator(dbroot, user)

        return cache[user]

    def _invalidate_user(self, user):
        if user in self._active:
            del self._active[user]

        if user in self._inactive:
            del self._inactive[user]

        if user in self._archived:
            del self._archived[user]

    def _invalidate_players(self, playable):
        for player in playable.players.itervalues():
            self._invalidate_user(player.user)

    def _invalidate_all(self, key):
        setattr(self, '_' + key, {})

    def onCreated(self, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_all, 'active')

    def onStarted(self, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_all, 'active')

    def onFinished(self, playable, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_players, playable)

    def onArchived(self, playable, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_players, playable)

    def onCanceled(self, playable, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_all, 'active')

    def onPlayerJoined(self, playable, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_players, playable)

    def onPlayerInvited(self, playable, *args, **kwargs):
        self._workerThread.enqueuePriorityTask(self._invalidate_players, playable)
