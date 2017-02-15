__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import sys
import types
import urllib

import hlib
import hlib.auth
import hlib.error
import hlib.http
import hlib.i18n
import hlib.input
import hlib.log
import hlib.server
import hlib.ui.templates.Mako

import hruntime  # @UnresolvedImport

__all__ = ['tag_fn', 'prohibited', 'require_login', 'require_admin', 'require_write', 'require_hosts',
           'page',
           'GenericHandler']

class IORegime(object):
  @staticmethod
  def check_session():
    return

  @staticmethod
  def run_handler():
    return

  @staticmethod
  def redirect(url):
    return

class PageIORegime(object):
  @staticmethod
  def check_session():
    hlib.auth.check_session()

  @staticmethod
  def run_handler():
    hruntime.response.headers['Content-Type'] = 'text/html; charset=utf-8'

    try:
      hlib.input.validate()

      return hruntime.request.handler(**hruntime.request.params)

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

def tag_fn_prep(fn):
  if not hasattr(fn, 'config'):
    setattr(fn, 'config', dict())

def tag_fn(fn, tag, value):
  tag_fn_prep(fn)

  if tag not in fn.config:
    fn.config[tag] = value

  return fn

def tag_fn_check(fn, tag, default):
  if not hasattr(fn, 'config'):
    return default

  return fn.config.get(tag, default)

prohibited			= lambda f: tag_fn(f, 'prohibited', True)
require_login			= lambda f: tag_fn(f, 'require_login', True)
require_admin			= lambda f: tag_fn(f, 'require_admin', True)
require_write			= lambda f: tag_fn(f, 'require_write', True)

def require_hosts(get_hosts = None):
  def _require_hosts(fn):
    tag_fn(fn, 'require_hosts', get_hosts)
    return fn
  return _require_hosts

page				= lambda f: tag_fn(f, 'ioregime', PageIORegime)

def enable_write():
  require_write(hruntime.request.handler)

def gettext(s):
  return hlib.i18n.gettext(s).encode('ascii', 'xmlcharrefreplace')

def prepare_template_params(params = None):
  real_params = GenericHandler.PARAMS.copy()
  params = params or {}
  real_params.update(params)

  real_params['root']     = hruntime.root
  real_params['user']     = hruntime.user
  real_params['server']   = hruntime.server
  real_params['_']        = gettext
  real_params['title']    = hruntime.app.config['title']
  real_params['basepath'] = hruntime.request.base
  
  real_params['_q']       = urllib.quote

  return real_params
  
class GenericHandler(object):
  PARAMS = {}

  def __init__(self):
    super(GenericHandler, self).__init__()

  def generate(self, template, params = None):
    params = prepare_template_params(params = params)

    params['handler'] = self

    indent = True
    if hruntime.user != None and hruntime.user.is_admin:
      indent = True

    t = hlib.ui.templates.Mako.Template(template, indent = indent, app = hruntime.app).load()
    return t.render(params = params)
