import tests.handlers

import random

from tests import query, check_json_reply

class settings_AfterPassTurn(tests.handlers.TestCase):
  def test_empty_submit(self):
    reply = query('/settings/after_pass_turn')

    check_json_reply(reply, {
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

    reply = query('/settings/after_pass_turn', data = {'__action': i})

    check_json_reply(reply, {
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
        'params':		{
        }
      }
    })

  def test_empty_action(self):
    reply = query('/settings/after_pass_turn', data = {'action': ''})

    check_json_reply(reply, {
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
    reply = query('/settings/after_pass_turn', data = {'action': 'foobar'})
    check_json_reply(reply, {
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
    reply = query('/settings/after_pass_turn', data = {'action': 3.14})
    check_json_reply(reply, {
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

    reply = query('/settings/after_pass_turn', data = {'action': i})
    check_json_reply(reply, {
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

    reply = query('/settings/after_pass_turn', data = {'action': i})
    check_json_reply(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'action':		i
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })
