__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class Cookie(object):
  """
  Represents 1 HTTP cookie and its properties, such as value and max age.
  """

  def __init__(self, name, value = None, max_age = None, path = None, server = None):
    """
    @type name:			C{string}
    @param name:		Name of cookie
    @type value:		C{string}
    @param value:		Value of cookie. Default is empty string
    @type max_age:		C{int}
    @param max_age:		Maximal age of cookie, in seconds. If not specified, default set for server or global default will be used.
    @type path:			C{string}
    @param path:		Path this cookie refers to. Default is web root, "C{/}".
    """

    super(Cookie, self).__init__()

    self.server			= server
    self.name			= name
    self.value			= value and str(value) or ''
    self.max_age		= int(max_age or (self.server and hasattr(self.server, 'cookie_max_age') and self.server.cookie_max_age))
    self.path			= path or '/'

  def __repr__(self):
    return 'hlib.cookies.Cookie(\'%s\', value = \'%s\', max_age = %i, path = \'%s\')' % (self.name, self.value, self.max_age, self.path)

  def set(self):
    """
    Adds this cookie to HTTP response.
    """

    hruntime.response.cookies[self.name] = self

  def delete(self):
    """
    Instructs client to remove this cookie from his storage, by setting Max-Age attribute to 0.
    """

    self.value			= '_deleted_'
    self.max_age		= 0

    self.set()
