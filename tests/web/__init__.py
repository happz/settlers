import functools
import os.path
import shutil
import signal
import splinter
import splinter.exceptions
import sys
import urlparse

import tests.appserver
from tests import *
from tests.web.conditions import WaitWhile, WaitUntil, BrowserHasURL
from nose.tools import make_decorator

def requires_login(fn):
  def __requires_login(*args, **kwargs):
    cls = args[0]
    cls.relogin()

    fn(*args, **kwargs)
  __requires_login = make_decorator(fn)(__requires_login)
  return __requires_login

def requires_url(url):
  def _requires_url(fn):
    fn.__requires_url = url

    def __requires_url(*args, **kwargs):
      cls = args[0]

      cls.goto(urlparse.urljoin(cls.get_root_url(), fn.__requires_url))

      fn(*args, **kwargs)
    __requires_url = make_decorator(fn)(__requires_url)
    return __requires_url
  return _requires_url

def HAS_URL(browser, url):
  EQ(url, browser.url)

def HAS_NOT_URL(browser, url):
  NEQ(url, browser.url)

def HAS_TITLE(browser, title):
  EQ(title, browser.title)

def HAS_NOT_TITLE(browser, title):
  NEQ(title, browser.title)

def HAS_TEXT(browser, text):
  T(browser.is_text_present(text))

def HAS_NOT_TEXT(browser, text):
  F(browser.is_text_present(text))

def HAS_ELEMENT(lookup, *args, **kwargs):
  elements = lookup(*args, **kwargs)

  if len(elements) <= 0:
    T(False, msg = 'No such element: %s(%s, %s)' % (lookup, str(args), str(kwargs)))

def HAS_VISIBLE_ELEMENT(lookup, *args, **kwargs):
  elements = lookup(*args, **kwargs)

  if len(elements) <= 0:
    T(False, msg = 'No such element: %s(%s, %s)' % (lookup, str(args), str(kwargs)))

  for el in elements:
    if el.visible:
      return

  T(False, msg = 'No such visible element: %s(%s, %s)' % (lookup, str(args), str(kwargs)))

def HAS_NOT_ELEMENT(lookup, *args, **kwargs):
  elements = lookup(*args, **kwargs)

  if len(elements) > 0:
    T(False, msg = 'Element exists: %s(%s, %s)' % (lookup, str(args), str(kwargs)))

def HAS_NOT_VISIBLE_ELEMENT(lookup, *args, **kwargs):
  elements = lookup(*args, **kwargs)

  if len(elements) <= 0:
    return

  for el in elements:
    if el.visible == True:
      T(False, msg = 'Element exists and is visible: %s(%s, %s)' % (lookup, str(args), str(kwargs)))

class _BrowserWrapper(object):
  def __init__(self, browser):
    super(_BrowserWrapper, self).__init__()

    self._browser = browser

  def __enter__(self):
    return self._browser

  def __exit__(self, type, value, tb):
    return False

class WebTestCase(TestCase):
  @classmethod
  def default_setup_class(cls):
    cls._appserver = tests.appserver.AppServer(*tests.appserver.AppServer.fetch_config('default_appserver'))
    cls._appserver.start()

  @classmethod
  def default_teardown_class(cls):
    if cls._appserver:
      cls._appserver.stop()

  @classmethod
  def setup_class(cls):
    super(WebTestCase, cls).setup_class()

    from testconfig import config
    cls._browser = _BrowserWrapper(splinter.Browser(config['web']['browser_driver']))

  @classmethod
  def teardown_class(cls):
    try:
      with cls._browser as B:
        B.quit()
    except Exception, e:
      pass

    cls._browser = None

    super(WebTestCase, cls).teardown_class()

  def __getattribute__(self, name):
    if name == 'browser':
      return self.__class__._browser

    return super(WebTestCase, self).__getattribute__(name)

  @classmethod
  def get_root_url(cls):
    if cls._appserver and cls._appserver.url:
      return cls._appserver.url

    from testconfig import config
    return config['web']['root_url']

  @classmethod
  def goto(cls, url, fail = True):
    with cls._browser as B:
      B.visit(url)
      return WaitUntil(BrowserHasURL(B, url)).wait(fail = fail)

  @classmethod
  def goto_login(cls):
    return cls.goto(urlparse.urljoin(cls.get_root_url(), '/login/'))

  @classmethod
  def goto_home(cls):
    return cls.goto(urlparse.urljoin(cls.get_root_url(), '/home/'))

  @classmethod
  def is_logged_in(cls):
    home_url = urlparse.urljoin(cls.get_root_url(), '/home/')

    with cls._browser as B:
      B.visit(home_url)
      WaitUntil(BrowserHasURL(B, home_url)).wait(fail = False)
      return B.url == home_url

  @classmethod
  def login(cls, username = None, password = None):
    if cls.is_logged_in():
      return

    from testconfig import config

    home_url = urlparse.urljoin(cls.get_root_url(), '/home/')

    username = username or config['web']['username']
    password = password or config['web']['password']

    with cls._browser as B:
      B.fill('username', username)
      B.fill('password', password)
      B.find_by_css('input.btn').first.click()
      WaitUntil(BrowserHasURL(B, urlparse.urljoin(cls.get_root_url(), '/home/'))).wait()

  @classmethod
  def logout(cls):
    if not cls.is_logged_in():
      return

    with cls._browser as B:
      B.find_link_by_href('/logout').first.click()
      WaitUntil(BrowserHasURL(B, urlparse.urljoin(cls.get_root_url(), '/login/'))).wait()

  @classmethod
  def relogin(cls, username = None, password = None):
    cls.logout()
    cls.login(username = username, password = password)
