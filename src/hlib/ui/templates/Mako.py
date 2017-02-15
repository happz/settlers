"""
Mako templates

@version:                       1.0

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import mako.exceptions
import mako.lookup
import mako.template
import types

import hlib.locks
import hlib.ui.templates

class Template(hlib.ui.templates.Template):
  """
  Mako template class.

  Based on Mako template library U{http://www.makotemplates.org/}
  """

  @staticmethod
  def init_app(app):
    app.mako_loader = mako.lookup.TemplateLookup(directories = app.config['templates.dirs'], module_directory = app.config['templates.tmp_dir'], filesystem_checks = True, input_encoding = 'utf-8', output_encoding = 'utf-8')

    orig_get_template = app.mako_loader.get_template
    app.mako_loader.loader_lock = hlib.locks.RLock(name = 'Mako template loader lock')

    def patched_get_template(self, uri):
      with self.loader_lock:
        return orig_get_template(uri)

    patched_get_template = types.MethodType(patched_get_template, app.mako_loader, app.mako_loader.__class__)
    app.mako_loader.get_template = patched_get_template

  def __init__(self, *args, **kwargs):
    super(Template, self).__init__(*args, **kwargs)

  def load(self):
    self.template = self.app.mako_loader.get_template(self.name)
    return self

  def create(self, text):
    self.template = mako.template.Template(text = text, lookup = self.app.loader, input_encoding = self.encoding, output_encoding = self.encoding)
    return self

  def do_render(self):
    return self.template.render(**self.params)

  @staticmethod
  def render_error():
    return mako.exceptions.html_error_template().render()
