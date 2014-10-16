from tests.online import TestCase
from tests import cmp_json_dicts

class login(TestCase):
  def test_empty_submit(self):
    reply = self.query('/login/login')

    cmp_json_dicts(reply, {
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
    reply = self.query('/login/login', data = {'username': self.config.get('online', 'username')})

    cmp_json_dicts(reply, {
      'status':			400,
      'form':			{
        'updated_fields':	None,
        'invalid_field':	'password',
        'orig_fields':		{
          'username':		self.config.get('online', 'username')
        }
      },
      'error':			{
        'message':		'Please enter a value',
        'params':		{}
      }
    })

  def test_empty_username(self):
    reply = self.query('/login/login', data = {'password': self.config.get('online', 'password')})

    cmp_json_dicts(reply, {
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
    reply = self.query('/login/login', data = {'username': 'foobar', 'password': 'foobar'})

    cmp_json_dicts(reply, {
      'status':			401,
      'error':			{
        'message':		'Invalid username or password',
        'params':		{}
      }
    })

  def test_wrong_password(self):
    reply = self.query('/login/login', data = {'username': self.config.get('online', 'username'), 'password': 'foobar'})

    cmp_json_dicts(reply, {
      'status':			401,
      'error':			{
        'message':		'Invalid username or password',
        'params':		{}
      }
    })

  def test_correct(self):
    reply = self.query('/login/login', data = {'username': self.config.get('online', 'username'), 'password': self.config.get('online', 'password')})

    cmp_json_dicts(reply, {
      'status':			303,
      'redirect':		{
        'url':			self.config.get('online', 'root_url') + '/home/'
      }
    })

if __name__ == '__main__':
  unittest.main()
