"""
"""

from tests.online import TestCase
from tests import cmp_json_dicts

import random

class Email(TestCase):
  def test_empty_submit(self):
    reply = self.query('/settings/email')
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'email',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_invalid_param(self):
    i = random.randint(-20, 20)

    reply = self.query('/settings/email', data = {'__email': '%s' % i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	None,
        'orig_fields':		{
          '__email':		'%s' % i
        }
      },
      'error':			{
        'message':		'The input field \'__email\' was not expected.',
        'params':		{}
      }
    })

  def test_empty_action(self):
    reply = self.query('/settings/email', data = {'email': ''})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'email',
        'orig_fields':		{
          'email':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_malformed_string(self):
    reply = self.query('/settings/email', data = {'email': 'foobar'})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'email',
        'orig_fields':		{
          'email':		'foobar'
        }
      },
      'error':			{
        'message':		'An email address must contain a single @',
        'params':		{
        }
      }
    })

  def test_malformed_float(self):
    reply = self.query('/settings/email', data = {'email': 3.14})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'email',
        'orig_fields':		{
          'email':		'3.14'
        }
      },
      'error':			{
        'message':		'An email address must contain a single @',
        'params':		{
        }
      }
    })

  def test_proper(self):
    reply = self.query('/settings/email', data = {'email': self.config.get('online', 'email')})
    cmp_json_dicts(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'email':		self.config.get('online', 'email')
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })

class AfterPassTurn(TestCase):
  def test_empty_submit(self):
    reply = self.query('/settings/after_pass_turn')
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'action',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_invalid_param(self):
    i = random.randint(-20, 20)

    reply = self.query('/settings/after_pass_turn', data = {'__action': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	None,
        'orig_fields':		{
          '__action':		'%i' % i
        }
      },
      'error':			{
        'message':		'The input field \'__action\' was not expected.',
        'params':		{}
      }
    })

  def test_empty_action(self):
    reply = self.query('/settings/after_pass_turn', data = {'action': ''})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'action',
        'orig_fields':		{
          'action':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_malformed_string(self):
    reply = self.query('/settings/after_pass_turn', data = {'action': 'foobar'})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'action',
        'orig_fields':		{
          'action':		'foobar'
        }
      },
      'error':			{
        'message':		'Please enter an integer value',
        'params':		{
        }
      }
    })

  def test_malformed_float(self):
    reply = self.query('/settings/after_pass_turn', data = {'action': 3.14})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'action',
        'orig_fields':		{
          'action':		'3.14'
        }
      },
      'error':			{
        'message':		'Please enter an integer value',
        'params':		{
        }
      }
    })

  def test_malformed_oor(self):
    i = random.randint(-20, -5)

    reply = self.query('/settings/after_pass_turn', data = {'action': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'action',
        'orig_fields':		{
          'action':		'%i' % i
        }
      },
      'error':			{
        'message':		'Value must be one of: 0; 1; 2 (not %i)' % i,
        'params':		{
        }
      }
    })

  def test_random(self):
    i = random.randint(0, 2)

    reply = self.query('/settings/after_pass_turn', data = {'action': i})
    cmp_json_dicts(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'action':		i
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })

class PerTablePage(TestCase):
  VALID_INPUTS		= range(10, 61, 10)

  def get_rand_input(self):
    i = random.randint(0, len(self.VALID_INPUTS) - 1)
    return self.VALID_INPUTS[i]

  def test_empty_submit(self):
    reply = self.query('/settings/per_page')
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'per_page',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_invalid_param(self):
    i = random.randint(-20, 20)

    reply = self.query('/settings/per_page', data = {'__per_page': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	None,
        'orig_fields':		{
          '__per_page':		'%i' % i
        }
      },
      'error':			{
        'message':		'The input field \'__per_page\' was not expected.',
        'params':		{
        }
      }
    })

  def test_empty(self):
    reply = self.query('/settings/per_page', data = {'per_page': ''})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'per_page',
        'orig_fields':		{
          'per_page':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_malformed_int(self):
    while True:
      i = random.randint(-100, 100)
      if i in self.VALID_INPUTS:
        continue
      break

    reply = self.query('/settings/per_page', data = {'per_page': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'per_page',
        'orig_fields':		{
          'per_page':		'%i' % i
        }
      },
      'error':			{
        'message':		'Value must be one of: 10; 20; 30; 40; 50; 60 (not %i)' % i,
        'params':		{
        }
      }
    })

  def test_malformed_string(self):
    reply = self.query('/settings/per_page', data = {'per_page': 'foobar'})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'per_page',
        'orig_fields':		{
          'per_page':		'foobar'
        }
      },
      'error':			{
        'message':		'Please enter an integer value',
        'params':		{
        }
      }
    })

  def test_random(self):
    i = self.get_rand_input()

    reply = self.query('/settings/per_page', data = {'per_page': i})
    cmp_json_dicts(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'per_page':		i
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })

class Sound(TestCase):
  def test_empty_submit(self):
    reply = self.query('/settings/sound')
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'sound',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_invalid_param(self):
    i = random.randint(-20, 20)

    reply = self.query('/settings/sound', data = {'__sound': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	None,
        'orig_fields':		{
          '__sound':		'%i' % i
        }
      },
      'error':			{
        'message':		'The input field \'__sound\' was not expected.',
        'params':		{
        }
      }
    })

  def test_empty_skin(self):
    reply = self.query('/settings/sound', data = {'sound': ''})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'sound',
        'orig_fields':		{
          'sound':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_malformed_int(self):
    i = random.randint(-20, -10)

    reply = self.query('/settings/sound', data = {'sound': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'sound',
        'orig_fields':		{
          'sound':		'%i' % i
        }
      },
      'error':			{
        'message':		'Value must be one of: 0; 1 (not %i)' % i,
        'params':		{
        }
      }
    })

  def test_random(self):
    i = random.randint(0, 1)

    reply = self.query('/settings/sound', data = {'sound': i})
    cmp_json_dicts(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'sound':		i
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })


class MyColor(TestCase):
  VALID_KINDS		= ['settlers']
  VALID_COLORS		= ['pink', 'purple', 'dark_green', 'black', 'brown', 'light_blue', 'orange', 'green', 'dark_blue', 'red']

  def get_rand_kind(self):
    return self.VALID_KINDS[0]

  def get_rand_color(self):
    i = random.randint(0, len(self.VALID_COLORS) - 1)
    return self.VALID_COLORS[i]

  def test_empty_submit(self):
    reply = self.query('/settings/color')
    cmp_json_dicts(reply, {
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

    reply = self.query('/settings/color', data = {'__kind': i})
    cmp_json_dicts(reply, {
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
    reply = self.query('/settings/color', data = {'kind': ''})
    cmp_json_dicts(reply, {
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
    reply = self.query('/settings/color', data = {'kind': '', 'color': ''})
    cmp_json_dicts(reply, {
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

    reply = self.query('/settings/color', data = {'kind': i, 'color': color})
    cmp_json_dicts(reply, {
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

    reply = self.query('/settings/color', data = {'kind': 'foobar', 'color': color})
    cmp_json_dicts(reply, {
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
    return

    kind = self.get_rand_kind()
    color = random.randint(-20, -10)

    reply = self.query('/settings/color', data = {'kind': kind, 'color': color})
    cmp_json_dicts(reply, {
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
    return

    kind = self.get_rand_kind()
    color = self.get_rand_color()

    reply = self.query('/settings/color', data = {'kind': kind, 'color': 'foobar'})
    cmp_json_dicts(reply, {
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

class Board(TestCase):
  def test_empty_submit(self):
    reply = self.query('/settings/board_skin')
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'skin',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_invalid_param(self):
    i = random.randint(-20, 20)

    reply = self.query('/settings/board_skin', data = {'__skin': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	None,
        'orig_fields':		{
          '__skin':		'%i' % i
        }
      },
      'error':			{
        'message':		'The input field \'__skin\' was not expected.',
        'params':		{
        }
      }
    })

  def test_empty_skin(self):
    reply = self.query('/settings/board_skin', data = {'skin': ''})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'skin',
        'orig_fields':		{
          'skin':		''
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_malformed_int(self):
    i = random.randint(-20, 20)

    reply = self.query('/settings/board_skin', data = {'skin': i})
    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'skin',
        'orig_fields':		{
          'skin':		'%i' % i
        }
      },
      'error':			{
        'message':		'Value must be one of: real; simple (not u\'%i\')' % i,
        'params':		{
        }
      }
    })

  def test_random(self):
    skins = ['simple', 'real']
    i = random.randint(0, 1)
    skin = skins[i]

    reply = self.query('/settings/board_skin', data = {'skin': skin})
    cmp_json_dicts(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'skin':		skin
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })

if __name__ == '__main__':
  unittest.main()
