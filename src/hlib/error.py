"""
Basic exception tree
"""

__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import logging
import sys
import syslog
import traceback
import types

def get_caller(back = 0):
  stack = traceback.extract_stack()

  i = -3 - back
  if abs(i) > len(stack):
    i = -len(stack)

  return stack[i]

def fmt_caller(back = 0):
  caller = get_caller(back = back + 1)
  return 'Called by "%s" on %s:%i ("%s")' % (caller[2], caller[0], caller[1], caller[3])

class BaseError(Exception):
  def __init__(self, msg = None, params = None, exception = None, exc_info = None, http_status = 500, reply_status = 500, dont_log = False, **kwargs):
    super(BaseError, self).__init__()

    self.msg = msg or '<Empty message>'
    self.params = params or {}
    self.exception = exception
    self.exc_info = exc_info

    self.http_status = http_status
    self.reply_status = reply_status

    self.params.update(kwargs)

    if self.exc_info:
      self.tb = traceback.extract_tb(self.exc_info[2])

    else:
      self.tb = traceback.extract_stack()[0:-1]

    self.name = self.exc_info and self.exc_info[0].__name__ or '<Unknown exception>'
    self.message = self.msg % self.params

    self.file = self.tb[-1][0]
    self.line = self.tb[-1][1]
    with open(self.file, 'r') as f:
      self.code = '%i. %s' % (self.line, f.readlines()[self.line - 1])

    self.log_record = logging.makeLogRecord({'name': 'settlers', 'level': syslog.LOG_ERR, 'pathname': self.file, 'lineno': self.line, 'msg': self.msg, 'args': self.params, 'exc_info': self.exc_info, 'func': None})

    self.dont_log = dont_log

  def __str__(self):
    return self.message

  def __unicode__(self):
    return unicode(self.message)

  def args_for_reply(self):
    return {}

def error_from_exception(e):
  if isinstance(e, BaseError):
    return e

  if len(e.args) != 0:
    _msg = []
    for t in e.args:
      if type(t) not in types.StringTypes:
        t = unicode(t)
      elif isinstance(t, str):
        t = unicode(t, 'utf-8')
      _msg.append(t)

    msg = u':'.join(_msg)

  elif len(e.message) != 0:
    msg = e.message

  elif hasattr(e, '_exceptions'):
    # pylint: disable-msg=W0212
    msg = e._exceptions[0][1].args[0]

  else:
    msg = repr(e)

  return BaseError(msg = msg, params = None, exception = e, exc_info = sys.exc_info())

class DieError(BaseError):
  """
  "Kill-me-now" exception - we want to exit and rollback db changes and we want it now. Nothing
  less, nothing more.
  """

  def __init__(self):
    """
    No arguments needed, we just hate this code.
    """

    super(DieError, self).__init__(msg = 'Die! Die! Die!')

class UnimplementedError(BaseError):
  """
  Exception that signals some function is left unimplemented yet.
  """

  @staticmethod
  def function_name(obj, frames):
    """
    Create a string naming the function n frames up on the stack.

    @todo:			DocString
    """

    # pylint: disable-msg=W0212
    fr = sys._getframe(frames + 1)
    co = fr.f_code
    return "%s.%s" % (obj.__class__, co.co_name)

  def __init__(self, obj = None):
    """
    @type obj:			C{callable object}
    @param obj:			Unimplemented function wrapper that called this function.
    """

    super(UnimplementedError, self).__init__('Unimplemented abstract method: %(method)s', params = {'method': UnimplementedError.function_name(obj, 1)})

class UnknownError(BaseError):
  pass

class TemporarilyDisabled(BaseError):
  pass

class InvalidInputError(BaseError):
  def __init__(self, invalid_field = None, **kwargs):
    super(InvalidInputError, self).__init__(**kwargs)

    self.dont_log = True
    self.invalid_field = invalid_field

  def args_for_reply(self):
    # pylint: disable-msg=W0621
    import hlib.api

    return {'form': hlib.api.Form(orig_fields = True, invalid_field = self.invalid_field)}

class AccessDeniedError(BaseError):
  def __init__(self, **kwargs):
    kwargs['reply_status']	= 401

    super(AccessDeniedError, self).__init__(**kwargs)

class NoSuchUserError(InvalidInputError):
  def __init__(self, username, **kwargs):
    super(NoSuchUserError, self).__init__(reply_status = 403, msg = 'No such user "%(username)s"', username = username, **kwargs)

class InvalidAuthError(BaseError):
  def __init__(self, **kwargs):
    super(InvalidAuthError, self).__init__(reply_status = 401, dont_log = True, **kwargs)

class InconsistencyError(BaseError):
  def __init__(self, **kwargs):
    super(InconsistencyError, self).__init__(reply_status = 402, **kwargs)

class InvalidOutputError(BaseError):
  def __init__(self, **kwargs):
    super(InvalidOutputError, self).__init__(reply_status = 500, msg = 'Invalid output produced by handler', **kwargs)

class ClientSideError(BaseError):
  pass
