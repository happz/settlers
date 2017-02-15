__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import logging
import syslog

import hlib.log.channels

class SysLogHandler(logging.Handler):
  def __init__(self, facility):
    self.facility = facility

    super(SysLogHandler, self).__init__()

  def emit(self, record):
    syslog.syslog(self.facility | 3, self.format(record))

class Channel(hlib.log.channels.Channel):
  def __init__(self, facility):
    super(Channel, self).__init__()

    self.sh = SysLogHandler(facility)
    self.sh.setLevel(logging.DEBUG)
    self.sh.setFormatter(logging.Formatter("%(message)s"))

  def log_message(self, record):
    self.sh.emit(record)

  def log_error(self, error):
    self.sh.emit(error.log_record)
