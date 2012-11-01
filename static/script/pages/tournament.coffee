window.settlers.events['tournament.Created']              = (e) ->
  window.hlib._g 'Tournament has been created'

window.settlers.events['tournament.Finished']             = (e) ->
  window.hlib._g 'Tournament has been finished'

window.settlers.events['tournament.Canceled']             = (e) ->
  return window.hlib._g 'Tournament has been canceled due to lack of interest'

window.settlers.events['tournament.Started']              = (e) ->
  return window.hlib._g 'Tournament has started'

window.settlers.events['tournament.PlayerJoined']             = (e) ->
  return (window.hlib._g '{0} joined game').format e.user.name

window.settlers = window.settlers or {}

class window.settlers.tournamentObject
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
  <div class="game-player">
    <div class="game-player-header header corners-top settlers-game-player-header-{{color.name}}">
      <span class="game-player-title">{{user.name}}</span>

      <span class="right">
        <span class="icon settlers-player-title-icon 
        {{#has_mightest_chilvary}}
          settlers-icon-chilvary-on
        {{/has_mightest_chilvary}}
        {{^has_mightest_chilvary}}
          settlers-icon-chilvary-off
        {{/has_mightest_chilvary}}
        "></span>
  
      <span class="icon settlers-player-title-icon
        {{#has_longest_path}}
          settlers-icon-path-on
        {{/has_longest_path}}
        {{^has_longest_path}}
          settlers-icon-path-off
        {{/has_longest_path}} 
        "></span>
    </div>

    <div class="game-player-points info important-info">{{points}} {{#_g}}points{{/_g}}</div>

    <table class="game-player-resources">

    {{#my_player}}
      <tr class="info"><td>{{#_g}}Wood{{/_g}}:</td><td>{{resources.wood}}</td></tr>
      <tr class="info"><td>{{#_g}}Clay{{/_g}}:</td><td>{{resources.clay}}</td></tr>
      <tr class="info"><td>{{#_g}}Sheep{{/_g}}:</td><td>{{resources.sheep}}</td></tr>
      <tr class="info"><td>{{#_g}}Grain{{/_g}}:</td><td>{{resources.grain}}</td></tr>
      <tr class="info"><td>{{#_g}}Rock{{/_g}}:</td><td>{{resources.rock}}</td></tr>
    {{/my_player}}
    {{^my_player}}
      <tr class="info"><td>{{#_g}}Resources{{/_g}}:</td><td>{{resources.total}}</td></tr>
    {{/my_player}}

    {{#my_player}}
      </table>
      <div class="info"><hr /></div>
      <table class="game-player-resources">
    {{/my_player}}

    {{#my_player}}
      <tr class="info"><td>{{#_g}}Cards{{/_g}}:</td><td>{{cards.length}}</td></tr>
    {{/my_player}}
    {{^my_player}}
      <tr class="info"><td>{{#_g}}Cards{{/_g}}:</td><td>{{cards}}</td></tr>
    {{/my_player}}

      <tr class="info game-player-knights corners-bottom"><td>{{#_g}}Knights{{/_g}}:</td><td>{{knights}}</td></tr>
    </table>
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
  tid = window.settlers.tournament.gid

  req = window.hlib.Ajax
    url:                '/tournament/state'
    data:
      tid:              tid
    handlers:
      h200:             (response, ajax) ->
        window.settlers.tournament = new window.settlers.TournamentObject response.tournament
        window.settlers.update_tournament_ui()
        window.hlib.INFO._hide()

window.settlers.update_tournament_ui_info = () ->
  T = window.settlers.tournament

  $('#tournament_id').html G.gid
  $('#game_name').html G.name
  $('#game_round').html G.round

  if G.last_numbers.length > 0
    $('#settlers_last_numbers').html G.last_numbers.join ', '
    $('.settlers-last-numbers').show()

window.settlers.update_tournament_ui_player = (player) ->
  dst_id = '#tournament-player-' + player.id + '-placeholder'

  $(dst_id).html ''
  rendered = window.hlib.render window.settlers.templates.tournament.player, player
  $(dst_id).html rendered

window.settlers.update_tournament_ui_players = () ->
  window.settlers.update_tournament_ui_player p for p in window.settlers.tournament.players

window.settlers.update_tournament_ui_history = () ->
  rendered = window.settlers.tournament.render_events window.settlers.events, window.settlers.templates.tournament.events
  $('#history_events').html rendered

window.settlers.update_game_ui = () ->
  window.settlers.update_game_ui_info()
  window.settlers.update_tournament_ui_players()
  window.settlers.update_game_ui_status()
  window.settlers.update_tournament_ui_history()

window.settlers.setup_page = () ->
  show_players = () ->
    $('#views').tabs 'select', 0
    window.location.hash = ''

  show_chat = () ->
    $('#views').tabs 'select', 1
    window.location.hash = '#chat'

  show_history = () ->
    $('#views').tabs 'select', 2
    window.location.hash = '#history'

  $('#views').tabs()

  chat_pager = window.settlers.setup_chat
    id_prefix:                  'chat'
    eid:                        '#chat_posts'
    url:                        '/tournament/chat/page'
    data:
      gid:                      window.settlers.tournament.gid

  window.settlers.setup_chat_form
    eid:                        '#chat_post'
    handlers:
      h200:             () ->
        chat_pager.refresh()

  window.settlers.update_tournament_state()

  $('#refresh').click () ->
    window.settlers.update_game_state()
    return false

  $('#show_history').click () ->
    show_history()
    return false

  $('#show_chat').click () ->
    show_chat()
    return false

  if window.location.hash == '#chat'
    show_chat()

  else if window.location.hash == '#history'
    show_history()

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
