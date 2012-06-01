import tests.handlers

import random

from tests import query, check_json_reply

class settings_MyColor(tests.handlers.TestCase):
  VALID_KINDS		= ['settlers']
  VALID_COLORS		= ['pink', 'purple', 'dark_green', 'black', 'brown', 'light_blue', 'orange', 'green', 'dark_blue', 'red']

  def get_rand_kind(self):
    return self.VALID_KINDS[0]

  def get_rand_color(self):
    i = random.randint(0, len(self.VALID_COLORS) - 1)
    return self.VALID_COLORS[i]

  def test_empty_submit(self):
    reply = query('/settings/color')

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'color',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_invalid_param_kind(self):
    i = random.randint(-20, 20)

    reply = query('/settings/color', data = {'__kind': i})

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	None,
        'orig_fields':		{
          '__kind':		'%i' % i
        }
      },
      'error':			{
        'message':		'The input field \'__kind\' was not expected.',
        'params':		{
        }
      }
    })

  def test_empty_kind(self):
    reply = query('/settings/color', data = {'kind': ''})

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'color',
        'orig_fields':		{
          'kind':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_empty(self):
    reply = query('/settings/color', data = {'kind': '', 'color': ''})

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'color',
        'orig_fields':		{
          'color':		'',
          'kind':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_malformed_kind_int(self):
    i = random.randint(-20, -10)
    color = self.get_rand_color()

    reply = query('/settings/color', data = {'kind': i, 'color': color})
    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'kind',
        'orig_fields':		{
          'kind':		'%i' % i,
          'color':		color
        }
      },
      'error':			{
        'message':		'Value must be one of: settlers (not u\'%i\')' % i,
        'params':		{
        }
      }
    })

  def test_malformed_kind_string(self):
    color = self.get_rand_color()

    reply = query('/settings/color', data = {'kind': 'foobar', 'color': color})
    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'kind',
        'orig_fields':		{
          'kind':		'foobar',
          'color':		color
        }
      },
      'error':			{
        'message':		'Value must be one of: settlers (not u\'foobar\')',
        'params':		{
        }
      }
    })

  def test_malformed_color_int(self):
    kind = self.get_rand_kind()
    color = random.randint(-20, -10)

    reply = query('/settings/color', data = {'kind': kind, 'color': color})
    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'color',
        'orig_fields':		{
          'kind':		kind,
          'color':		'%i' % color
        }
      },
      'error':			{
        'message':		'Value must be one of: pink; purple; dark_green; black; brown; light_blue; orange; green; dark_blue; red (not u\'%i\')' % color,
        'params':		{
        }
      }
    })

  def test_malformed_color_string(self):
    kind = self.get_rand_kind()
    color = self.get_rand_color()

    reply = query('/settings/color', data = {'kind': kind, 'color': 'foobar'})
    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'color',
        'orig_fields':		{
          'kind':		kind,
          'color':		'foobar'
        }
      },
      'error':			{
        'message':		'Value must be one of: pink; purple; dark_green; black; brown; light_blue; orange; green; dark_blue; red (not u\'foobar\')',
        'params':		{
        }
      }
    })
