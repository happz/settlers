import handlers

# Shortcuts
from handlers import page, require_login

class Handler(handlers.GenericHandler):
  #
  # Index
  #
  @require_login
  @page
  def index(self):
    return self.generate('new.mako')
