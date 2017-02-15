__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import functools
import logging
import sys
import syslog
import time
import traceback
import threading

import hlib.locks

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

def make_record(message, params = None, level = None):
  params = {
    'name':     'settlers',
    'level':    level and level or syslog.LOG_ERR,
    'pathname': None,
    'lineno':   None,
    'msg':      message,
    'args':     params and params or tuple(),
    'exc_info': None,
    'func':     None
  }

  return logging.makeLogRecord(params)

def log_msg(msg, channels, flush = False):
  for c in channels:
    c.log_message(msg)

    if flush:
      c.flush()

def log_params():
  import hlib.server

  def __response_api_status():
    res = hruntime.response

    if not res.api_response:
      return '-'
    if not hasattr(res.api_response, 'status'):
      return '/'

    return res.api_response.status

  return {
    'tid':			hruntime.tid,
    'stamp':			hruntime.localtime,
    'date':			time.strftime('%d/%m/%Y', hruntime.localtime),
    'time':			time.strftime('%H:%M:%S', hruntime.localtime),
    'request_line':		hruntime.request.requested_line,
    'request_ip':		hlib.server.ips_to_str(hruntime.request.ips),
    'request_user':		hruntime.session.name if hruntime.session != None and hasattr(hruntime.session, 'authenticated') and hasattr(hruntime.session, 'name') else '-',
    'request_agent':		hruntime.request.headers.get('User-Agent', '-'),
    'response_status':		hruntime.response.status,
    'response_length':		hruntime.response.output_length != None and hruntime.response.output_length or 0,
    'response_api_status': __response_api_status(),
    'session_id':		hruntime.session.sid if hruntime.session != None else None
  }

def log_error(e):
  if e.dont_log == True:
    print >> sys.stderr, 'Skipped exception: \'%s\'' % unicode(e).encode('ascii', 'replace')
    return

  print >> sys.stderr, unicode(e).encode('ascii', 'replace')

  for c in hruntime.app.channels.error:
    c.log_error(e)

def log_dbg(msg):
  log_msg('%s - %s' % (hruntime.tid, msg), hruntime.app.channels.error)

_transaction_log_lock = hlib.locks.RLock(name = 'Transaction log')
def log_transaction(transaction, state, *args, **kwargs):
  if hruntime.user:
    kwargs['user'] = hruntime.user.name.encode('ascii', 'replace')

  kwargs['stamp'] = time.time()
  kwargs['state'] = transaction.status

  tb = traceback.extract_stack()
  if len(tb) >= 7:
    kwargs['tb'] = '[%s]' % ', '.join(['%s:%s' % ('/'.join([tb[i][0].split('/')[-2], tb[i][0].split('/')[-1]]), tb[i][1]) for i in range(-4, -7, -1)])

  args = ' '.join([str(arg) for arg in args])
  kwargs = ' '.join(['%s=%s' % (k, v) for k, v in kwargs.items()])

  transaction = id(transaction)

  global _transaction_log_lock
  with _transaction_log_lock:
    log_msg('%s: %s %s %s' % (transaction, state, args, kwargs), hruntime.app.channels.transactions, flush = True)
