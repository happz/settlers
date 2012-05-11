window.settlers.templates.recent_events = {}
window.settlers.templates.recent_events.games = '
  <li class="header">Games</li>
  {{#games}}
    <li id="game_{{id}}" class="info info-with-menu">
      <span class="game-name">{{name}}</span>
      <span class="game-menu right">
        {{#is_present}}
          {{#is_invited}}
            <span id="game_join_{{id}}" class="icon icon-medium icon-game-join" title="Join game"></span>
          {{/is_invited}}
          {{^is_invited}}
            {{#is_on_turn}}
              <a href="/game/?gid={{id}}#board" title="On turn!"><span class="icon icon-medium icon-game-on-turn"></span></a>
            {{/is_on_turn}}
            <a href="/game/?gid={{id}}#board" title="Open board"><span class="icon icon-medium icon-game-board"></span></a>
            <a href="/game/?gid={{id}}#history" title="Open history"><span class="icon icon-medium icon-game-history"></span></a>
            <a href="/game/?gid={{id}}#chat" title="Open chat">
              <span class="icon icon-medium icon-game-chat">
                {{#chat_posts}}
                  <span class="menu-alert">{{chat_posts}}</span>
                {{/chat_posts}}
              </span>
            </a>
          {{/is_invited}}
        {{/is_present}}
        {{^is_present}}
          <span id="game_join_{{id}}" class="icon icon-medium icon-game-join" title="Join game"></span>
        {{/is_present}}
      </span>
    </li>
  {{/games}}

  <li id="free_games_header" class="header">
    Free games ({{free_games.length}} games)
    <span class="right icon icon-medium icon-roll-open"></span>
  </li>
  <div class="hide">
  {{#free_games}}
    <li id="game_{{id}}" class="info info-with-menu">
      <span class="game-name">{{name}}</span>
      <span class="game-menu right">
        <span id="game_join_{{id}}" title="Join game" class="icon icon-medium icon-game-join"></span>
      </span>
    </li>
  {{/free_games}}
  </div>

  <li id="finished_games_header" class="header">
    Finished games ({{finished_games.length}} games)
    <span class="right icon icon-medium icon-roll-open"></span>
  </li>
  <div class="hide">
  {{#finished_games}}
    <li id="game_{{id}}" class="info info-with-menu">
      <span class="game-name">{{name}}</span>
      <span class="game-menu right">
        <a href="/game/?gid={{id}}#board" title="Open board"><span class="icon icon-medium icon-game-board"></span></a>
        <a href="/game/?gid={{id}}#history" title="Open history"><span class="icon icon-medium icon-game-history"></span></a>
        <a href="/game/?gid={{id}}#chat" title="Open chat">
          <span class="icon icon-medium icon-game-chat">
            {{#chat_posts}}
              <span class="menu-alert">{{chat_posts}}</span>
            {{/chat_posts}}
          </span>
        </a>
      </span>
    </li>
  {{/finished_games}}
  </div>
'
window.settlers.templates.recent_events.game_preview = '
  <div class="bold">{{name}}</div>
  <div class="game-players">{{{players_list}}}</div>
  <div class="game-limit">For {{limit}} players</div>
  {{#round}}
    <div class="game-round">{{round}}. round, {{forhont.name}} on turn</div>
  {{/round}}
  {{#is_invited}}
    <div style="font-weight: bold">You are invited!</div>
  {{/is_invited}}
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

          response.events.games.sort __cmp
          $(eid).html window.hlib.render(window.settlers.templates.recent_events.games, response.events)

          $('#free_games_header').click () ->
            $('#free_games_header + div').toggle()
            $('#free_games_header > span').toggleClass 'icon-roll-open'
            $('#free_games_header > span').toggleClass 'icon-roll-close'
            return false

          $('#finished_games_header').click () ->
            $('#finished_games_header + div').toggle()
            $('#finished_games_header > span').toggleClass 'icon-roll-open'
            $('#finished_games_header > span').toggleClass 'icon-roll-close'
            return false

          decorate_game = (g) ->
            geid = '#game_' + g.id

            g.players_list = () ->
              l = []

              __fmt_user = (u) ->
                s = u.name

                if u.is_online == true
                  s = '<span class="user-online">' + s + '</span>'

                if u.is_confirmed != true
                  s = '<span class="user-invited">' + s + '</span>'

                if u.is_on_turn == true
                  s = '<span class="user-onturn">' + s + '</span>'

                return s
              
              l = (__fmt_user u for u in g.players)
              return l.join ', '

            tooltip = window.hlib.render window.settlers.templates.recent_events.game_preview, g
            $(geid).qtip
              id:			'game-' + g.id
              content:
                text:			tooltip
                title:
                  text:			'Game #' + g.id
              position:
                target:			$(geid)
                at:			'center'
                my:			'center'
                effect:			false
              hide:
                fixed:			true
              style:
                def:			false
                classes:		'game-preview corners-top corners-bottom'

            $('#game_join_' + g.id).click () ->
              new window.hlib.Ajax
                url:			'/game/join?gid=' + g.id
                handlers:
                  h200:		(response, ajax) ->
                    window.hlib.INFO.success 'Game joined'
                    update_events()

              return false

            if g.chat_posts
              window.settlers.show_menu_alert 'game_' + g.id
            # if g.has_password ...

          decorate_game g for g in response.events.games
          decorate_game g for g in response.events.free_games
          decorate_game g for g in response.events.finished_games

          window.hlib.INFO._hide()

#  $(eid).everyTime '20s', update_events
  update_events()

window.settlers.setup_page = () ->
  window.settlers.setup_fetch()
