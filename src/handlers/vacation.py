import handlers

# Shortcuts
from handlers import page, require_login, require_write, survive_vacation
from hlib.api import api

# pylint: disable-msg=F0401
import hruntime

class VacationHandler(handlers.GenericHandler):
  @survive_vacation
  @require_write
  @require_login
  @api
  def kill(self):
    hruntime.user.vacation_kill()

  @survive_vacation
  @require_login
  @page
  def index(self):
    return self.generate('vacation.mako')
