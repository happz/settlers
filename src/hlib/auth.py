__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import hlib.events
import hlib.http.session

# pylint: disable-msg=F0401
import hruntime # @UnresolvedImport

def refresh_session():
  """
  When called, sets some default values based on session - current user and his
  preferred language.
  """

  hruntime.response.headers['Cache-Control'] = 'must-revalidate, no-cache, no-store'

  hruntime.user = hruntime.dbroot.users[hruntime.session.name]
  hruntime.i18n = hruntime.dbroot.localization.languages['cz']

def start_session(user = None, tainted = False):
  """
  Start new session.

  @type user:			L{datalayer.User}
  @param user:			If set, save its id and name into session.
  @type tainted:		C{bool}
  @param tainted:		If not C{False}, L{datalayer.User} is expected
                                and its id is saved to session.
  """

  if not hruntime.session or not hruntime.session.authenticated or hruntime.session.name != user.name:
    hruntime.session = hlib.http.session.Session.create()

  hruntime.session.refresh_sid()

  hruntime.session.authenticated = True
  hruntime.session.name = user.name

  if tainted:
    # pylint: disable-msg=E1101,E1103
    hruntime.session.tainted = tainted.name

  elif hasattr(hruntime.session, 'tainted'):
    hruntime.session.tainted = False

  hruntime.app.sessions.invalidate_onlines()

  refresh_session()

def check_session(redirect_to_login = True):
  """
  Check if current session contains authenticated user record - if not, redirect request to
  login page.

  @raise http.Redirect:	Raised when there is no session started, redirect user to login page.
  """

  if not hruntime.request.is_authenticated:
    hruntime.app.sessions.invalidate_onlines()

    if redirect_to_login == True:
      raise hlib.http.Redirect('/login/')

    return

  refresh_session()

def logout(trigger_event = True):
  """
  Mark session as not authenticated and redirect to login page.
  """

  if trigger_event == True:
    hlib.events.trigger('system.UserLoggedOut', hruntime.dbroot.server, user = hruntime.user)

  hruntime.session.destroy()
  hruntime.session = None

  hruntime.app.sessions.invalidate_onlines()

  raise hlib.http.Redirect('/login/')
