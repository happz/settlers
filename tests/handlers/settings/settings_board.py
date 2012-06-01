import tests.handlers

import random

from tests import query, check_json_reply

class settings_Board(tests.handlers.TestCase):
  def test_empty_submit(self):
    reply = query('/settings/board_skin')

    check_json_reply(reply, {
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

    reply = query('/settings/board_skin', data = {'__skin': i})

    check_json_reply(reply, {
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
    reply = query('/settings/board_skin', data = {'skin': ''})

    check_json_reply(reply, {
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

    reply = query('/settings/board_skin', data = {'skin': i})
    check_json_reply(reply, {
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

    reply = query('/settings/board_skin', data = {'skin': skin})
    check_json_reply(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'skin':		skin
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })
