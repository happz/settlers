__author__			= 'Milos Prchlik'
__copyright__			= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__			= 'happz@happz.cz'
__license__			= 'http://www.php-suit.com/dpl'

import threading

import handlers
import lib.datalayer

import hlib.api
import hlib.input
import hlib.pageable

# Handlers
from hlib.api import api
from handlers import page, require_login, require_write

# Validators
from hlib.input import validator_factory, validate_by

# pylint: disable-msg=F0401
import hruntime

class Post(object):
  def __init__(self, author, stamp, text):
    super(Post, self).__init__()

    self.author		= author
    self.stamp		= stamp
    self.text		= text

  def to_api(self):
    return {
      'author':		hlib.api.User(self.author),
      'stamp':		self.stamp,
      'text':		self.text
    }

class Handler(handlers.GenericHandler):
  def __init__(self):
    super(Handler, self).__init__()

    self.lock = threading.RLock()
    self._posts = []
    self.cached_posts = None

  #
  # Posts
  #
  @require_login
  @api
  def posts(self):
    posts = []
    with self.lock:
      if self.cached_posts == None:
        self.cached_posts = []
        for post in self._posts:
          self.cached_posts.append(post.to_api())

      self.cached_posts = [p for p in reversed(self.cached_posts)]
      posts = self.cached_posts

    return hlib.api.Reply(200, posts = posts)

  #
  # Add
  #
  class ValidateAdd(hlib.input.SchemaValidator):
    text = validator_factory(hlib.input.CommonString(), hlib.input.MaxLength(65535))

  @require_login
  @validate_by(schema = ValidateAdd)
  @api
  def add(self, text = None):
    with self.lock:
      self.cached_posts = None

      ot = hruntime.time - 300
      self._posts = [p for p in self._posts if p.stamp >= ot]

      self._posts.append(Post(hruntime.user, hruntime.time, unicode(text)))
