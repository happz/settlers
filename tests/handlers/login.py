import tests.handlers
import sys

from tests import query, check_json_reply

class login(tests.handlers.TestCase):
  def test_empty_submit(self):
    reply = query('/login/login')

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'username',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_empty_password(self):
    reply = query('/login/login', data = {'username': tests.USERNAME})

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'password',
        'orig_fields':		{
          'username':		tests.USERNAME
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_empty_username(self):
    reply = query('/login/login', data = {'password': tests.PASSWORD})

    check_json_reply(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'username',
        'orig_fields':		None
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_wrong_username(self):
    reply = query('/login/login', data = {'username': 'foobar', 'password': 'foobar'})

    check_json_reply(reply, {
      'status':			401,
      'error':			{
        'message':		'Invalid username or password',
        'params':		{}
      }
    })

  def test_wrong_password(self):
    reply = query('/login/login', data = {'username': tests.USERNAME, 'password': 'foobar'})

    check_json_reply(reply, {
      'status':			401,
      'error':			{
        'message':		'Invalid username or password',
        'params':		{}
      }
    })

  def test_correct(self):
    reply = query('/login/login', data = {'username': tests.USERNAME, 'password': tests.PASSWORD})
    check_json_reply(reply, {
      'status':			303,
      'redirect':		{
        'url':			'http://osadnici-test.happz.cz/home/'
      }
    })

if __name__ == '__main__':
  unittest.main()


"""
        Q(label + 'correct', url = URL, data = {'username': 'happz', 'password': 'heslo'}, check = {"status": 200, "message": None, 'form_info': None})
        """
