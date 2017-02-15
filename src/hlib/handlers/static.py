import mimetypes
import os
import os.path
import posixpath
import urllib
import sys

import hlib.handlers

import hruntime

class StaticIORegime(hlib.handlers.IORegime):
  @staticmethod
  def check_session():
    hlib.auth.check_session()

  @staticmethod
  def run_handler():
    try:
      return hruntime.request.handler()

    except hlib.http.Redirect, e:
      hruntime.db.doom()
      raise e

    except Exception, e:
      hruntime.db.doom()

      e = hlib.error.error_from_exception(e)
      hlib.log.log_error(e)

    return ''

  @staticmethod
  def redirect(url):
    res = hruntime.response

    res.status = 301 
    res.output = None
    res.headers['Location'] = url

    if 'Content-Type' in res.headers:
      del res.headers['Content-Type']

static = lambda f: hlib.handlers.tag_fn(f, 'ioregime', StaticIORegime)

class StaticHandler(object):
  if not mimetypes.inited:
    mimetypes.init()

  extensions_map = mimetypes.types_map.copy()
  extensions_map.update({
    '': 'application/octet-stream', # Default
  })

  def __init__(self):
    super(StaticHandler, self).__init__()

  def translate_path(self, path):
    path = path.split('?',1)[0]
    path = path.split('#',1)[0]
    path = posixpath.normpath(urllib.unquote(path))
    words = path.split('/')
    words = filter(None, words)

    path = hruntime.app.config.get('static.root')

    for word in words:
      drive, word = os.path.splitdrive(word)
      head, word = os.path.split(word)
      if word in (os.curdir, os.pardir): continue
      path = os.path.join(path, word)

    return path

  def guess_type(self, path):
    base, ext = posixpath.splitext(path)

    if ext in self.extensions_map:
      return self.extensions_map[ext]

    ext = ext.lower()
    if ext in self.extensions_map:
      return self.extensions_map[ext]
    else:
      return self.extensions_map['']

  @static
  def generate(self, _version_stamp = None):
    req = hruntime.request
    res = hruntime.response

    path = self.translate_path(req.requested)
    content_type = self.guess_type(path)

    sys.stdout.flush()

    try:
      res.source_file = open(path, 'rb')
    except IOError:
      res.status = 404
      res.output = None
      return

    stat = os.fstat(res.source_file.fileno())

    res.status = 200
    res.headers['Content-Type'] = content_type
    res.headers['Content-Length'] = stat[6]
    res.headers['Last-Modified'] = hlib.http.stamp_to_string(stat.st_mtime)

    return None
