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

  def test_static(self):
    home_url = urlparse.urljoin(self.__class__.get_root_url(), '/static/status/500.html')

    self.__class__.goto(home_url)

    with self.browser as B:
      HAS_TITLE(B, 'Osadnici')
