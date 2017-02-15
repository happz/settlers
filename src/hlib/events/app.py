__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2014, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

from hlib.events import Event

class AppEvent(Event):
  dont_store = True

  def __init__(self, app = None, *args, **kwargs):
    Event.__init__(self, *args, **kwargs)

    self.app = app

class Started(AppEvent):
  pass

Started.register()
