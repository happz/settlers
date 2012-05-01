#
# Namespaces
#
window.settlers = window.settlers or {}
window.settlers.events = window.settlers.events or {}
window.settlers.templates = window.settlers.templates or {}

#
# Classes
#
class window.settlers.PullNotify
  constructor:	() ->
    pull_notify = @
    __call_update = () ->
      pull_notify.update()

    $('.menu-widget').everyTime '120s', __call_update

  update:		() ->
    $.ajax
      dataType:	'json'
      type:		'POST'
      url:		'/pull_notify'
      success:	(data) ->
        window.settlers.hide_menu_alert 'menu_chat'
        window.settlers.hide_menu_alert 'menu_home'

        if data.status != 200
          return

        if data.events.chat != false
          $('#menu_chat .menu-alert').html data.events.chat
          window.settlers.show_menu_alert 'menu_chat'

        if data.events.on_turn != false
          $('#menu_home .menu-alert').html data.events.on_turn
          window.settlers.show_menu_alert 'menu_home'

#
# Events
#
window.settlers.events['game.GameCreated']		= (e) ->
  window.hlib._g 'Game has been created'

window.settlers.events['game.GameFinished']		= (e) ->
  window.hlib._g 'Game has been finished'

window.settlers.events['game.GameCanceled']		= (e) ->
  if e.reason == 1
    return window.hlib._g 'Game has been canceled due to massive timeouts'

  if e.reason == 2
    return (window.hlib._g 'Game has been canceled due to missing player {0}').format e.user.name

  if e.reason == 3
    return window.hlib._g 'Game has been canceled due to lack of interest'

  return ''

window.settlers.events['game.GameStarted']		= (e) ->
  return window.hlib._g 'Game has started'

window.settlers.events['game.PlayerJoined']		= (e) ->
  return (window.hlib._g 'Player {0} joined game').format e.user.name

window.settlers.events['game.ChatPost']			= (e) ->
  return (window.hlib._g 'Player {0} post new message on chat').format e.user.name

window.settlers.events['game.PlayerMissed']		= (e) ->
  return (window.hlib._g 'Player {0} missed his turn').format e.user.name

window.settlers.events['game.Pass']			= (e) ->
  return (window.hlib._g 'Player {0} passed turn, next player is {1}').format e.prev.name, e.next.name

window.settlers.events['game.PlayerInvited']		= (e) ->
  return (window.hlib._g 'Player {0} has been invited to game').format e.user.name

window.settlers.events['game.CardUsed']			= (e) ->
  return (window.hlib._g 'Player {0} used card {1} from round {2}').format e.user.name, card = _(games.settlers.Card.map_card2str[e.card.type].capitalize()), e.round

window.settlers.events['game.CardBought']		= (e) ->
  return ''

#
# Methods
#
window.settlers.show_menu_alert = (item) ->
  eid = '#' + item + ' .menu-alert'

  $(eid).show()

window.settlers.hide_menu_alert = (item) ->
  eid = '#' + item + ' .menu-alert'

  $(eid).hide()

window.settlers.setup_chat_form = (opts) ->
  new window.hlib.Form
    fid:              'chat_post'
    handlers:
      s200:   (response, form) ->
        form.info.success 'Posted'
        opts.handlers.h200()

window.settlers.setup_chat = (opts) ->
  pager = new window.hlib.Pager
    url:		opts.url
    data:		opts.data
    template:		window.settlers.templates.chat_post
    eid:		opts.eid
    start:		0
    length:		20

  pager.refresh()

  return pager

window.settlers.startup = () ->
  window.hlib.setup_common
    info_dialog:
      eid:                    '.info-dialog'

  window.settlers.PULL_NOTIFY = new window.settlers.PullNotify

  window.settlers.setup_settlers()
  window.settlers.setup_page()

#
# Bind startup event
#
$(window).bind 'hlib_startup', window.settlers.startup
