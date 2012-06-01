import json
import unittest
import urllib
import urllib2
import sys
import types
import cookielib

ROOT_URL = 'http://osadnici-test.happz.cz'
COOKIE_JAR = '/tmp/settlers-test-cookies.dat'

USERNAME		= 'happz'
PASSWORD		= 'heslo'

cookiejar = None

def setup():
  global cookiejar

  cookiejar = cookielib.MozillaCookieJar(COOKIE_JAR)

  try:
    cookiejar.load()

  except IOError:
    cookiejar.save()

def teardown():
  global cookiejar

  cookiejar = None

def do_query(url, data = None):
  url = ROOT_URL + url
  data = data or {}

  req = urllib2.Request(url, data = (urllib.urlencode(data) if data != None else None))
  cookiejar.add_cookie_header(req)

  res = urllib2.urlopen(req)

  cookiejar.extract_cookies(res, req)
  cookiejar.save()

  return (req, res)

def query_http_status(url, data = None):
  req, res = do_query(url, data = data)

  print res.info()

def query(url, data = None, json_expected = True):
  req, res = do_query(url, data = data)

  reply = res.read()

  if json_expected:
    reply = json.loads(reply)

  return reply

def check_json_reply(reply, expect):
  def __check_dict(d1, d2, prefix):
    for k, v1 in d1.iteritems():
      assert k in d2, 'key \'%s.%s\' not present' % (prefix, k)

      v2 = d2[k]

      if type(v1) in types.StringTypes and type(v2) in types.StringTypes:
        pass

      else:
        assert type(v1) == type(v2), 'type mismatch for key \'%s\': got %s, expected %s' % (k, type(v2), type(v1))

        if type(v1) == types.DictType:
          __check_dict(v1, v2, prefix + '.' + k)
          continue

      assert v1 == v2, 'reply[%s] = \'%s\', expected \'%s\'' % (k, unicode(v2).encode('ascii', 'replace'), v1)

#  print >> sys.stderr, reply
  try:
    __check_dict(expect, reply, '')
    __check_dict(reply, expect, '')

  except AssertionError, e:
    print >> sys.stderr, 'JSON reply: \'%s\'' % reply
    raise e

class TestCase(unittest.TestCase):
  pass
