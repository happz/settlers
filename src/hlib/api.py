__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import hashlib
import json
import threading
import types
import UserDict

import hlib.error
import hlib.handlers
import hlib.http.session
import hlib.input
import hlib.locks
import hlib.log

# pylint: disable-msg=F0401
import hruntime # @UnresolvedImport

API_TOKEN_LENGTH = 32

PASSWORD_FIELD_FILTERS = [
  lambda s: s.startswith('password')
]

class APICookieStorage(UserDict.UserDict):
  def __init__(self):
    UserDict.UserDict.__init__(self)

    self._lock = hlib.locks.RLock(name = 'API cookie storage')

  def __getitem__(self, name):
    with self._lock:
      return UserDict.UserDict.__getitem__(self, name)

  def __setitem__(self, name, value):
    with self._lock:
      UserDict.UserDict.__setitem__(self, name, value)

  def __contains__(self, name):
    with self._lock:
      return UserDict.UserDict.__contains__(self, name)

_COOKIES = APICookieStorage()

class ApiIORegime(hlib.handlers.IORegime):
  @staticmethod
  def check_session():
    hlib.handlers.PageIORegime.check_session()

  @staticmethod
  def run_handler():
    res = hruntime.response

    res.headers['Content-Type'] = 'application/json'

    try:
      hlib.input.validate()

      res.api_response = hruntime.request.handler(**hruntime.request.params)

      if res.api_response == None:
        res.api_response = Reply(200)

      if hasattr(res.api_response, 'dump'):
        return res.api_response.dump()

      if type(res.api_response) == types.DictType:
        return Raw(res.api_response).dump()

      if type(res.api_response) in types.StringTypes:
        return res.api_response

      raise hlib.error.InvalidOutputError()

    except hlib.http.Redirect, e:
      raise e

    except Exception, e:
      hruntime.db.doom()

      e = hlib.error.error_from_exception(e)
      hlib.log.log_error(e)

      kwargs = e.args_for_reply()
      res.api_response = Reply(e.reply_status, error = Error(e), **kwargs)

      # pylint: disable-msg=W0142
      return res.api_response.dump()

  @staticmethod
  def redirect(url):
    res = hruntime.response

    reply = Reply(303, redirect = Redirect(url))

    res.status = 200
    res.output = reply.dump()

class ApiTokenIORegime(ApiIORegime):
  @staticmethod
  def check_session():
    hlib.input.validate(schema = api.ValidateAPIToken)

    token = hruntime.request.params['api_token']

    try:
      hruntime.user = hruntime.app.api_tokens[token]

      hruntime.request.api_token = token
      del hruntime.request.params['api_token']

    except KeyError:
      raise hlib.http.Prohibited()

api = lambda f: hlib.handlers.tag_fn(f, 'ioregime', ApiIORegime)
api_token = lambda f: hlib.handlers.tag_fn(f, 'ioregime', ApiTokenIORegime)

#
# Encoders
#
class JSONEncoder(json.JSONEncoder):
  """
  Custom JSON encoder, able to encode L{api.ApiJSON} objects.

  @see:				http://docs.python.org/library/json.html#encoders-and-decoders
  """

  # pylint: disable-msg=E0202
  def default(self, o):
    """
    Return dictionary of field values if C{o} is instance of L{ApiJSON} class.

    Only fields mentioned in o.API_FIELDS are exported.

    @param o:			object to convert
    @type o:			L{object}
    @return:			If C{o} is instance of L{ApiJSON}, C{dict} of C{field}={o.field} pairs
                                for C{field}s specified in C{o.API_FIELDS}. Return value of L{JSONEncoder.default}
                                otherwise.
    @rtype:			C{dict} or anything that L{JSONEncoder.default} returns
    """

    return dict([[f, getattr(o, f)] for f in o.API_FIELDS]) if isinstance(o, ApiJSON) else super(JSONEncoder, self).default(o)

class ApiJSON(object):
  def __init__(self, fields):
    super(ApiJSON, self).__init__()

    # pylint: disable-msg=C0103
    self.API_FIELDS = []

    self.update(fields)

  def __str__(self):
    return '\n'.join(['%s: %s' % (f, type(getattr(self, f))) for f in self.API_FIELDS])

  def update(self, fields):
    self.API_FIELDS += fields

    for f in fields:
      setattr(self, f, None)

  def dump(self, o = None, **kwargs):
    return json.dumps(o or self, cls = JSONEncoder, **kwargs)

class Error(ApiJSON):
  def __init__(self, e):
    super(Error, self).__init__(['message', 'params'])

    self.message			= e.msg
    self.params				= e.params

class Form(ApiJSON):
  def __init__(self, orig_fields = False, remove_password = True, remove_fields = None, invalid_field = None, updated_fields = None):
    super(Form, self).__init__(['orig_fields', 'invalid_field', 'updated_fields'])

    if orig_fields:
      fields = hruntime.request.params.copy()
      fields_to_remove = []

      if remove_password:
        def _check_password_filters(s):
          for f in PASSWORD_FIELD_FILTERS:
            if f(s):
              return True
          return False

        # pylint: disable-msg=W0141
        fields_to_remove = filter(_check_password_filters, fields.keys())

      if remove_fields:
        fields_to_remove += remove_fields

      _fields = {}

      for k, v in fields.iteritems():
        if k in fields_to_remove:
          continue

        _fields[k] = v

      if len(_fields) > 0:
        self.orig_fields = _fields

    if invalid_field:
      self.invalid_field = invalid_field

    if updated_fields:
      self.updated_fields = updated_fields

class User(ApiJSON):
  def __init__(self, user):
    super(User, self).__init__(['name', 'is_online'])

    self.name		= user.name
    self.is_online	= user.is_online

class Reply(ApiJSON):
  def __init__(self, status, message = None, **kwargs):
    super(Reply, self).__init__(['status'])

    self.status         = status

    if message:
      self.update(['message'])
      self.message = message

    self.update(kwargs.keys())
    for k, v in kwargs.iteritems():
      setattr(self, k, v)

class Raw(ApiJSON):
  def __init__(self, data):
    super(Raw, self).__init__([])

    self.data = data

  def dump(self):
    return super(Raw, self).dump(o = self.data)

class Redirect(ApiJSON):
  def __init__(self, url):
    super(Redirect, self).__init__(['url'])

    self.url = url

#
# API Tokens
#
class ValidateAPIToken(hlib.input.SchemaValidator):
  """
  API token validator

  API token must be
    - string (L{input.CommonString})
    - exactly 32 (length of MD5 username hash) + L{API_TOKEN_LENGTH} characters long (L{lib.input.MinLength}, L{input.MaxLength})
  """

  api_token = hlib.input.validator_factory(hlib.input.CommonString(), hlib.input.MinLength(32 + API_TOKEN_LENGTH), hlib.input.MaxLength(32 + API_TOKEN_LENGTH))

class ApiTokenCache(object):
  """
  Cache to store token => L{datalayer.User} bond at hand.

  There is no other way how to find to which user belongs supplied token
  than to walk through all users and look for token. Cache results.
  """

  def __init__(self, name, app):
    super(ApiTokenCache, self).__init__()

    self.name			= name
    self.app			= app

    self.lock = hlib.locks.Lock(name = 'API token cache')
    self.token_to_user = {}

  def __getitem__(self, key):
    with self.lock:
      if key in self.token_to_user:
        return self.token_to_user[key]

      for user in hruntime.dbroot.users.values():
        if key in user.api_tokens:
          self.token_to_user[key] = user
          return user

      raise KeyError(key)

  def __setitem__(self, key, value):
    raise AttributeError(key)

  def __delitem__(self, key):
    raise AttributeError(key)

  def __len__(self):
    with self.lock:
      return len(self.token_to_user)

  def __contains__(self, key):
    with self.lock:
      return key in self.token_to_user

def api_token_generate(user):
  return hashlib.md5(user.name.encode('ascii', 'replace')).hexdigest() + hlib.http.session.gen_rand_string(API_TOKEN_LENGTH)
