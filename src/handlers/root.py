import re

import games
import handlers
import handlers.admin
import handlers.home
import handlers.chat
import handlers.game
import handlers.login
import handlers.maint
import handlers.new
import handlers.profile
import handlers.registration
import handlers.settings
import handlers.stats
import handlers.tour
import handlers.vacation
import lib.trumpet

import hlib
import hlib.auth
import hlib.error
import hlib.http
import hlib.stats
import lib.chat

import hlib.handlers.root

# Handlers
from hlib.api import api, ApiJSON, ApiReply
from handlers import page, require_login, survive_vacation, require_write

# Validators
from hlib.input import validate_by, SchemaValidator, Username

# pylint: disable-msg=F0401
import hruntime

class PullNotify(ApiJSON):
  def __init__(self):
    super(PullNotify, self).__init__(['chat', 'on_turn', 'trumpet'])

    self.chat           = False
    self.on_turn	= False
    self.trumpet	= False

class Handler(hlib.handlers.root.Handler):
  admin		= handlers.admin.Handler()
  home		= handlers.home.Handler()
  new		= handlers.new.Handler()

  login        = handlers.login.LoginHandler()
  loginas      = handlers.login.LoginAsHandler()
  settings     = handlers.settings.Handler()
  chat         = handlers.chat.ChatHandler(lib.chat.ChatPagerGlobal())
  registration = handlers.registration.Handler()
  stats        = handlers.stats.StatsHandler()
  vacation     = handlers.vacation.VacationHandler()
  maint        = handlers.maint.MaintHandler()
  game         = handlers.game.Handler()
  tournament   = handlers.tour.Handler()

  monitor	= hlib.stats.Handler('monitor.mako')

  @page
  def index(self):
    hlib.auth.check_session()

    raise hlib.http.Redirect('/home/')

  @survive_vacation
  @require_login
  @api
  def logout(self):
    # pylint: disable-msg=R0201
    hlib.auth.logout()

  @validate_by(schema = handlers.admin.ValidateLangSchema)
  @page
  def i18n(self, lang = None):
    hruntime.response.headers['Content-Type'] = 'text/javascript'
    return hruntime.cache.test_and_set(lib.datalayer.DummyUser('__system__'), 'i18n', self.generate, 'i18n.mako', params = {'lang': hruntime.dbroot.localization.languages[lang]})

  class ValidateUsersByName(SchemaValidator):
    term = Username()

  @require_login
  @validate_by(schema = ValidateUsersByName)
  @api
  def users_by_name(self, term = None):
    r = re.compile('.*?' + term + '.*?', re.I)
    return {'users': [u.name for u in hruntime.dbroot.users.itervalues() if r.search(u.name) != None and u != hruntime.user]}

  @api
  def trumpet(self):
    return {'message': lib.trumpet.Board.text}

  @require_login
  @api
  def pull_notify(self):
    r = PullNotify()

    txt = lib.trumpet.Board().text
    if len(txt) > 0:
      r.trumpet = txt

    # Do I have unread posts on global chat?
    cnt = lib.chat.ChatPagerGlobal().unread
    if cnt > 0:
      r.chat = cnt

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

    if cnt > 0:
      r.on_turn = cnt

    return ApiReply(200, events = r)
