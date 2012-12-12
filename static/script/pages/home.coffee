window.settlers.templates.recent_events = {}
window.settlers.templates.recent_events.playable = doT.template '
  <div id="{{= it.eid}}" class="mediumListIconTextItem" data-placement="top" data-content="{{= it.limit}} {{= window.hlib._g("players")}}<br />{{= it.players_list}}" data-title="{{= it.name}}">
    <div class="icon-grid-view mediumListIconTextItem-Image" />
    <div class="mediumListIconTextItem-Detail">
      <h4 title="{{= it.name}}">
        {{? it.is_game}}
          {{= window.hlib._g("Game")}}
        {{?? it.is_game == false}}
          {{= window.hlib._g("Tournament")}}
        {{?}}
        &nbsp;{{= it.id}} - {{= it.name}}
      </h4>
      <div class="btn-toolbar">
        <div class="btn-group">
          {{? it.is_present}}
            {{? it.is_invited}}
              <button class="btn" id="{{= it.eid}}_join" title="{{= window.hlib._g("Join")}}" rel="tooltip" data-placement="top"><i class="icon-checkmark"></i></button>
            {{??}}
              {{? it.is_game}}
                <a class="btn" href="/game/?gid={{= it.id}}#board" title="{{= window.hlib._g("Show board")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_board"><i class="icon-info-3"></i><span class="badge badge-important menu-alert"></span></a>
                <a class="btn" href="/game/?gid={{= it.id}}#history" title="{{= window.hlib._g("Show history")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_history"><i class="icon-clipboard-2"></i></a>
                <a class="btn" href="/game/?gid={{= it.id}}#chat" title="{{= window.hlib._g("Show chat")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_chat"><i class="icon-comments"></i><span class="badge badge-important menu-alert"></span></a>
                {{? it.is_finished}}
                  <a class="btn" href="/game/?gid={{= it.id}}#stats" title="{{= window.hlib._g("Show stats")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_stats"><i class="icon-bars"></i></a>
                {{?}}
              {{??}}
                <a class="btn" href="/tournament/?tid={{= it.id}}#board" title="{{= window.hlib._g("Show board")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_board"><i class="icon-info-3"></i><span class="badge badge-important menu-alert"></span></a>
                <a class="btn" href="/tournament/?tid={{= it.id}}#history" title="{{= window.hlib._g("Show history")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_history"><i class="icon-clipboard-2"></i></a>
                <a class="btn" href="/tournament/?tid={{= it.id}}#chat" title="{{= window.hlib._g("Show chat")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_chat"><i class="icon-comments"></i><span class="badge badge-important menu-alert"></span></a>
                <a class="btn" href="/tournament/?tid={{= it.id}}#rounds" title="{{= window.hlib._g("Show rounds")}}" rel="tooltip" data-placement="top"><i class="icon-clipboard-2"></i></a>
                {{? it.is_finished}}
                  <a class="btn" href="/tournament/?tid={{= it.id}}#stats" title="{{= window.hlib._g("Show stats")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_stats"><i class="icon-bars"></i></a>
                {{?}}
              {{?}}
            {{?}}
          {{??}}
            <button class="btn" id="{{= it.eid}}_join" title="{{= window.hlib._g("Join")}}" rel="tooltip" data-placement="top"><i class="icon-checkmark"></i></button>
          {{?}}
        </div>
      </div>
    </div>
  </div>
'

window.settlers.templates.recent_events.password = doT.template '
  <input type="text" id="{{= it.id}}_join_password" />
  <button class="btn" id="{{= it.id}}_join" title="{{= window.hlib._g("Join")}}" rel="tooltip" data-placement="top">
    <i class="icon-checkmark"></i>
  </button>
'

$(window).bind 'page_startup', () ->
  cmp_playables = (x, y) ->
    if x.is_invited == true
      if y.is_invited == true
        return 0
      else
        return -1
    if y.is_invited == true
      return 1

    if x.is_on_turn == true
      if y.is_on_turn == true
        return 0
      else
        return -1
    if y.is_on_turn == true
      return 1

    if x.chat_posts and x.chat_posts > 0
      if y.chat_posts and y.chat_posts > 0
        return 0
      else
        return -1
    if y.chat_posts and y.chat_posts > 0
       return 1

    if x.is_present == true
      if y.is_present == true
        return 0
      else
        return -1
    if y.is_present == true
      return 1

    return 0

  decorate_playable = (p) ->
    peid = '#' + p.peid

    __generic_click = (button, postfix) ->
      eid = '#' + p.eid

      if button
        eid += '_' + button

      $(eid).click () ->
        if p.is_game
          url = '/game?gid'
        else
          url = '/tournament?tid'

        url += '=' + p.id

        if postfix
          url += '#' + postfix

        window.hlib.redirect url

        return false

    __join_click = (click_eid) ->
      $(click_eid).click () ->
        if p.is_game
          url = '/game/join?gid=' + p.id
        else
          url = '/tournament/join?tid=' + p.id

        if p.has_password
          data =
            password:		$('#' + p.eid + '_join_password').val()
        else
          data = null

        __get_field = (response) ->
          field = null

          if response.hasOwnProperty('form') and response.form.hasOwnProperty 'invalid_field'
            field = response.form.invalid_field
          else
            field = 'password'

          field = new window.hlib.FormField '#' + p.eid + '_join_' + field
          return field

        new window.hlib.Ajax
          url:			url
          data:			data
          handlers:
            h200:		(response, ajax) ->
              console.log 'joined, show info and update'
              window.hlib.INFO.show 'You have joined a game', ''

              __update = () ->
                window.hlib.MESSAGE.hide()
                update_events()
                window.settlers.PULL_NOTIFY.update()

              $('body').oneTime '5s', __update

            h400:		(response, ajax) ->
              field = __get_field response
              field.mark_error()

              window.hlib.error 'Bad request', response.error, () ->
                field.unmark_error()

            h401:		(response, ajax) ->
              field = __get_field response
              field.mark_error()

              window.hlib.error 'Unauthorized', response.error, () ->
                field.unmark_error()

        return false

    if p.has_password
      $('#' + p.eid + '_join').replaceWith(window.settlers.templates.recent_events.password p)

    if p.is_present
      __generic_click()

    else
      __join_click '#' + p.eid

    __generic_click 'board'
    __generic_click 'history', 'history'
    __generic_click 'chat', 'chat'
    __generic_click 'stats', 'stats'

    if p.is_on_turn
      window.settlers.show_menu_alert p.eid + ' #' + p.eid + '_board', '!'

    if p.chat_posts
      window.settlers.show_menu_alert p.eid + ' #' + p.eid + '_chat', p.chat_posts

    if p.archive_deadline
      d = new Date (p.archive_deadline * 1000)
      console.log d.strftime '%d/%m %H:%M'

    $('#' + p.eid).popover
      html:			true
      trigger:			'hover'

  render_playable = (eid, p) ->
    p.eid = 'playable_' + (if p.is_game then 'game' else 'tournament') + '_' + p.id

    __fmt_player = (player) ->
      s = player.user.name

      if player.user.is_online == true
        s = '<span class=\'user-online\'>' + s + '</span>'

      if player.is_confirmed != true
        s = '<span class=\'user-invited\'>' + s + '</span>'

      if player.is_on_turn == true
        s = '<span class=\'user-onturn\'>' + s + '</span>'

      return s

    p.players_list = (__fmt_player player for player in p.players).join ', '

    $(eid).append window.settlers.templates.recent_events.playable p
    decorate_playable p

  refresh_list = (opts) ->
    $(opts.eid).html ''

    opts.playables.sort cmp_playables

    render_playable opts.eid, p for p in opts.playables

  update_events = () ->
    new window.hlib.Ajax
      url:			'/home/recent_events'
      handlers:
        h200:			(response, ajax) ->
          # active
          refresh_list
            eid:		'#active'
            playables:		response.events.playable
            _g:			window.hlib._g

          # free
          refresh_list
            eid:		'#free'
            playables:		response.events.free
            _g:			window.hlib._g

          # finished
          refresh_list
            eid:		'#finished'
            playables:		response.events.finished
            _g:			window.hlib._g

          if response.events.finished_chat
            window.settlers.show_menu_alert 'finished_header', response.events.finished_chat

          window.hlib.MESSAGE.hide()

#  $(eid).everyTime '20s', update_events
  update_events()
