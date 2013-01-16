import hlib.input
import hlib.issues

import handlers

from hlib.api import api
from hlib.input import validate_by, SchemaValidator

from handlers import page, require_login

import hruntime

class Handler(handlers.GenericHandler):
  @require_login
  @page
  def index(self):
    return self.generate('issues.mako')

  class ValidateCreate(SchemaValidator):
    title = hlib.input.CommonString()
    body = hlib.input.CommonString()

  @require_login
  @validate_by(schema = ValidateCreate)
  @api
  def create(self, title = None, body = None):
    body = (u'Reported by: %s\n\n' % hruntime.user.name) + body

    repo = hlib.issues.Repository(hruntime.app.config['issues']['token'], hruntime.app.config['issues']['repository'])
    repo.create_new_issue(title, body)
