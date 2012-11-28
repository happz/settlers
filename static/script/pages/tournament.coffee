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

  render_events:        (event_formatters, list_template) ->
    __per_event = (e) ->
      d = new Date (e.stamp * 1000)
      e.stamp_formatted = d.strftime '%d/%m %H:%M'
      e.message = event_formatters[e.ename] e

    __per_event e for e in @events
    @events.reverse()
    return window.hlib.render list_template, @

window.settlers.templates.tournament = {}
window.settlers.templates.tournament.player = '
  <div class="tournament-player corners-bottom">
    <div class="tournament-player-header corners-top header">
      <span class="tournament-player-title">{{user.name}}</span>
    </div>

    <div class="tournament-player-points info important">{{points}} {{#_g}}points{{/_g}}</div>

    <table class="tournament-player-info"></table>
  </div>
'
window.settlers.templates.tournament.events = '
  {{#events}}
    {{^hidden}}
      <tr>
        <td class="event-stamp">{{stamp_formatted}}</td>
        <td class="event-round">{{round}}.</td>
        <td class="event-message">{{message}}</td>
      </tr>
    {{/hidden}}
  {{/events}}
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

window.settlers.update_tournament_ui_player = (player) ->
  rendered = window.hlib.render window.settlers.templates.tournament.player, player
  $('#players').append rendered

window.settlers.update_tournament_ui_players = () ->
  $('#players').html ''

  window.settlers.update_tournament_ui_player p for p in window.settlers.tournament.players

window.settlers.update_tournament_ui_history = () ->
  rendered = window.settlers.tournament.render_events window.settlers.events, window.settlers.templates.tournament.events
  $('#history_events').html rendered

window.settlers.update_tournament_ui = () ->
  window.settlers.update_tournament_ui_info()
  window.settlers.update_tournament_ui_players()
  window.settlers.update_tournament_ui_history()

window.settlers.setup_page = () ->
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

  if window.location.hash == '#chat'
    show_chat()

  else if window.location.hash == '#history'
    show_history()

  else if window.location.hash == '#rounds'
    show_rounds()

  else
    show_players()

window.settlers.templates.chat_post = '
  <fieldset class="chat-post">
    <legend>
      {{#user.is_online}}
        <span class="user-online">
      {{/user.is_online}}
      {{user.name}}
      {{#user.is_online}}
        </span>   
      {{/user.is_online}} - {{time}}
    </legend>
    <div>{{{message}}}</div>
  </fieldset>
'
