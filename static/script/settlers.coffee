#
# Namespaces
#
window.settlers = window.settlers or {}
window.settlers.events = window.settlers.events or {}
window.settlers.templates = window.settlers.templates or {}

#
# Classes
#
class window.settlers.Trumpet
  constructor:                  () ->
    _trumpet = @

    @eid = '#trumpet_board_dialog'

    $(@eid + ' .modal-footer a').click () ->
      new window.hlib.Ajax
        url:                    '/confirm_trumpet'
        handlers:
          h200:                 (response, ajax) ->
            _trumpet.hide()
            window.hlib.MESSAGE.hide()

  update_offset:                () ->
    if $(@eid).css('display') == 'block'
      $('body').css 'margin-top', ($(@eid).height() + 'px')
    else
      $('body').css 'margin-top', '0px'

  hide:                         () ->
    $(@eid).hide()
    @update_offset()

  show:                         (message) ->
    $(@eid + ' p').html message
    $(@eid).show()
    @update_offset()

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

          window.settlers.TRUMPET.hide()

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
            window.settlers.TRUMPET.show response.events.trumpet

          if response.events.free_games != false
            $('#menu_home .menu-alert.badge-info').html response.events.free_games
            window.settlers.show_menu_alert 'menu_home', response.events.free_games, 'badge-info', (response.events.free_games + ' ' + (window.hlib._g 'free games'))

          window.hlib.MESSAGE.hide()

class window.settlers.Preview
  constructor: (preview_space_eid, source_eid, control_eid) ->
    __preview =
      nop: () ->
        return

      render: () ->
        if marked
          marked.setOptions()
          preview_text = marked($(source_eid).val())
        else
          preview_text = $(source_eid).val()
        $(preview_space_eid).html preview_text

      update: () ->
        __preview.render()

      show: (e) ->
        __preview.render()
        $(preview_space_eid).show()
        $(control_eid).click __preview.hide

      hide: (e) ->
        $(preview_space_eid).hide()
        $(control_eid).click __preview.show

    @preview = __preview

    $(control_eid).click __preview.show
    $(source_eid).keyup __preview.update

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
      h200:   (response, form) ->
        form.info.success 'Posted'
        opts.handlers.h200()

  return new window.settlers.Preview '#chat_post_form #preview', '#chat_post_form #chat_post_text', '#chat_post_form .btn-preview'

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
      N = String.fromCharCode 10
      raw_message_tmpl = doT.template "> **{{= it.user.name}} - {{= it.time }}**{{= String.fromCharCode(10)}}>{{= String.fromCharCode(10)}}{{= it.prefixed_message}}"

      window.settlers.chat_posts = {}

      __process_post = (post) ->
        window.settlers.chat_posts[post.id] = post

        $('a[data-chat-post]').click (e) ->
          e.preventDefault()

          _post = window.settlers.chat_posts[$(e.currentTarget).attr 'data-chat-post']

          # split and prefix lines
          lines = _post.raw_message.split '\n'
          _post.prefixed_message = []
          _post.prefixed_message.push ('> ' + line.trim()) for line in lines
          _post.prefixed_message = _post.prefixed_message.join N

          s = raw_message_tmpl _post
          $(opts.editor_eid).val s
          opts.preview.preview.render()

        if post.id > response.last_board
          $('#chat_post_' + post.id + ' .chat-post-unread').show()

      __process_post post for post in response.page.records

      window.hlib.bind_tooltips()

  pager.refresh()

  return pager

window.settlers.fmt_player = (player) ->
  classes = []

  if player.user.is_online == true
    classes.push 'user-online'

  if player.hasOwnProperty('is_confirmed') and player.is_confirmed != true
    classes.push 'user-invited'

  if player.hasOwnProperty('is_on_turn') and player.is_on_turn == true
    classes.push 'user-onturn'

  classes.push 'user-name'

  return '<a href="/profile/?username=' + player.user.name + '"><span class="' + classes.join(' ') + '">' + player.user.name + '</span></a>'

$(window).bind 'hlib_startup', () ->
  window.hlib.setup
    message_dialog:		'#message_dialog'
    i18n_table:			window.settlers.i18n_table
    visibility_check_eid:	'#visibility_check_mobile'

  window.settlers.PULL_NOTIFY = new window.settlers.PullNotify
  window.settlers.TRUMPET = new window.settlers.Trumpet

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
            window.settlers.TRUMPET.show response.trumpet
          else
            window.settlers.TRUMPET.hide()

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

  $(window).on 'resize', () ->
    window.settlers.TRUMPET.update_offset()

  $(window).on 'orientationchange', () ->
    adapt_to_orientation()

$(window).bind 'hlib_poststartup', () ->
  if window.hlib.mobile == false
    window.hlib.bind_tooltips()

  $('body').css 'margin-bottom', ($('footer').height() + 'px')

  if window.settlers.user
    window.settlers.PULL_NOTIFY.update()
