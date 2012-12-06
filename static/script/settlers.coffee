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

#    $('#trumpet_board_dialog').modal
#      show:			false
#      backdrop:			'static'
#      keyboard:			false

    __call_update = () ->
      pull_notify.update()

    $('.win-commandlayout').everyTime '300s', __call_update

  update:		() ->
    new window.hlib.Ajax
      url:			'/pull_notify'
      keep_focus:		true
      handlers:
        h200:			(response, ajax) ->
          # Reset all widgets
          window.hlib.setTitle 'Osadnici'
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
window.settlers.render_board_piece = (attrs) ->
  return '<span ' + ((attr_name + '="' + attr_value + '"' for own attr_name, attr_value of attrs).join ' ') + '></span>'

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
          $('#chat_post_' + post.id + ' .chat-post-unread-badge').show()

      __mark_unread post for post in response.page.records

  pager.refresh()

  return pager

window.settlers.startup = () ->
  window.hlib.setup_common
    message_dialog:		'#message_dialog'

  window.settlers.PULL_NOTIFY = new window.settlers.PullNotify

  window.settlers.setup_settlers()
  window.settlers.setup_page()

  if window.settlers.user
    window.settlers.PULL_NOTIFY.update()

window.settlers.post_startup = () ->
  $('a[rel=tooltip]').tooltip()
  $('button[rel=tooltip]').tooltip()
  $('body').css 'margin-bottom', ($('footer').height() + 'px')

#
# Bind startup event
#
$(window).bind 'hlib_startup', window.settlers.startup
$(window).bind 'hlib_poststartup', window.settlers.post_startup
