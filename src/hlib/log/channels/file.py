__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import hlib.log.channels

class Channel(hlib.log.channels.StreamChannel):
  def __init__(self, path, *args, **kwargs):
    super(Channel, self).__init__(open(path, 'a'), *args, **kwargs)

    self.path		= path

  def flush(self):
    self.stream.flush()

  def close(self):
    self.stream.close()

  def reopen(self):
    self.stream.close()

    self.stream = open(self.path, 'a')
