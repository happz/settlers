# pylint: disable-msg=W0401
from hlib.handlers import *

def survive_vacation(f):
  return tag_fn(f, 'survive_vacation', True)

from hlib.input import validate_by, validator_factory, SchemaValidator, Username, Password, FieldsMatch, Pipe, CommonString, NotEmpty, Int, OneOf, UnicodeString
