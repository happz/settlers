window.settlers.templates.recent_events = {}
window.settlers.templates.recent_events.playable = doT.template '
  <tr id="{{= it.eid}}">
    <td>
      {{? it.is_game}}
        {{= window.hlib._g("Game")}}
      {{?? it.is_game == false}}
        {{= window.hlib._g("Tournament")}}
      {{?}}
      &nbsp;#{{= it.id}} - {{= it.name}}
    </td>
    <td>{{= it.limit}} {{= window.hlib._g("players")}}</td>
    <td>{{= it.players_list}}</td>
    <td>
      {{? it.is_finished}}
        {{= window.hlib._g(\'Winner is\')}} {{= window.settlers.fmt_player({user: it.forhont})}}
      {{?}}
    </td>
    <td>
      <div class="btn-toolbar">
        <div>
          {{? it.is_present}}
            {{? it.is_invited}}
              <a class="btn" href="#" id="{{= it.eid}}_join" title="{{= window.hlib._g("Join")}}" rel="tooltip" data-placement="top" style="position: relative"><span class="icon-checkmark"></span><span class="badge badge-important badge-join menu-alert"></span></a>
            {{??}}
              {{? it.is_game}}
                <a class="btn" href="/game/?gid={{= it.id}}#board" title="{{= window.hlib._g("Show board")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_board" style="position: relative"><span class="icon-info-7"></span><span class="badge badge-important menu-alert"></span></a>
                <a class="btn" href="/game/?gid={{= it.id}}#history" title="{{= window.hlib._g("Show history")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_history" style="position: relative"><span class="icon-clipboard"></span></a>
                <a class="btn" href="/game/?gid={{= it.id}}#chat" title="{{= window.hlib._g("Show chat")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_chat" style="position: relative"><span class="icon-comment-3"></i><span class="badge badge-important menu-alert"></span></a>
                {{? it.is_finished}}
                  <a class="btn" href="/game/?gid={{= it.id}}#stats" title="{{= window.hlib._g("Show stats")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_stats" style="position: relative"><span class="icon-bars-3"></span></a>
                {{?}}
              {{??}}
                <a class="btn" href="/tournament/?tid={{= it.id}}#players" title="{{= window.hlib._g("Show players")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_board" style="position: relative"><span class="icon-users"></span><span class="badge badge-important menu-alert"></span></a>
                <a class="btn" href="/tournament/?tid={{= it.id}}#history" title="{{= window.hlib._g("Show history")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_history" style="position: relative"><span class="icon-clipboard"></span></a>
                <a class="btn" href="/tournament/?tid={{= it.id}}#chat" title="{{= window.hlib._g("Show chat")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_chat" style="position: relative"><span class="icon-comment-3"></span><span class="badge badge-important menu-alert"></span></a>
                <a class="btn" href="/tournament/?tid={{= it.id}}#rounds" title="{{= window.hlib._g("Show rounds")}}" rel="tooltip" data-placement="top"><span class="icon-table-2" style="position: relative"></span></a>
                {{? it.is_finished}}
                  <a class="btn" href="/tournament/?tid={{= it.id}}#stats" title="{{= window.hlib._g("Show stats")}}" rel="tooltip" data-placement="top" id="{{= it.eid}}_stats" style="position: relative"><i class="icon-bars-3"></span></a>
                {{?}}
              {{?}}
            {{?}}
          {{??}}
            <button class="btn" id="{{= it.eid}}_join" title="{{= window.hlib._g("Join")}}" rel="tooltip" data-placement="top"><span class="icon-checkmark"></span></button>
          {{?}}
        </div>
      </div>
    </td>
  </tr>
'

window.settlers.templates.recent_events.password = doT.template '
  <div class="input-append">
    <input type="text" id="{{= it.id}}_join_password" />
    <button class="btn" id="{{= it.id}}_join" title="{{= window.hlib._g("Join")}}" rel="tooltip" data-placement="top">
      <i class="icon-checkmark"></i>
    </button>
  </div>
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

    if x.last_pass > y.last_pass
      return -1
    if x.last_pass < y.last_pass
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

            h402:		(response, ajax) ->
              window.hlib.error 'Error!', response.error

        return false

    if p.has_password
      $('#' + p.eid + '_join').replaceWith(window.settlers.templates.recent_events.password p)

    if p.is_invited
      window.settlers.show_menu_alert p.eid + ' #' + p.eid + '_join', '!', 'badge-join'
      __join_click '#' +  p.eid + '_join'
    else
      __join_click '#' + p.eid + '_join'

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

    $('#' + p.eid).popover
      html:			true
      trigger:			'hover'

  render_playable = (eid, p) ->
    p.eid = 'playable_' + (if p.is_game then 'game' else 'tournament') + '_' + p.id

    p.players_list = (window.settlers.fmt_player player for player in p.players).join ', '

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

          window.hlib.bind_tooltips()
          window.hlib.MESSAGE.hide()

#  $(eid).everyTime '20s', update_events
  update_events()
