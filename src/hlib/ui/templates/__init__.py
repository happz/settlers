__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import BeautifulSoup
import mako.exceptions
import mako.lookup
import mako.template
import os.path

import hlib.error

class Template(object):
  """
  Generic template class
  """

  def __init__(self, name, app = None, encoding = 'utf-8', indent = False):
    """
    Instantiate with C{Template(name, encoding = 'utf-8', indent = True)}

    @param name:		Name of template, usually filename.
    @type name:			C{string}
    @param encoding:		Output encoding. Default is C{utf-8}.
    @type encoding:		C{string}
    @param indent:		Whether to output indented and clean output. Default C{True}.
    @type indent:		C{bool}
    """

    super(Template, self).__init__()

    self.app			= app
    self.name			= name
    self.encoding		= encoding
    self.encoding_errors	= 'replace'
    self.indent			= indent

    self.params			= None
    self.template		= None

  # pylint: disable-msg=W0613
  def load(self, text = None):
    """
    Load template into memory. Do what is neccessary - precompile etc.
    """

    # pylint: disable-msg=R0201
    raise hlib.error.UnimplementedError(obj = Template)

  def do_render(self):
    """
    Do real render stuff
    """

    # pylint: disable-msg=R0201
    raise hlib.error.UnimplementedError(obj = Template)

  def render(self, params = None):
    """
    Prepare template to be rendered. Apply indent methods if required.

    @param params:		Params to pass into template.
    @type params:		C{dict} in form C{variable name}: C{variable value}
    @return:			Rendered template.
    @rtype:			C{unicode}
    """

    self.params = params or {}

    data = self.do_render()

#    if self.indent == True:
#      from bs4 import BeautifulSoup
#      soup = BeautifulSoup(data)
#      data = soup.prettify()

    return data

  @staticmethod
  def render_error():
    return ''

def simple_render(cls, imports, text, params):
  return cls('_simple_render_').load(''.join(['<%namespace file="' + i + '.mako" import="*"/>' for i in imports]) + text).render(params = params)
