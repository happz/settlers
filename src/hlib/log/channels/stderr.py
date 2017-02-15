__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import sys

import hlib.log.channels

class Channel(hlib.log.channels.StreamChannel):
  def __init__(self, *args, **kwargs):
    super(Channel, self).__init__(sys.stderr, *args, **kwargs)
