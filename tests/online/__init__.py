import json
import unittest
import urllib
import urllib2
import sys
import types
import cookielib

import tests

class TestCase(tests.TestCase):
  cookiejar = None

  def setUp(self):
    tests.TestCase.setUp(self)

    self.cookiejar = None

    if not TestCase.cookiejar:
      cookiejar = cookielib.MozillaCookieJar(self.config.get('online', 'cookie_jar'))

      try:
        cookiejar.load()

      except IOError:
        cookiejar.save()

      TestCase.cookiejar = cookiejar

    self.cookiejar = TestCase.cookiejar

  def do_query(self, url, data = None):
    url = self.config.get('online', 'root_url') + url
    data = data or {}

    req = urllib2.Request(url, data = (urllib.urlencode(data) if data != None else None))
    TestCase.cookiejar.add_cookie_header(req)

    res = urllib2.urlopen(req)

    self.cookiejar.extract_cookies(res, req)
    self.cookiejar.save()

    return (req, res)

  def query_http_status(self, url, data = None):
    req, res = self.do_query(url, data = data)

    print res.info()

  def query(self, url, data = None, json_expected = True):
    req, res = self.do_query(url, data = data)

    reply = res.read()

    if json_expected:
      reply = json.loads(reply)

    return reply
