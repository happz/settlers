window.settlers.templates.recent_events = {}
window.settlers.templates.recent_events.playables = '
  {{#playables}}
    <div id="{{eid}}" class="mediumListIconTextItem">
      <div class="icon-grid-view mediumListIconTextItem-Image" />
      <div class="mediumListIconTextItem-Detail">
        <h4 title="{{name}}">{{#is_game}}{{#_g}}Game{{/_g}}{{/is_game}}{{^is_game}}{{#_g}}Tournament{{/_g}}{{/is_game}}&nbsp;{{id}} - {{name}}</h4>
        <div class="btn-toolbar">
          <div class="btn-group">
            {{#is_present}}
              {{#is_invited}}
                <button class="btn" id="{{eid}}_join" title="{{#_g}}Join{{/_g}}" rel="tooltip" data-placement="top">
                  <i class="icon-checkmark"></i>
                </button>
              {{/is_invited}}
              {{^is_invited}}
                {{#is_game}}
                  <a class="btn" href="/game/?gid={{id}}#board" title="{{#_g}}Show board{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_board"><i class="icon-info-3"></i><span class="badge badge-important menu-alert"></span></a>
                  <a class="btn" href="/game/?gid={{id}}#history" title="{{#_g}}Show history{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_history"><i class="icon-clipboard-2"></i></a>
                  <a class="btn" href="/game/?gid={{id}}#chat" title="{{#_g}}Show chat{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_chat"><i class="icon-comments"></i><span class="badge badge-important menu-alert"></span></a>
                  {{#is_finished}}
                    <a class="btn" href="/game/?gid={{id}}#stats" title="{{#_g}}Show stats{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_stats"><i class="icon-bars"></i></a>
                  {{/is_finished}}
                {{/is_game}}
                {{^is_game}}
                  <a class="btn" href="/tournament/?tid={{id}}#board" title="{{#_g}}Show board{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_board"><i class="icon-info-3"></i><span class="badge badge-important menu-alert"></span></a>
                  <a class="btn" href="/tournament/?tid={{id}}#history" title="{{#_g}}Show history{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_history"><i class="icon-clipboard-2"></i></a>
                  <a class="btn" href="/tournament/?tid={{id}}#chat" title="{{#_g}}Show chat{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_chat"><i class="icon-comments"></i><span class="badge badge-important menu-alert"></span></a>
                  <a class="btn" href="/tournament/?tid={{id}}#rounds" title="{{#_g}}Show rounds{{/_g}}" rel="tooltip" data-placement="top"><i class="icon-clipboard-2"></i></a>
                  {{#is_finished}}
                    <a class="btn" href="/tournament/?tid={{id}}#stats" title="{{#_g}}Show stats{{/_g}}" rel="tooltip" data-placement="top" id="{{eid}}_stats"><i class="icon-bars"></i></a>
                  {{/is_finished}}
                {{/is_game}}
              {{/is_invited}}
            {{/is_present}}
            {{^is_present}}
              <a class="btn" href="#" id="{{eid}}_join" title="{{#_g}}Join{{/_g}}"><i class="icon-checkmark"></i></a>
            {{/is_present}}
          </div>
        </div>
      </div>
    </div>
  {{/playables}}
'

window.settlers.templates.recent_events.playable_preview = '
  <div class="bold">{{name}}</div>
  <div class="playable-players">{{{players_list}}}</div>
  {{#is_game}}
    <div class="playable-limit">{{limit}} {{#_g}}players{{/_g}}</div>
  {{/is_game}}
  {{#round}}
    <div class="playable-round">
      {{round}}. {{#_g}}round{{/_g}},
      {{#is_finished}}
        winner is {{forhont.name}}
      {{/is_finished}}
      {{^is_finished}}
        {{forhont.name}} {{#_g}}on turn{{/_g}}
      {{/is_finished}}
    </div>
  {{/round}}
  {{#is_invited}}
    <div style="font-weight: bold">{{#_g}}You are invited!{{/_g}}</div>
  {{/is_invited}}
  {{^is_game}}
    <div class="playable-limit">{{limit}} {{#_g}}players per game{{/_g}}</div>
    <div class="playable-limit">Tournament for {{num_players}} players</div>
  {{/is_game}}
'
window.settlers.templates.recent_events.password = '
  <input type="text" id="{{id}}_join_password" />
  <button class="btn" id="{{id}}_join" title="{{#_g}}Join{{/_g}}" rel="tooltip" data-placement="top">
    <i class="icon-checkmark"></i>
  </button>
'

window.settlers.setup_page = () ->
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

    p.players_list = () ->
      l = []

      __fmt_player = (player) ->
        s = player.user.name

        if player.user.is_online == true
          s = '<span class="user-online">' + s + '</span>'

        if player.is_confirmed != true
          s = '<span class="user-invited">' + s + '</span>'

        if player.is_on_turn == true
          s = '<span class="user-onturn">' + s + '</span>'

        return s

      l = (__fmt_player player for player in p.players)
      return l.join ', '

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
              window.hlib.INFO.show 'Joined'
              update_events()

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
      $('#' + p.eid + '_join').replaceWith(window.hlib.render window.settlers.templates.recent_events.password, p)

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

  refresh_list = (opts) ->
    $(opts.eid).html ''

    opts.playables.sort cmp_playables

    __per_playable = (p) ->
      p.eid = 'playable_' + (if p.is_game then 'game' else 'tournament') + '_' + p.id

    __per_playable p for p in opts.playables

    $(opts.eid).html window.hlib.render(window.settlers.templates.recent_events.playables, opts)

    decorate_playable p for p in opts.playables

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
