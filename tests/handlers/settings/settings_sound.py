import tests.handlers

import random

from tests import query, check_json_reply

class settings_Sound(tests.handlers.TestCase):
  def test_empty_submit(self):
    reply = query('/settings/sound')

    check_json_reply(reply, {
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

    reply = query('/settings/sound', data = {'__sound': i})

    check_json_reply(reply, {
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
    reply = query('/settings/sound', data = {'sound': ''})

    check_json_reply(reply, {
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

    reply = query('/settings/sound', data = {'sound': i})
    check_json_reply(reply, {
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

    reply = query('/settings/sound', data = {'sound': i})
    check_json_reply(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'sound':		i
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })
