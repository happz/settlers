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

window.settlers.templates.chat_post = doT.template '
 <tr id="chat_post_{{= it.id}}">
    <td>
      <h3>
        <span class="chat-post-unread label label-important hide">Unread</span>
        {{? it.user.is_online}}
          <span class="user-online">
        {{?}}
        {{= it.user.name}}
        {{? it.user.is_online}}
          </span>
        {{?}} - {{= it.time}}
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

    req = window.hlib.Ajax
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
    $('#tournament_num_players').html T.num_players

    $('#tournament_status').hide()

    if T.stage == 0
      $('#tournament_status').html(window.hlib._g 'Waiting for more players').show()

    window.hlib.disableIcon '#show_stats'
    if T.stage == 2
      window.hlib.enableIcon '#show_stats', window.settlers.show_stats

    tabs.render()

  $('#players').on 'hlib_render', (event) ->
    tmpl = doT.template '
      <div class="playable-player">
        <div class="tournament-player-header">
          <h4>{{= it.user.name}}</h4>
        </div>
        <table class="table table-condensed">
          <tr class="info"><td><strong>{{= it.points}} {{= window.hlib._g("points")}}</strong></td></tr>
        </table>
      </div>'

    $('#players').html ''
    $('#players').append(tmpl(player)) for player in window.settlers.tournament.players
    return false

  $('#rounds').on 'hlib_render', (event) ->
    tmpl = doT.template '
      {{~ it.rounds :round:round_index}}
        <h3>{{= window.hlib._g("Round")}} #{{= round_index + 1}}</h3>
        <table class="table">
          {{~ round :group:group_index}}
            {{ num_players = group.players.length; }}
            <tr class="info">
              <td colspan="{{= num_players}}"><h4>{{= window.hlib._g("Group")}} #{{= group_index + 1}}</h4></td>
            </tr>
            {{~ group.games :game:game_index}}
              <tr>
                <td colspan="{{= num_players}}"><h5>{{= window.hlib._g("Game")}} {{= game.id}} ({{= game.round}}. {{= window.hlib._g("round")}})</h5></td>
              </tr>
              <tr>
                {{~ game.players :player:pindex}}
                  <td>{{= window.settlers.fmt_player(player)}} ({{= player.points}} {{= window.hlib._g("points")}})</td>
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

  chat_pager = window.settlers.setup_chat
    id_prefix:                  'chat'
    eid:                        '#chat_posts'
    url:                        '/tournament/chat/page'
    data:
      tid:                      window.settlers.tournament.tid

  window.settlers.setup_chat_form
    eid:                        '#chat_post'
    handlers:
      h200:             () ->
        chat_pager.refresh()

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
