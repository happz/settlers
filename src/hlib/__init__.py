__author__		= 'Milos Prchlik'
__copyright__		= 'Copyright 2010 - 2012, Milos Prchlik'
__contact__		= 'happz@happz.cz'
__license__		= 'http://www.php-suit.com/dpl'
__version__		= '3.0-rc1'

import htmlentitydefs
import os
import os.path
import random
import re
import sys
import threading
import time
import traceback
import types

__version__ = '3.0-rc1'

import hlib.runtime

# pylint: disable-msg=W0201
PATH = os.path.dirname(__file__)

#def url(path = None):
#  return 'http://' + hruntime.request.base + path

def unescape(text):
  def fixup(m):
    text = m.group(0)
    if text[:2] == "&#":
      try:
        if text[:3] == "&#x":
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
    return text
  return re.sub(r"&#?\w+;", fixup, text)
