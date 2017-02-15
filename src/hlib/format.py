"""
Methods for formating text output.
"""

__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import markdown2

# pylint: disable-msg=W0613
def tagize(text):
  """
  Process tags in text.

  @type text:			C{string}
  @param text:			Text to be processed.
  """

  return markdown2.markdown(text)
