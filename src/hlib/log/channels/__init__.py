__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import types

import hlib.ui.templates.Mako

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class Channel(object):
  def do_log_message(self, msg):
    pass

  def log_message(self, record):
    msg = type(record) not in types.StringTypes and (record.msg % record.args) or record

    self.do_log_message(msg)

  def log_error(self, error):
    pass

  def close(self):
    pass

  def reopen(self):
    pass

  def flush(self):
    pass

class StreamChannel(Channel):
  def __init__(self, stream, *args, **kwargs):
    super(StreamChannel, self).__init__(*args, **kwargs)

    self.stream		= stream

  def do_log_message(self, msg):
    msg = msg.decode('utf-8', 'replace').encode('ascii', 'replace')
    self.stream.write(msg + '\n')
    self.stream.flush()

  def log_error(self, error):
    t = hlib.ui.templates.Mako.Template('hlib_error_plain.mako', indent = False, app = hruntime.app).load()
    self.do_log_message(t.render(params = {'error': error}).strip())
