from tests.web import *

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

  def test_login(self):
    self.login()

  @requires_login
  def test_logout(self):
    self.logout()
