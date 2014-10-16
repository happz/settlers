import tests.appserver
from tests.web import *

import random
import string

class TestCase(WebTestCase):
  @classmethod
  def setup_class(cls):
    super(TestCase, cls).setup_class()

    cls._appserver = tests.appserver.AppServer(*tests.appserver.AppServer.fetch_config('default_appserver'))
    cls._appserver.start()

  @classmethod
  def teardown_class(cls):
    if cls._appserver:
      cls._appserver.stop()

    super(TestCase, cls).teardown_class()

  @requires_login
  @requires_url('/chat/')
  def test_sanity(self):
    pass

  @requires_login
  @requires_url('/chat/')
  def test_add(self):
    post = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(64))

    with self.browser as B:
      # Get rid of any "Unread" tags
      B.reload()

      HAS_NOT_TEXT(B, post)
      HAS_NOT_VISIBLE_ELEMENT(B.find_by_css, 'span.chat-post-unread')

      B.fill('text', post)
      B.find_by_css('input.btn').first.click()
      PAUSE(10)

      # "Unread" tag should be visible
      HAS_VISIBLE_ELEMENT(B.find_by_css, 'span.chat-post-unread')
      HAS_TEXT(B, post)

