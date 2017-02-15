"""
Support for simple paging.
"""

__author__              = 'Milos Prchlik'
__copyright__           = 'Copyright 2010 - 2012, Milos Prchlik'
__contact__             = 'happz@happz.cz'
__license__             = 'http://www.php-suit.com/dpl'

import hlib.api
import hlib.input

class ValidatePage(hlib.input.SchemaValidator):
  """
  Input validator

  @ivar start:    Starting offset of requested page
  @type start:    L{input.Validator}
  @ivar length:    Number of items on requested page
  @type length:    L{input.Validator}
  """
  start  = hlib.input.validator_factory(hlib.input.NotEmpty, hlib.input.Int(min = 0))
  length = hlib.input.validator_factory(hlib.input.NotEmpty, hlib.input.Int(min = 1))

class Page(hlib.api.ApiJSON):
  """
  List of items on one page.

  @ivar cnt_total:   Number of items that are available.
  @type cnt_total:   C{int}
  @ivar cnt_display: Number of records in current page.
  @type cnt_display: C{int}
  @ivar records:     list of items in current page.
  @type records:     C{list}
  """

  def __init__(self):
    super(Page, self).__init__(['cnt_total', 'cnt_display', 'records', 'last_access'])

    self.cnt_total              = 0
    self.cnt_display            = 0
    self.records                = []
    self.last_access            = None

class Pageable(object):
  def __init__(self, default_length = None):
    """
    Object used to get pages of items from any resource. Use as a parent of custom class,
    and implement C{record_to_api} and C{get_records} methods.

    @param default_length: Number of items of requested page, when L{Pageable.get_page} is called without C{length} specified.
    @type default_length: C{int}
    """

    super(Pageable, self).__init__()

    self.default_length = default_length if default_length != None else 20

  def get_records(self, start, length):
    """
    Return list of records.

    @param start: Offset of first item of requested page. If not set, C{0} is used.
    @type start:  C{int}
    @param length: Number of items of requested page. If not set, C{default_length} as set when creating C{Pageable} is used.
    @type length: C{int}
    @return: Tuple (C{list of records}, C{number of all items available}, C{None})
    @rtype: C{(list, int)}
    """

    # pylint: disable-msg=W0613
    return ([], 0, None)
    
  def get_page(self, start = None, length = None):
    """
    Returns L{Page} instance, filled with items of requested page. For every item on page L{Pageable.record_to_api} method
    is called and result is appended to L{Page.records}.

    @param start: Offset of first item of requested page. If not set, C{0} is used.
    @type start:  C{int}
    @param length: Number of items of requested page. If not set, C{default_length} as set when creating C{Pageable} is used.
    @type length: C{int}
    @rtype: filled L{Page} instance
    """

    start = start if start != None else 0
    length = length if length != None else self.default_length

    reply = Page()

    records, cnt_total, last_access = self.get_records(start, length)

    for record in records:
      reply.records.append(record.to_api())

    reply.cnt_total = cnt_total
    reply.cnt_display = len(records)
    reply.last_access = last_access

    return reply
