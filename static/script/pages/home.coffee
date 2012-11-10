window.settlers.templates.recent_events = {}
window.settlers.templates.recent_events.playables = '
  <li class="header">{{#_g}}Playable{{/_g}}</li>
  {{#playable}}
    <li id="playable_{{#is_game}}game{{/is_game}}{{^is_game}}tournament{{/is_game}}_{{id}}" class="info info-with-menu info-with-border">
      {{#is_game}}
        <span class="playable-name">{{name}}</span>
      {{/is_game}}
      {{^is_game}}
        <span class="playable-name">Turnaj {{name}}</span>
      {{/is_game}}
      <span class="playable-menu right">
        {{#is_present}}
          {{#is_invited}}
            <span id="playable_join_{{id}}" class="icon icon-medium icon-playable-join" title="{{#_g}}Join{{/_g}}"></span>
          {{/is_invited}}
          {{^is_invited}}
            {{#is_on_turn}}
              <a href="/game/?gid={{id}}#board" title="{{#_g}}On turn!{{/_g}}"><span class="icon icon-medium icon-game-on-turn"></span></a>
            {{/is_on_turn}}
            {{#is_game}}
              <a href="/game/?gid={{id}}#board" title="{{#_g}}Show board{{/_g}}"><span class="icon icon-medium icon-game-board"></span></a>
              <a href="/game/?gid={{id}}#history" title="{{#_g}}Show history{{/_g}}"><span class="icon icon-medium icon-playable-history"></span></a>
              <a href="/game/?gid={{id}}#chat" title="{{#_g}}Show chat{{/_g}}">
            {{/is_game}}
            {{^is_game}}
              <a href="/tournament/?tid={{id}}#history" title="{{#_g}}Show history{{/_g}}"><span class="icon icon-medium icon-playable-history"></span></a>
              <a href="/tournament/?tid={{id}}#chat" title="{{#_g}}Show chat{{/_g}}">
            {{/is_game}}
              <span class="icon icon-medium icon-playable-chat">
                {{#chat_posts}}
                  <span class="menu-alert">{{chat_posts}}</span>
                {{/chat_posts}}
              </span>
            </a>
          {{/is_invited}}
        {{/is_present}}
        {{^is_present}}
          <span id="playable_join_{{id}}" class="icon icon-medium icon-playable-join" title="{{#_g}}Join{{/_g}"></span>
        {{/is_present}}
      </span>
    </li>
  {{/playable}}

  <li id="free_header" class="header">
    {{#_g}}Free{{/_g}} ({{free.length}})
    <span class="right icon icon-small icon-roll-open"></span>
  </li>
  <section class="hide">
  {{#free}}
    <li id="playable_{{#is_game}}game{{/is_game}}{{^is_game}}tournament{{/is_game}}_{{id}}" class="info info-with-menu info-with-border">
      {{#is_game}}
        <span class="playable-name">{{name}}</span>
      {{/is_game}}
      {{^is_game}}
        <span class="playable-name">Turnaj {{name}}</span>
      {{/is_game}}
      <span class="playable-menu right">
        <span id="playable_join_{{id}}" title="{{#_g}}Join{{/_g}}" class="icon icon-medium icon-playable-join"></span>
      </span>
    </li>
  {{/free}}
  </section>

  <li id="finished_header" class="header relative">
    {{#_g}}Finished{{/_g}} ({{finished.length}})
    <span class="right icon icon-small icon-roll-open">
      <span class="menu-alert"></span>
    </span>
  </li>
  <section class="hide">
  {{#finished}}
    <li id="playable_{{#is_game}}game{{/is_game}}{{^is_game}}tournament{{/is_game}}_{{id}}" class="info info-with-menu info-with-border">
      <span class="playable-name">{{name}}</span>
      <span class="playable-menu right">
        {{#is_game}}
          <a href="/game/?gid={{id}}#board" title="{{#_g}}Show board{{/_g}}"><span class="icon icon-medium icon-game-board"></span></a>
          <a href="/game/?gid={{id}}#history" title="{{#_g}}Show history{{/_g}}"><span class="icon icon-medium icon-playable-history"></span></a>
          <a href="/game/?gid={{id}}#chat" title="{{#_g}}Show chat{{/_g}}">
        {{/is_game}}
        {{^is_game}}
          <a href="/tournament/?tid={{id}}#history" title="{{#_g}}Show history{{/_g}}"><span class="icon icon-medium icon-playable-history"></span></a>
          <a href="/tournament/?tid={{id}}#chat" title="{{#_g}}Show chat{{/_g}}">
        {{/is_game}}
          <span class="icon icon-medium icon-playable-chat">
            {{#chat_posts}}
              <span class="menu-alert">{{chat_posts}}</span>
            {{/chat_posts}}
          </span>
        </a>
      </span>
    </li>
  {{/finished}}
  </section>
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
  <input type="text" class="formee-txt" id="playable_join_{{id}}_password" /><span id="playable_join_{{id}}" class="icon icon-medium icon-playable-join" title="{{#_g}}Join{{/_g}}"></span>
'

window.settlers.setup_fetch = () ->
  eid = '#recent_events'

  update_events = () ->
    clear_events = () ->
      $(eid).html('')

    new window.hlib.Ajax
      url:		'/home/recent_events'
      handlers:
        h200:		(response, ajax) ->
          clear_events()

          __cmp = (x, y) ->
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

          response.events.playable.sort __cmp
          $(eid).html window.hlib.render(window.settlers.templates.recent_events.playables, response.events)

          $('#free_header').click () ->
            $('#free_header + section').toggle()
            $('#free_header > span').toggleClass 'icon-roll-open'
            $('#free_header > span').toggleClass 'icon-roll-close'
            return false

          if response.events.finished_chat
            window.settlers.show_menu_alert 'finished_header', response.events.finished_chat

          $('#finished_header').click () ->
            $('#finished_header + section').toggle()
            $('#finished_header > span').toggleClass 'icon-roll-open'
            $('#finished_header > span').toggleClass 'icon-roll-close'
            return false

          decorate_playable = (p) ->
            peid_plain = 'playable_' + (if p.is_game then 'game' else 'tournament') + '_' + p.id
            peid = '#' + peid_plain

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

            tooltip = window.hlib.render window.settlers.templates.recent_events.playable_preview, p
            $(peid).qtip
              id:			'playable-' + (if p.is_game then 'game' else 'tournament') + '-' + p.id
              content:
                text:			tooltip
                title:
                  text:			'#' + p.id
              position:
                target:			$(peid)
                at:			'center'
                my:			'center'
                effect:			false
              hide:
                fixed:			true
              style:
                def:			false
                classes:		'playable-preview corners-top corners-bottom'

            if p.has_password
              $('#playable_join_' + p.id).replaceWith(window.hlib.render window.settlers.templates.recent_events.password, p)

            $('#playable_join_' + p.id).click () ->
              if p.is_game
                url = '/game/join?gid=' + p.id
              else
                url = '/tournament/join?tid=' + p.id

              if p.has_password
                data =
                  password:		$('#playable_join_' + p.id + '_password').val()
              else
                data = null

              __get_field = (response) ->
                field = null

                if response.hasOwnProperty('form') and response.form.hasOwnProperty 'invalid_field'
                  field = response.form.invalid_field
                else
                  field = 'password'

                field = new window.hlib.FormField '#playable_join_' + p.id + '_' + field
                return field

              new window.hlib.Ajax
                url:			url
                data:			data
                handlers:
                  h200:		(response, ajax) ->
                    window.hlib.INFO.success window.hlib._g 'Joined'
                    update_events()

                  h400:		(response, ajax) ->
                    field = __get_field response
                    field.mark_error()

                    window.hlib.error response.error, () ->
                      field.unmark_error()

                  h401:		(response, ajax) ->
                    field = __get_field response
                    field.mark_error()

                    window.hlib.error response.error, () ->
                      field.unmark_error()

              return false

            if p.chat_posts
              window.settlers.show_menu_alert peid_plain

          decorate_playable p for p in response.events.playable
          decorate_playable p for p in response.events.free
          decorate_playable p for p in response.events.finished

          window.hlib.INFO._hide()

#  $(eid).everyTime '20s', update_events
  update_events()

window.settlers.setup_page = () ->
  window.settlers.setup_fetch()
