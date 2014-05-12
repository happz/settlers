window.settlers.events['tournament.Created']              = (e) ->
  window.hlib._g 'Tournament has been created'

window.settlers.events['tournament.Finished']             = (e) ->
  window.hlib._g 'Tournament has been finished'

window.settlers.events['tournament.Canceled']             = (e) ->
  return window.hlib._g 'Tournament has been canceled due to lack of interest'

window.settlers.events['tournament.Started']              = (e) ->
  return window.hlib._g 'Tournament has started'

window.settlers.events['tournament.PlayerJoined']             = (e) ->
  return (window.hlib._g '{0} joined tournament').format e.user.name

window.settlers = window.settlers or {}

class window.settlers.TournamentObject
  constructor:          (data) ->
    jQuery.extend true, @, data

    @my_player = @players[@my_player]

    T = @

    @events.reverse()

window.settlers.templates.game_stage = doT.template '
  {{? it.type == 0}}
    <span class="game-running">{{= window.hlib._g("Not started yet")}}</span>
  {{?? it.type == 2 || it.type == 3}}
    <span class="game-finished">{{= window.hlib._g("Finished")}}</span>
  {{??}}
    <span class="game-running">{{= window.hlib._g("Active")}}</span>
  {{?}}
'

window.settlers.templates.chat_post = doT.template '
  <tr id="chat_post_{{= it.id}}">
    <td>
      <h3>
        <span class="chat-post-unread label label-important hide">{{= window.hlib._g("Unread")}}</span>
        {{= window.settlers.fmt_player(it) }} - {{= it.time}}
        <a href="#" rel="tooltip" data-placement="right" title="{{= window.hlib._g(\'Quote\')}}" data-chat-post="{{= it.id}}">
          <span class="icon-comment-alt2-stroke"></span>
        </a>
      </h3>
      <div>
        <p>{{= it.message}}</p>
      </div>
    </td>
  </tr>
'

$(window).on 'page_startup', () ->
  tabs = new window.hlib.Tabs '#views'

  $('body').on 'hlib_update', (event, startup_check) ->
    tid = window.settlers.tournament.tid

    req = new window.hlib.Ajax
      url:			'/tournament/state'
      data:
        tid:			tid
      handlers:
        h200:			(response, ajax) ->
          window.settlers.tournament = new window.settlers.TournamentObject response.tournament
          $('body').trigger 'hlib_render'
          window.hlib.MESSAGE.hide()

          if startup_check
            startup_check()

  $('body').on 'hlib_render', (event) ->
    T = window.settlers.tournament

    $('#tournament_id').html T.tid
    $('#tournament_name').html T.name
    $('#tournament_round').html T.round
    $('#tournament_limit_round').html T.limit_rounds
    $('#tournament_num_players').html T.limit

    $('#tournament_status').hide()

    if T.stage == 0
      $('#tournament_status').html(window.hlib._g 'Waiting for more players').show()
    else if T.stage == 2
      $('#tournament_status').html(window.hlib._g('Tournament finished, winner is {0}').format(T.winner.user.name)).show()

    window.hlib.disableIcon '#show_stats'
    if T.stage == 2
      __show_stats = () ->
        tabs.show 'stats'

      window.hlib.enableIcon '#show_stats', __show_stats

    tabs.render()

  $('#players').on 'hlib_render', (event) ->
    tmpl = doT.template '
      {{? it.user.name == window.settlers.user.name}}
        <tr class="info">
      {{??}}
        <tr>
      {{?}}
        <td>{{= it.user.name}}</td>
        <td>{{= it.points}}</td>
        <td>{{= it.wins}}</td>
      </tr>'

    window.settlers.tournament.players.sort (x, y) ->
      if x.points < y.points
        return -1
      if x.points > y.points
        return 1
      if x.wins < y.wins
        return -1
      if x.wins > y.wins
        return 1
    window.settlers.tournament.players.reverse()

    $('#players table tbody').html ''
    $('#players table tbody').append(tmpl(player)) for player in window.settlers.tournament.players
    return false

  $('#rounds').on 'hlib_render', (event) ->
    tmpl = doT.template '
      {{~ it.rounds :round:round_index}}
        {{ round = it.rounds[it.rounds.length - 1 - round_index]; }}
        <h3>{{= window.hlib._g("Round")}} #{{= it.rounds.length - round_index}}</h3>
        <table class="table">
          {{~ round :group:group_index}}
            {{ num_players = group.players.length; }}
            <tr class="info">
              <td colspan="{{= num_players}}"><h4>{{= window.hlib._g("Group")}} #{{= group_index + 1}}</h4></td>
            </tr>
            {{~ group.games :game:game_index}}
              <tr>
                <td colspan="{{= num_players}}"><h5>{{= window.hlib._g("Game")}} {{= game.id}} ({{= game.round}}. {{= window.hlib._g("round")}}) - {{= window.settlers.templates.game_stage(game)}}</h5></td>
              </tr>
              <tr>
                {{~ game.players :player:pindex}}
                  <td>
                    {{= window.settlers.fmt_player(player)}}
                    {{? player.hasOwnProperty("points")}}
                      ({{= player.points}} {{= window.hlib._g("points")}})
                    {{?}}
                  </td>
                {{~}}
              </tr>
            {{~}}
          {{~}}
        </table>
        <hr />
        {{~}}'

    $('#rounds').html tmpl window.settlers.tournament
    return false

  $('#history').on 'hlib_render', (event) ->
    tmpl = doT.template '
      {{~ it.events :event:index}}
        {{? !event.hidden}}
          <tr>
            <td class="event-stamp">{{= new Date(event.stamp * 1000).strftime("%d/%m %H:%M")}}</td>
            <td class="event-round">{{= event.round}}.</td>
            <td class="event-message">{{= window.settlers.events[event.ename](event)}}</td>
          </tr>
        {{?}}
      {{~}}'

    $('#history_events').html tmpl window.settlers.tournament
    return false

  chat_preview = null
  chat_pager = null

  chat_preview = window.settlers.setup_chat_form
    eid: '#chat_post'
    handlers:
      h200: () ->
        chat_pager.refresh()
        chat_preview.preview.hide()

  chat_pager = window.settlers.setup_chat
    id_prefix: 'chat'
    eid: '#chat_posts'
    url: '/tournament/chat/'
    editor_eid: '#chat_post_text'
    preview: chat_preview
    data:
      tid: window.settlers.tournament.tid

  $('#chat').on 'hlib_render', (event) ->
    chat_pager.refresh()
    false

  $('#refresh').click () ->
    $('body').trigger 'hlib_update'
    false

  $('#show_history').click () ->
    tabs.show 'history'
    false

  $('#show_chat').click () ->
    tabs.show 'chat'
    false

  $('#show_players').click () ->
    tabs.show 'players'
    false

  $('#show_rounds').click () ->
    tabs.show 'rounds'
    false

  $('#show_stats').click () ->
    tabs.show 'stats'
    false

  $('body').trigger 'hlib_update', () ->
    tabs.show_by_hash 'players'
