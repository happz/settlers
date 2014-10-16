import datetime
import time

import hlib.tests
import tests

class AbstractWait(object):
  DEFAULT_TIMEOUT = 10
  DEFAULT_DELAY = 0.5

  def __init__(self, cond, timeout = None, delay = None):
    super(AbstractWait, self).__init__()

    self.cond = cond
    self.timeout = timeout or AbstractWait.DEFAULT_TIMEOUT
    self.delay = delay or AbstractWait.DEFAULT_DELAY

  def condition_test(self):
    raise hlib.error.UnimplementedError(obj = AbstractWait)

  def wait(self, fail = True):
    wait_until = datetime.datetime.now() + datetime.timedelta(seconds = self.timeout)

    while True:
      if self.condition_test():
        return True

      current_time = datetime.datetime.now()
      if current_time >= wait_until:
        break

      time.sleep(self.delay)

    if fail:
      assert False, 'Waiting failed: condition="%s"' % str(self.cond)

    return False

class Condition(object):
  def __init__(self):
    super(Condition, self).__init__()

#
# "Wait for ..." classes
#
class WaitUntil(AbstractWait):
  def condition_test(self):
    return self.cond()

class WaitWhile(AbstractWait):
  def condition_test(self):
    return not self.cond()

#
# Browser conditions
#
class BrowserCondition(Condition):
  def __init__(self, browser):
    super(BrowserCondition, self).__init__()

    self.browser = browser

class BrowserHasURL(BrowserCondition):
  def __init__(self, browser, url):
    super(BrowserHasURL, self).__init__(browser)

    self.url = url

  def __str__(self):
    return 'Browser in on page with URL %s' % self.url

  def __call__(self):
    return self.browser.url == self.url

class BrowserHasElement(BrowserCondition):
  def __init__(self, browser, lookup, *args):
    super(BrowserHasURL, self).__init__(browser)

    self.lookup = lookup
    self.args = args

  def __str__(self):
    return 'Browser has element %s(%s)' % (self.lookup, self.args)

  def __call__(self):
    return getattr(self.browser, self.lookup)(*self.args)
