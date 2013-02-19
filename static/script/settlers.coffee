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
    @sound_notified = false

    _pn = @

    __call_update = () ->
      _pn.update()

    $('.win-commandlayout').everyTime '300s', __call_update

  update:		() ->
    _pn = @

    new window.hlib.Ajax
      url:			'/pull_notify'
      keep_focus:		true
      handlers:
        h200:			(response, ajax) ->
          # Reset all widgets
          window.hlib.setTitle window.settlers.title
          window.settlers.hide_menu_alert 'menu_chat'
          window.settlers.hide_menu_alert 'menu_home', 'badge-important'
          window.settlers.hide_menu_alert 'menu_home', 'badge-info'

          $('#trumpet_board').hide()
          $('body').css 'margin-top', '0'

          to_title = 0

          if response.events.chat != false
            to_title += response.events.chat
            window.settlers.show_menu_alert 'menu_chat', response.events.chat

          if response.events.on_turn != false
            to_title += response.events.on_turn
            window.settlers.show_menu_alert 'menu_home', response.events.on_turn, 'badge-important'

          if to_title > 0
            window.hlib.setTitle window.settlers.title + ' (' + to_title + ')'

            if window.settlers.user.sound and _pn.sound_notified != true
              $.fn.soundPlay
                url:		'/static/sound/cartoon008.wav'
                playerId:	'player1'
                command:	'play'

              _pn.sound_notified = true

          if response.events.trumpet != false
            $('#trumpet_board_dialog p').html response.events.trumpet
            $('#trumpet_board_dialog').show()

            $('body').css 'margin-top', ($('#trumpet_board_dialog').height() + 'px')

          if response.events.free_games != false
            $('#menu_home .menu-alert.badge-info').html response.events.free_games
            window.settlers.show_menu_alert 'menu_home', response.events.free_games, 'badge-info', (response.events.free_games + ' ' + (window.hlib._g 'free games'))

          window.hlib.MESSAGE.hide()

#
# Methods
#
window.settlers.show_menu_alert = (item, cnt, additional, tooltip) ->
  eid = '#' + item + ' span.menu-alert'

  if additional
    eid += '.' + additional

  if cnt
    $(eid).html cnt

  if tooltip
    $(eid).attr 'title', tooltip

  $(eid).show()

window.settlers.hide_menu_alert = (item, additional) ->
  eid = '#' + item + ' span.menu-alert'

  if additional
    eid += '.' + additional

  $(eid).hide()

window.settlers.autocomplete_options = () ->
  options =
    minLength:                  3
    source:                     (query, process) ->
      new window.hlib.Ajax
        url:                    '/users_by_name'
        show_spinner:           false
        data:
          term:                 query
        handlers:
          h200:                 (response, ajax) ->
            process response.users
          error:                (response, ajax) ->
            process []
      return null

  return options

window.settlers.setup_chat_form = (opts) ->
  new window.hlib.Form
    fid:			'chat_post'
    clear_fields:		['text']
    handlers:
      s200:   (response, form) ->
        form.info.success 'Posted'
        opts.handlers.h200()

window.settlers.setup_chat = (opts) ->
  pager = new window.hlib.Pager
    id_prefix:		opts.id_prefix
    url:		opts.url
    data:		opts.data
    template:		window.settlers.templates.chat_post
    eid:		opts.eid
    start:		0
    length:		20
    after_refresh:	(response, pager) ->
      __mark_unread = (post) ->
        if post.id > response.last_board
          $('#chat_post_' + post.id + ' .chat-post-unread').show()

      __mark_unread post for post in response.page.records

  pager.refresh()

  return pager

window.settlers.fmt_player = (player) ->
  s = player.user.name

  if player.user.is_online == true
    s = '<span class=\'user-online\'>' + s + '</span>'

  if player.is_confirmed != true
    s = '<span class=\'user-invited\'>' + s + '</span>'

  if player.is_on_turn == true
    s = '<span class=\'user-onturn\'>' + s + '</span>'

  return s

$(window).bind 'hlib_startup', () ->
  window.hlib.setup
    message_dialog:		'#message_dialog'
    i18n_table:			window.settlers.i18n_table
    visibility_check_eid:	'#visibility_check_mobile'

  window.settlers.PULL_NOTIFY = new window.settlers.PullNotify

  if window.settlers.user
    $('#menu_logout').click () ->
      new window.hlib.Ajax
        url:			'/logout/'
      return false

  else
    new window.hlib.Ajax
      url:			'/trumpet'
      keep_focus:		true
      handlers:
        h200:			(response, ajax) ->
          if response.trumpet != false
            $('#trumpet_board_dialog p').html response.trumpet
            $('#trumpet_board_dialog').show()
            $('body').css 'margin-top', ($('#trumpet_board_dialog').height() + 'px')

          window.hlib.MESSAGE.hide()

  # needed for iOS mobile devices (well, afaik...)
  adapt_to_orientation = () ->
    if window.orientation == 0 or window.orientation == 180
      content_width = 758
      screen_dimension = screen.width * 0.98

    else if window.orientation == 90 or window.orientation == -90
      content_width = 1024
      screen_dimension = screen.height

    viewport_scale = screen_dimension / content_width

    $('meta[name=viewport]').attr 'content', ('width=' + content_width + ', minimum-scale=' + viewport_scale + ', maximum-scale=' + viewport_scale)

  adapt_to_orientation()

  window.addEventListener 'resize', () ->
    $('body').css 'margin-top', ($('#trumpet_board_dialog').height() + 'px')

  window.addEventListener 'orientationchange', () ->
    adapt_to_orientation()

$(window).bind 'hlib_poststartup', () ->
  if window.hlib.mobile == false
    $('a[rel=tooltip]').tooltip()
    $('button[rel=tooltip]').tooltip()

  $('body').css 'margin-bottom', ($('footer').height() + 'px')

  if window.settlers.user
    window.settlers.PULL_NOTIFY.update()
