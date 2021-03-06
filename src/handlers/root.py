import re
import urllib

import games
import tournaments
import handlers.admin
import handlers.archive
import handlers.home
import handlers.chat
import handlers.game
import handlers.issues
import handlers.login
import handlers.maint
import handlers.maintenance
import handlers.monitor
import handlers.new
import handlers.profile
import handlers.registration
import handlers.settings
import handlers.stats
import handlers.tournament
import handlers.vacation
import lib.trumpet

import hlib.api
import hlib.auth
import hlib.error
import hlib.format
import hlib.handlers.root
import hlib.http
import hlib.log

import lib.chat

# Shortcuts
from hlib.api import api, api_token
from handlers import page, require_login, survive_vacation, require_write
from hlib.input import validate_by

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

class PullNotify(hlib.api.ApiJSON):
  def __init__(self):
    super(PullNotify, self).__init__(['chat', 'on_turn', 'trumpet', 'free_games'])

    self.chat           = False
    self.on_turn	= False
    self.trumpet	= False
    self.free_games	= False

class Handler(hlib.handlers.root.Handler):
  admin		= handlers.admin.Handler()
  archive     = handlers.archive.Handler()
  home		= handlers.home.Handler()
  issues	= handlers.issues.Handler()
  maintenance	= handlers.maintenance.Handler()
  new		= handlers.new.Handler()
  profile = handlers.profile.Handler()

  login        = handlers.login.LoginHandler()
  loginas      = handlers.login.LoginAsHandler()
  settings     = handlers.settings.Handler()
  chat         = handlers.chat.Handler(lib.chat.ChatPagerGlobal())
  registration = handlers.registration.Handler()
  stats        = handlers.stats.StatsHandler()
  vacation     = handlers.vacation.VacationHandler()
  maint        = handlers.maint.Handler()
  game         = handlers.game.Handler()
  tournament   = handlers.tournament.Handler()

  monitor	= handlers.monitor.Handler()

  @page
  def index(self):
    hlib.auth.check_session()

    raise hlib.http.Redirect('/home/')

  @page
  @require_login
  def about(self):
    return self.generate('about.mako')

  @survive_vacation
  @require_login
  @api
  def logout(self):
    # pylint: disable-msg=R0201
    hlib.auth.logout()

  @api
  def submit_error(self, error_msg = None, **kwargs):
    return

    if error_msg:
      if error_msg == 'Unknown token' and 'token' in kwargs:
        hruntime.i18n.coverage.miss(kwargs['token'])
        return

    kwargs['error_msg'] = error_msg
    data = {}
    for k, v in kwargs.items():
      k = urllib.unquote(k).encode('ascii', 'replace').replace('%5B', '[').replace('%5D', ']')
      v = urllib.unquote(v).encode('ascii', 'xmlcharrefreplace')
      data[k] = v

    e = hlib.error.ClientSideError(msg = data['error_msg'], params = data)
    hlib.log.log_error(e)

  @validate_by(schema = handlers.admin.ValidateLangSchema)
  @page
  def i18n(self, lang = None):
    hruntime.response.headers['Content-Type'] = 'text/javascript'
    return self.generate('i18n.mako', params = {'lang': hruntime.dbroot.localization.languages[lang]})

  class ValidateUsersByName(hlib.input.SchemaValidator):
    term = hlib.input.Username()

  @require_login
  @validate_by(schema = ValidateUsersByName)
  @api
  def users_by_name(self, term = None):
    r = re.compile('.*?' + term + '.*?', re.I)
    return hlib.api.Reply(200, users = [u.name for u in hruntime.dbroot.users.values() if r.search(u.name) != None and u != hruntime.user])

  @api
  def trumpet(self):
    txt = lib.trumpet.Board().text
    if len(txt) <= 0:
      txt = False
    else:
      txt = hlib.format.tagize(txt)

    return hlib.api.Reply(200, trumpet = txt)

  @require_login
  @require_write
  @api
  def confirm_trumpet(self):
    hruntime.user.seen_board = True

  def prepare_notify_events(self, no_trumpet = False):
    pn = PullNotify()

    if not no_trumpet and hruntime.user.seen_board != True:
      txt = lib.trumpet.Board().text
      if len(txt) > 0:
        pn.trumpet = hlib.format.tagize(txt)

    # Do I have unread posts on global chat?
    cnt = lib.chat.ChatPagerGlobal().unread
    if cnt > 0:
      pn.chat = cnt

    # Are there any free games?
    cnt  = sum([1 for g in games.f_active(hruntime.user) if g.is_free and not g.is_personal_free(hruntime.user)])
    cnt += sum([1 for t in tournaments.f_active(hruntime.user) if t.is_active and not t.has_player(hruntime.user)])
    if cnt > 0:
      pn.free_games = cnt

    # Am I on turn in any game?
    cnt = 0
    for k in games.GAME_KINDS:
      cnt += len(games.game_module(k, submodule = 'handler').GameOnTurnChecker.check())

    for g in games.f_active(hruntime.user):
      if g.has_player(hruntime.user):
        # Am I invited to this game?
        if not g.has_confirmed_player(hruntime.user):
          cnt += 1
          continue

        # Do I have undread posts?
        if g.my_player.chat.unread > 0:
          cnt += 1
          continue

    # Do I have unread posts in inactive games?
    cnt += sum([1 for g in games.f_inactive(hruntime.user) if g.my_player.chat.unread > 0])

    # Do I have unread posts in tournaments' chat?
    cnt += sum([1 for t in tournaments.f_active(hruntime.user) if t.has_player(hruntime.user) and t.my_player.chat.unread > 0])

    # Do I have unread posts in inactive tournaments?
    cnt += sum([1 for t in tournaments.f_inactive(hruntime.user) if t.my_player.chat.unread > 0])

    if cnt > 0:
      pn.on_turn = cnt

    return pn

  @require_login
  @api
  def pull_notify(self):
    return hlib.api.Reply(200, events = self.prepare_notify_events())

  @require_login
  @api_token
  def pull_notify_at(self):
    return hlib.api.Reply(200, events = self.prepare_notify_events(no_trumpet = True))
