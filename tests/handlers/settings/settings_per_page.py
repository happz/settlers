import tests.handlers

import random
import sys

from tests import query, check_json_reply

class settings_PerTablePage(tests.handlers.TestCase):
  VALID_INPUTS		= range(10, 61, 10)

  def get_rand_input(self):
    i = random.randint(0, len(self.VALID_INPUTS) - 1)
    return self.VALID_INPUTS[i]

  def test_empty_submit(self):
    reply = query('/settings/per_page')

    check_json_reply(reply, {
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

    reply = query('/settings/per_page', data = {'__per_page': i})

    check_json_reply(reply, {
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
    reply = query('/settings/per_page', data = {'per_page': ''})

    check_json_reply(reply, {
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

    reply = query('/settings/per_page', data = {'per_page': i})

    check_json_reply(reply, {
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
    reply = query('/settings/per_page', data = {'per_page': 'foobar'})

    check_json_reply(reply, {
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

    reply = query('/settings/per_page', data = {'per_page': i})

    check_json_reply(reply, {
      'status':			200,
      'form':			{
        'updated_fields':	{
          'per_page':		i
        },
        'invalid_field':	None,
        'orig_fields':		None
      }
    })
