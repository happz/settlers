<%!

import re
import hlib
import hlib.i18n

import hruntime

def gettext(s):
  return hlib.i18n.gettext(s).encode('ascii', 'xmlcharrefreplace')

class Element(object):
  def __init__(self, name, id = None, classes = None, style = None):
    super(Element, self).__init__()

    self.name			= name
    self.id			= id
    self.raw_id			= id
    self.classes		= classes or []
    self.style			= style

  def attrs(self):
    attrs = {}

    if self.id != None:
      attrs['id'] = self.id

    if self.classes != None and len(self.classes) > 0:
      attrs['class'] = ' '.join(self.classes)

    if self.style != None:
      attrs['style'] = self.style

    return attrs

  def start(self):
    attrs = self.attrs()

    if self.name == 'input':
      fmt = '<%s %s />'
    else:
      fmt = '<%s %s>'

    return fmt % (self.name, ' '.join(['%s="%s"' % (k, v) for k, v in attrs.iteritems()]))

  def end(self):
    if self.name == 'input':
      return ''

    return '</%s>' % self.name

class Form(Element):
  def __init__(self, action = None, method = None, horizontal = True, legend = None, validate = False, enctype = None, *args, **kwargs):
    super(Form, self).__init__('form', *args, **kwargs)

    self.validate		= validate

    self.action			= action or ''
    self.method			= method or 'post'
    self.legend			= legend
    self.enctype    = enctype

    self.current_element	= None

    if self.id != None:
      self.id = self.id + '_form'

    if horizontal:
      self.classes.append('form-horizontal')

    hruntime.ui_form = self

  def attrs(self):
    attrs = super(Form, self).attrs()

    attrs['action'] = self.action
    attrs['method'] = self.method

    if self.validate:
      attrs['data-validate'] = 'true'

    if self.enctype:
      attrs['enctype'] = self.enctype

    return attrs

  def start(self):
    s = super(Form, self).start()

    s += '<fieldset>'

    if self.legend != None:
      s += '<legend>' + gettext(self.legend) + '</legend>'

    s += '<div class="alert fade in hide form-info"><strong></strong><p></p></div>'

    return s

  def end(self):
    hruntime.ui_form = None

    return '</fieldset>' + super(Form, self).end()

class InputElement(Element):
  def __init__(self, name, form_name = None, label = None, size = None, value = None, disabled = False, required = False, help = None, placeholder = None, minimal_struct = False, validators = None, validation_message = None, autocomplete = False, accept = None, *args, **kwargs):
    super(InputElement, self).__init__(name, *args, **kwargs)

    self.form_name		= form_name
    self.label			= label
    self.value			= value
    self.disabled		= disabled
    self.required		= required
    self.help			= help
    self.placeholder		= placeholder
    self.minimal_struct		= minimal_struct
    self.autocomplete = autocomplete
    self.accept = accept

    if self.form_name != None:
      self.id			= hruntime.ui_form.raw_id + '_' + self.form_name

    if size:
      self.classes.append('input-' + size)

    self.validators = None
    self.validation_message = validation_message or 'Please enter a value'

    if validators:
      self.validators = {}

      matcher = r'(\w+)(?:="(.*?)")?'
      matches = re.findall(matcher, validators.strip())

      for validator in matches:
        if len(validator[1]) == 0:
          self.validators['data-%s' % validator[0]] = 'true'
        else:
          self.validators['data-%s' % validator[0]] = validator[1]

  def attrs(self):
    attrs = super(InputElement, self).attrs()

    if self.form_name != None:
      attrs['name']		= self.form_name

    if self.value != None:
      attrs['value']		= self.value

    if self.disabled:
      attrs['disabled']		= 'disabled'

    if self.placeholder != None:
      attrs['placeholder']	= self.placeholder

    if self.validators:
      attrs.update(self.validators)
      attrs['data-error-message'] = self.validation_message

    if self.autocomplete:
      attrs['autocomplete'] = 'on'

    if self.accept:
      attrs['accept'] = self.accept

    return attrs

  def start(self):
    if self.minimal_struct:
      s = ''

    else:
      s = '<div class="control-group">'

      if self.label != None:
        s += '<label class="control-label" for="' + hruntime.ui_form.raw_id + '_' + self.form_name + '">' + gettext(self.label) + '</label>'

      s += '<div class="controls">'

    s += super(InputElement, self).start()

    if self.minimal_struct == False and self.help != None:
      s += '<span class="help-block">' + gettext(self.help) + '</span>'

    return s

  def end(self):
    return super(InputElement, self).end() + ('' if self.minimal_struct else '</div></div>')

class Select(InputElement):
  def __init__(self, default = False, *args, **kwargs):
    super(Select, self).__init__('select', *args, **kwargs)

    self.default		= default

    hruntime.ui_form.current_element = self
  
  def start(self):
    s = super(Select, self).start()

    if self.default != False:
      s += '<option value="" selected="selected">' + gettext(self.default) + '</option>'

    return s

class SelectOption(Element):
  def __init__(self, value = None, selected = None, label = None, *args, **kwargs):
    super(SelectOption, self).__init__('option', *args, **kwargs)

    self.value			= value
    self.label			= label
    self.selected		= selected

  def attrs(self):
    attrs = super(SelectOption, self).attrs()

    if self.value != None:
      attrs['value'] = self.value

    if self.selected != None and self.selected != False:
      attrs['selected'] = 'selected'

    return attrs

  def start(self):
    s = super(SelectOption, self).start()

    if self.label != None:
      s += gettext(self.label)

    return s

class Input(InputElement):
  def __init__(self, name = 'input', type = None, *args, **kwargs):
    super(Input, self).__init__('input', *args, **kwargs)

    self.type			= type

  def attrs(self):
    attrs = super(Input, self).attrs()

    if self.type != None:
      attrs['type']		= self.type

    return attrs

class Textarea(InputElement):
  def __init__(self, cols = 90, rows = 7, *args, **kwargs):
    super(Textarea, self).__init__(name = 'textarea', *args, **kwargs)

    self.cols			= cols
    self.rows			= rows

  def attrs(self):
    attrs = super(Textarea, self).attrs()

    attrs['cols']		= self.cols
    attrs['rows']		= self.rows

    if 'value' in attrs:
      del attrs['value']

    return attrs

  def start(self):
    s = super(Textarea, self).start()

    if self.value != None:
      s += self.value

    return s

class Button(Input):
  def __init__(self, *args, **kwargs):
    if 'value' in kwargs:
      kwargs['value'] = gettext(kwargs['value'])

    super(Button, self).__init__(*args, **kwargs)

    self.classes.append('btn')

%>

<%def name="script(path)">
  <script type="text/javascript" src="${path}${hlib.version_stamp(path)}"></script>
</%def>

<%def name="style(path)">
  <link rel="stylesheet" href="${path}${hlib.version_stamp(path)}" type="text/css" />
</%def>

<%def name="ui_page_header(header)">
  <div class="row-fluid page-header"><h2>${_(header)}</h2></div>
</div>
<div class="container-fluid">
</%def>

<%def name="ui_section_header(id, header)">
  <section id="${id}"><div class="page-header"><h3>${_(header)}</h3></div>
</%def>

<%def name="ui_row_start(offset = None, span = None, classes = None)">
  <%
    span = span or 12
    offset = offset or (12 - span) / 2
    classes = classes or []
  %>
  <div class="row-fluid"><div class="offset${offset} span${span} ${' '.join(classes)}">
</%def>

<%def name="ui_row_end()">
  </div></div>
</%def>

<%def name="ui_form_start(*args, **kwargs)">
  ${Form(*args, **kwargs).start()}
</%def>

<%def name="ui_form_end()">
  ${hruntime.ui_form.end()}
</%def>

<%def name="ui_select_start(*args, **kwargs)">
  ${Select(*args, **kwargs).start()}
</%def>

<%def name="ui_select_end()">
  ${hruntime.ui_form.current_element.end()}
</%def>

<%def name="ui_select_option(*args, **kwargs)">
  <%
    so = SelectOption(*args, **kwargs)
  %>
  ${so.start()}${so.end()}
</%def>

<%def name="ui_input(*args, **kwargs)">
  <%
    i = Input(*args, **kwargs)
  %>
  ${i.start()}${i.end()}
</%def>

<%def name="ui_textarea(*args, **kwargs)">
  <%
    t = Textarea(*args, **kwargs)
  %>
  ${t.start()}${t.end()}
</%def>

<%def name="ui_submit(*args, **kwargs)">
  <%
    b = Button(type = 'submit', *args, **kwargs)
  %>
  ${b.start()}${b.end()}
</%def>
