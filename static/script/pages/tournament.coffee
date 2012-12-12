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

window.settlers.templates.tournament = {}
window.settlers.templates.tournament.player = doT.template '
  <div class="playable-player">
    <div class="tournament-player-header">
      <h4>{{= it.user.name}}</h4>
    </div>

    <table class="table table-condensed">
      <tr class="info"><td><strong>{{= window.hlib._g("Points")}}:</strong></td><td><strong>{{= it.points}}</strong></td></tr>
    </table>
  </div>
'
window.settlers.templates.tournament.events = doT.template '
  {{~ it.events :event:index}}
    {{? !event.hidden}}
      <tr>
        <td class="event-stamp">{{= new Date(event.stamp * 1000).strftime("%d/%m %H:%M")}}</td>
        <td class="event-round">{{= event.round}}.</td>
        <td class="event-message">{{= window.settlers.events[event.ename](event)}}</td>
      </tr>
    {{?}}
  {{~}}
'

window.settlers.update_tournament_state = () ->
  tid = window.settlers.tournament.tid

  req = window.hlib.Ajax
    url:                '/tournament/state'
    data:
      tid:              tid
    handlers:
      h200:             (response, ajax) ->
        window.settlers.tournament = new window.settlers.TournamentObject response.tournament
        window.settlers.update_tournament_ui()
        window.hlib.MESSAGE.hide()

window.settlers.update_tournament_ui_info = () ->
  T = window.settlers.tournament

  $('#tournament_id').html T.tid
  $('#tournament_name').html T.name
  $('#tournament_round').html T.round
  $('#tournament_num_players').html T.num_players

window.settlers.update_tournament_ui_status = () ->
  T = window.settlers.tournament
  eid = '#tournament_status'

  $(eid).hide()

  if T.stage == 0
   $(eid).html(window.hlib._g 'Waiting for more players').show()

window.settlers.update_tournament_ui_player = (player) ->
  $('#players').append window.settlers.templates.tournament.player player

window.settlers.update_tournament_ui_players = () ->
  $('#players').html ''

  window.settlers.update_tournament_ui_player p for p in window.settlers.tournament.players

window.settlers.update_tournament_ui_history = () ->
  $('#history_events').html window.settlers.templates.tournament.events window.settlers.tournament

window.settlers.update_tournament_ui_buttons = () ->
  # reset to default
  window.hlib.disableIcon '#show_stats'

  T = window.settlers.tournament

  if T.stage == 2
    window.hlib.enableIcon '#show_stats', window.settlers.show_stats

window.settlers.update_tournament_ui = () ->
  window.settlers.update_tournament_ui_info()
  window.settlers.update_tournament_ui_status()
  window.settlers.update_tournament_ui_players()
  window.settlers.update_tournament_ui_history()
  window.settlers.update_tournament_ui_buttons()

$(window).bind 'page_startup', () ->
  show_players = () ->
    $('#views').tabs 'select', 1
    window.location.hash = ''

  show_chat = () ->
    $('#views').tabs 'select', 2
    window.location.hash = '#chat'

  show_history = () ->
    $('#views').tabs 'select', 3
    window.location.hash = '#history'

  show_rounds = () ->
    $('#views').tabs 'select', 4
    window.location.hash = '#rounds'

  window.settlers.show_stats = () ->
    $('#views').tabs 'select', 5
    window.location.hash = '#stats'

  $('#views').tabs()

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

  window.settlers.update_tournament_state()

  $('#refresh').click () ->
    window.settlers.update_tournament_state()
    return false

  $('#show_history').click () ->
    show_history()
    return false

  $('#show_chat').click () ->
    show_chat()
    return false

  $('#show_players').click () ->
    show_players()
    return false

  $('#show_rounds').click () ->
    show_rounds()

  $('#show_stats').click () ->
    window.settlers.show_stats()

  if window.location.hash == '#chat'
    show_chat()

  else if window.location.hash == '#history'
    show_history()

  else if window.location.hash == '#rounds'
    show_rounds()

  else if window.location.hash == '#stats'
    window.settlers.show_stats()

  else
    show_players()

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
