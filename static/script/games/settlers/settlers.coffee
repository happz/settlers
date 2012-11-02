_log_enabled = false
_log = (args...) ->
  if window.settlers._log_enabled == true
    console.log args

window.settlers = window.settlers or {}
window.settlers._log_enabled = false

window.settlers.format_event_resources = (rs) ->
  return (window.hlib._g '{0} wood, {1} clay, {2} sheep, {3} grain, {4} rock').format rs.wood, rs.clay, rs.sheep, rs.grain, rs.rock

window.settlers.events['game.CardUsed']					= (e) ->
  return (window.hlib._g '{0} used card {1} from round {2}').format e.user.name, (window.hlib._g window.settlers.game.card_type_to_name[e.card.type]), e.card.bought

window.settlers.events = window.settlers.events or {}
window.settlers.events['game.settlers.LongestPathBonusEarned']		= (e) ->
  return 'game.settlers.LongestPathBonusEarned'
window.settlers.events['game.settlers.MightestChilvaryBonusEarned']	= (e) ->
  return 'game.settlers.MightestChilvaryBonusEarned'

window.settlers.events['game.settlers.ResourceStolen']			= (e) ->
  if e.am_i_thief == true
    return (window.hlib._g 'You stole 1 piece of {0} from {1}').format e.resource, e.victim.name

  if e.am_i_victim == true
    return (window.hlib._g '{0} stole 1 piece of {1} from you').format e.thief.name, e.resource

  return (window.hlib._g '{0} stole 1 piece of resources from {1}').format e.thief.name, e.victim.name

window.settlers.events['game.settlers.ResourcesStolen']			= (e) ->
  if e.am_i_thief != true
    if e.am_i_victim
      return (window.hlib._g 'Thief stole you resources: {0}').format window.settlers.format_event_resources e.resources

    else
      rs = e.resources
      return (window.hlib._g 'Thief stole {0} {1} resources').format e.victim.name, (rs.wood + rs.clay + rs.sheep + rs.grain + rs.rock)

  return ''

window.settlers.events['game.settlers.DiceRolled']			= (e) ->
  return 'game.settlers.DiceRolled'
window.settlers.events['game.settlers.VillageBuilt']			= (e) ->
  return 'game.settlers.VillageBuilt'
window.settlers.events['game.settlers.TownBuild']			= (e) ->
  return 'game.settlers.TownBuild'
window.settlers.events['game.settlers.ResourcesReceived']		= (e) ->
  return (window.hlib._g '{0} received these resources: {1}').format e.user.name, (window.settlers.format_event_resources e.resources)

window.settlers.events['game.settlers.ResourcesExchanged']		= (e) ->
  return (window.hlib._g '{0} exchanged resources: {1} for {2}').format e.user.name, (window.settlers.format_event_resources e.src), (window.settlers.format_event_resources e.dst)

window.settlers.events['game.settlers.Monopoly']			= (e) ->
  return (window.hlib._g '{0} stole resources from {1}: {2}').format e.thief.name, e.victim.name, (window.settlers.format_event_resources e.resources)

window.settlers.events['game.settlers.ThiefPlaced']			= (e) ->
  return (window.hlib._g '{0} moved thief').format e.user.name

class window.settlers.GameObject
  resource_id_to_name:		['sheep', 'wood', 'rock', 'grain', 'clay']
  card_type_to_name:		['undefined', 'Knight', 'Monopoly', 'Paths', 'Invention', 'Point']

  constructor:		(data) ->
    jQuery.extend true, @, data

    @my_player = @players[@my_player]
    @forhont_player = @players[@forhont_player]

    G = @

    __per_player = (p) ->
      if p.first_village
        p.first_village = G.board.nodes[p.first_village - 1]

      if p.second_village
        p.second_village = G.board.nodes[p.second_village - 1]

    __per_player p for p in @players

    @current_node = null
    @current_path = null

    @current_active_nodes_map = null
    @current_active_paths_map = null

  get_thief_field:	() ->
    fields = @board.fields.filter (f) -> f.thief == true
    return fields[0]

  get_nodes_by_field:	(field) ->
    nodes = []

    __per_node = (node) ->
      if field.id in window.settlers.board_defs.nodes[node.id].fields
        nodes.push n

    __per_node n for n in @board.nodes
    return nodes

  get_path_sibling_by_node:	(path, node, index) ->
    G = @
    i = 0
    ret = null

    __per_path = (pid) ->
      if ret
        return

      if pid == path.id
        index += 1
        i += 1
        return

      if i == index
        ret = G.board.paths[pid - 1]
        return

      i += 1

    __per_path pid for pid in window.settlers.board_defs.nodes[node.id].paths
    return ret

  get_free_paths_map_by_node:		(node) ->
    G = @
    m = jQuery.extend {}, window.settlers.board_defs.active_paths_map_positive

    m[pid] = (G.board.paths[pid - 1].type == 1) for pid in window.settlers.board_defs.nodes[node.id].paths

    return m

  active_nodes_map:	() ->
    P = @my_player

    if not P.is_on_turn
      return window.settlers.board_defs.active_nodes_map_negative

    if @state == 10 or @state == 11
      m = jQuery.extend {}, window.settlers.board_defs.active_nodes_map_positive

      __per_node = (node) ->
        if node.type == 1
          return

        m[node.id] = false
        m[neighbour_id] = false for neighbour_id in window.settlers.board_defs.nodes[ node.id].neighbours

      __per_node node for node in @board.nodes
      return m

    if @state == 14 or @state == 16 or @state == 20
      thief_field = @get_thief_field()
      nodes = @get_nodes_by_field thief_field

      m = jQuery.extend {}, window.settlers.board_defs.active_nodes_map_negative

      __per_node = (node) ->
        if node.type != 1 and node.owner != P.id
          m[node.id] = true

      __per_node node for node in nodes

      return m

    if @state == 1
      G = @
      m = jQuery.extend {}, window.settlers.board_defs.active_nodes_map_positive

      __per_node = (node) ->
        if m[node.id] == false
          return

        if node.type != 1
          m[neighbour_id] = false for neighbour_id in window.settlers.board_defs.nodes[node.id].neighbours

          if node.type != 2 or node.owner != P.id
            m[node.id] = false

          return

        found = false
        __per_path = (pid) ->
          if G.board.paths[pid - 1].owner == P.id
            found = true

        __per_path pid for pid in window.settlers.board_defs.nodes[node.id].paths

        m[node.id] = found

      __per_node node for node in @board.nodes
      return m

    return jQuery.extend {}, window.settlers.board_defs.active_nodes_map_negative

  active_paths_map:	() ->
    G = @
    P = @my_player

    if not P.is_on_turn
      return window.settlers.board_defs.active_paths_map_negative

    if G.state == 10
      if not G.my_player.first_village
        return window.settlers.board_defs.active_paths_map_negative

      return G.get_free_paths_map_by_node G.my_player.first_village

    if G.state == 11
      if not G.my_player.second_village
        return window.settlers.board_defs.active_paths_map_negative

      return G.get_free_paths_map_by_node G.my_player.second_village

    if G.state == 1 or G.state == 22 or G.state == 23
      m = jQuery.extend true, {}, window.settlers.board_defs.active_paths_map_negative

      __per_path = (path) ->
        if path.type != 1
          return

        node1 = G.board.nodes[window.settlers.board_defs.paths[path.id].nodes[0] - 1]
        node2 = G.board.nodes[window.settlers.board_defs.paths[path.id].nodes[1] - 1]

        if node1.owner == P.id or node2.owner == P.id
          m[path.id] = true
          return

        sibling1 = null
        sibling2 = null

        sibling1 = G.get_path_sibling_by_node path, node1, 0
        if sibling1 and (sibling1.type != 2 or sibling1.owner != G.my_player.id)
          sibling1 = null

        if not sibling1
          sibling1 = G.get_path_sibling_by_node path, node1, 1
          if sibling1 and (sibling1.type != 2 or sibling1.owner != G.my_player.id)
            sibling1 = null

        sibling2 = G.get_path_sibling_by_node path, node2, 0
        if sibling2 and (sibling2.type != 2 or sibling2.owner != G.my_player.id)
          sibling2 = null

        if not sibling2
          sibling2 = G.get_path_sibling_by_node path, node2, 1
          if sibling2 and (sibling2.type != 2 or sibling2.owner != G.my_player.id)
            sibling2 = null

        if sibling1 and not sibling2 and node1.type != 1
          return

        if sibling2 and not sibling1 and node2.type != 1
          return

        m[path.id] = (sibling1 != null or sibling2 != null)

      __per_path path for path in G.board.paths
      return m

    return window.settlers.board_defs.active_paths_map_negative

  render_events:	(event_formatters, list_template) ->
    __per_event = (e) ->
      d = new Date (e.stamp * 1000)
      e.stamp_formatted = d.strftime '%d/%m %H:%M'
      e.message = event_formatters[e.ename] e

    __per_event e for e in @events
    @events.reverse()
    return window.hlib.render list_template, @

  resources_values:	(rs) ->
    return [rs.wood, rs.clay, rs.sheep, rs.grain, rs.rock]

  get_used_ports:	(player, resource) ->
    G = @
    ret = []

    __per_port = (p) ->
      if p.resource != resource
        return

      n = G.board.nodes[p.nodes[0] - 1]
      if (n.type == 2 or n.type == 3) and n.owner == player.id
        ret.push p

      n = G.board.nodes[p.nodes[1] - 1]
      if (n.type == 2 or n.type == 3) and n.owner == player.id
        ret.push p

    __per_port p for p in @board.ports

    return ret

  can_exchange_common:	() ->
    return @state == 1

  can_exchange_four:	() ->
    if not @can_exchange_common()
      return false

    return (Math.max.apply Math, (@resources_values @my_player.resources)) >= 4

  can_exchange_three:	() ->
    if not @can_exchange_common()
      return false

    return (Math.max.apply(Math, @resources_values(@my_player.resources)) >= 3 and (@get_used_ports @my_player, -2).length > 0)

  can_exchange_two:	() ->
    G = @

    if not @can_exchange_common()
      return false

    ret = false

    __per_resource = (resource) ->
      if G.my_player.resources[G.resource_id_to_name[resource]] >= 2 and (G.get_used_ports G.my_player, resource).length > 0
        ret = true

    __per_resource r for r in [0, 1, 2, 3, 4]

    return ret

  can_exchange:		() ->
    return @can_exchange_four() or @can_exchange_three() or @can_exchange_two()

window.settlers.templates.game = {}
window.settlers.templates.game.player = '
  <div class="playable-player">
    <div class="playable-player-header header corners-top settlers-game-player-header-{{color.name}}">
      <span class="playable-player-title">{{user.name}}</span>

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

    <div class="playable-player-points info important-info">{{points}} {{#_g}}points{{/_g}}</div>

    <table class="game-player-resources">

    {{#my_player}}
      <tr class="info"><td>{{#_g}}Wood{{/_g}}:</td><td>{{resources.wood}}</td></tr>
      <tr class="info"><td>{{#_g}}Clay{{/_g}}:</td><td>{{resources.clay}}</td></tr>
      <tr class="info"><td>{{#_g}}Sheep{{/_g}}:</td><td>{{resources.sheep}}</td></tr>
      <tr class="info"><td>{{#_g}}Grain{{/_g}}:</td><td>{{resources.grain}}</td></tr>
      <tr class="info"><td>{{#_g}}Rock{{/_g}}:</td><td>{{resources.rock}}</td></tr>
      <tr class="info important-info"><td>{{#_g}}Total{{/_g}}:</td><td>{{resources.total}}</td></tr>
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
window.settlers.templates.game.cards = '
  <ul class="game-cards">
    <li class="header">{{#_g}}Cards{{/_g}}</li>
    {{#cards}}
      <li id="card_{{id}}" class="info info-with-menu">
        <span class="card-type">{{type_name}}</span>
        {{#can_be_used}}
          <span class="card-menu right">
            <span id="card_use_{{id}}" class="icon icon-medium icon-card-use"></span>
          </span>
        {{/can_be_used}}
      </li>
    {{/cards}}
  </ul>
'
window.settlers.templates.game.events = '
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
window.settlers.templates.game.exchange = window.settlers.templates.game.exchange or {}
window.settlers.templates.game.exchange.amount = '
  <option value="" selected="selected">{{#_g}}# pieces of ...{{/_g}}</option>
  {{#amounts}}
    <option value="{{amount}}">{{amount}}</option>
  {{/amounts}}
'
window.settlers.templates.game.exchange.resources = '
  <option value="" selected="selected">{{hint}}</option>
  {{#resources}}
    <option value="{{resource}}">{{resource_label}}</option>
  {{/resources}}
'

window.settlers.update_game_state = () ->
  gid = window.settlers.game.gid

  req = window.hlib.Ajax
    url:		'/game/state'
    data:
      gid:		gid
    handlers:
      h200:		(response, ajax) ->
        window.settlers.game = new window.settlers.GameObject response.game
        window.settlers.update_game_ui()
        window.hlib.INFO._hide()

window.settlers.__refresh_game_ui_exchange = (i) ->
  eid_prefix = '#exchange_' + i

  $(eid_prefix).hide()

  G = window.settlers.game
  my_player = G.my_player

  if i == 4
    if G.can_exchange_four() != true
      return
  else if i == 3
    if G.can_exchange_three() != true
      return
  else if i == 2
    if G.can_exchange_two() != true
      return

  __mk_resource_option = (j) ->
    return { resource: j, resource_label: window.hlib._g G.resource_id_to_name[j].capitalize() }

  amounts =
    amounts:	[]

  amounts.amounts.push { amount: n } for n in [i..Math.max.apply Math, (G.resources_values G.my_player.resources)] by i

  dst_resources =
    hint:		window.hlib._g 'To ...'
    resources:		[
      __mk_resource_option 1
      __mk_resource_option 4
      __mk_resource_option 3
      __mk_resource_option 0
      __mk_resource_option 2
    ]

  src_resources =
    hint:		window.hlib._g 'From ...'
    resources:		[
    ]

  if i == 4
    if my_player.resources.wood >= i
      src_resources.resources.push __mk_resource_option 1
    if my_player.resources.clay >= i
      src_resources.resources.push __mk_resource_option 4
    if my_player.resources.grain >= i
      src_resources.resources.push __mk_resource_option 3
    if my_player.resources.sheep >= i
      src_resources.resources.push __mk_resource_option 0
    if my_player.resources.rock >= i
      src_resources.resources.push __mk_resource_option 2

  else if i == 3 and G.can_exchange_three() == true
    if my_player.resources.wood >= i
      src_resources.resources.push __mk_resource_option 1
    if my_player.resources.clay >= i
      src_resources.resources.push __mk_resource_option 4
    if my_player.resources.grain >= i
      src_resources.resources.push __mk_resource_option 3
    if my_player.resources.sheep >= i
      src_resources.resources.push __mk_resource_option 0
    if my_player.resources.rock >= i
      src_resources.resources.push __mk_resource_option 2

  else if i == 2
    if G.my_player.resources.wood >= 2 and (G.get_used_ports G.my_player, 1).length > 0
      src_resources.resources.push __mk_resource_option 1
    if G.my_player.resources.clay >= 2 and (G.get_used_ports G.my_player, 4).length > 0
      src_resources.resources.push __mk_resource_option 4
    if G.my_player.resources.grain >= 2 and (G.get_used_ports G.my_player, 3).length > 0
      src_resources.resources.push __mk_resource_option 3
    if G.my_player.resources.sheep >= 2 and (G.get_used_ports G.my_player, 0).length > 0
      src_resources.resources.push __mk_resource_option 0
    if G.my_player.resources.rock >= 2 and (G.get_used_ports G.my_player, 2).length > 0
      src_resources.resources.push __mk_resource_option 2

  $(eid_prefix + '_gid').val G.gid
  $(eid_prefix + '_ratio').val i
  $(eid_prefix + '_amount').html window.hlib.render window.settlers.templates.game.exchange.amount, amounts
  $(eid_prefix + '_src').html window.hlib.render window.settlers.templates.game.exchange.resources, src_resources
  $(eid_prefix + '_dst').html window.hlib.render window.settlers.templates.game.exchange.resources, dst_resources

  $(eid_prefix).show()

window.settlers.update_game_ui_exchange = () ->
  window.settlers.__refresh_game_ui_exchange i for i in [2, 3, 4]

  if window.settlers.game.can_exchange() == true
    $('#exchange_no').hide()
  else
    $('#exchange_no').show()

window.settlers.update_game_ui_info = () ->
  $('.settlers-last-numbers').hide()
  $('.settlers-game-status').hide()

  G = window.settlers.game

  $('#game_id').html G.gid
  $('#game_name').html G.name
  $('#game_round').html G.round

  if G.last_numbers.length > 0
    s = G.last_numbers.slice()
    s[0] = '<span class="label green">' + s[0] + '</span>'
    $('#settlers_last_numbers').html s.join ' '
    $('.settlers-last-numbers').show()

window.settlers.update_game_ui_player = (player) ->
  dst_id = '#game-player-' + player.id + '-placeholder'

  $(dst_id).html ''
  rendered = window.hlib.render window.settlers.templates.game.player, player
  $(dst_id).html rendered

window.settlers.update_game_ui_players = () ->
  window.settlers.update_game_ui_player p for p in window.settlers.game.players

window.settlers.update_game_ui_board = () ->
  eid = '.game-board'
  G = window.settlers.game
  bs = G.render_info.board_skin

  map_resource_to_str = ['free', 'unknown', 'sheep', 'wood', 'rock', 'grain', 'clay', 'desert']
  map_nodetype_to_str = ['unused', 'free', 'village', 'town']
  map_pathid_to_position = ['undefined', 'lt', 'rt', 't', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'rt', 'lt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'lt', 'rt', 't', 'rt', 'lt', 'rt', 'lt', 'rt', 'lt', 'rt']

  G.current_active_nodes_map = window.settlers.game.active_nodes_map()
  G.current_active_paths_map = window.settlers.game.active_paths_map()

  $(eid).html ''

  __add_field = (f) ->
    attrs =
      id:		'settlers_board_field_' + f.id
      class:		'settlers-board-piece settlers-board-field settlers-board-field-' + f.id + ' settlers-board-field-' + bs + '-' + map_resource_to_str[f.resource + 2]

    $(eid).append window.settlers.render_board_piece attrs

    if f.thief == true
      attrs =
        class:		'settlers-board-piece settlers-board-thief settlers-board-thief-' + bs + ' settlers-board-thief-' + f.id

      $(eid).append window.settlers.render_board_piece attrs

  __add_number = (f) ->
    attrs =
      id:		'settlers_board_number_' + f.id
      class:		'settlers-board-piece settlers-board-number settlers-board-number-field-' + f.id + ' settlers-board-number-' + f.number

    if (G.state == 13 or G.state == 15 or G.state == 19) and f.thief != true
      attrs.class += ' settlers-board-number-active'

    $(eid).append window.settlers.render_board_piece attrs

    if (G.state == 13 or G.state == 15 or G.state == 19) and f.thief != true
      $('#' + attrs.id).click () ->
        window.hlib.INFO.working()

        window.hlib.Ajax
          url:			'/game/settlers/number_click'
          data:
            gid:		G.gid
            nid:		f.id
          handlers:
            h200:     (response, ajax) ->
              window.settlers.update_game_state()
            h403:	(response, ajax) ->
              window.hlib.error response.error

        return false

  __add_path = (p) ->
    attrs =
      id:		'settlers_board_path_' + p.id
      class:		'settlers-board-piece settlers-board-path settlers-board-path-' + p.id + ' settlers-board-path-' + map_pathid_to_position[p.id] + ' '

    if p.owner == -1
      attrs.class += 'settlers-board-path-' + bs + '-free-' + map_pathid_to_position[p.id]

    else
      owner = G.players[p.owner]

      attrs.class += 'settlers-board-path-' + bs + '-' + owner.color.name + '-' + map_pathid_to_position[p.id]
      attrs.title = owner.user.name

    if G.current_active_paths_map[p.id] == true
      attrs.class += ' settlers-board-path-active settlers-board-path-' + bs + '-free-' + map_pathid_to_position[p.id] + '-active'

    $(eid).append window.settlers.render_board_piece attrs

    if G.current_active_paths_map[p.id] == true
      if G.state == 1
        $('#' + attrs.id).click () ->
          window.hlib.INFO.working()

          window.hlib.Ajax
            url:		'/game/settlers/path_click'
            data:
              gid:		G.gid
              pid:		p.id
            handlers:
              h200:     (response, ajax) ->
                window.settlers.update_game_state()
              h403:	(response, ajax) ->
                window.hlib.error response.error

          return false

      else if G.state == 10 or G.state == 11
        $('#' + attrs.id).click () ->
          window.hlib.INFO.working()

          if G.current_path
            G.current_path.type = 1
            G.current_path.owner = -1

          G.current_path = p

          p.type = 2
          p.owner = G.my_player.id

          G.current_active_paths_map = window.settlers.game.active_paths_map()

          window.settlers.update_game_ui()
          window.hlib.INFO._hide()

          return false

      else if G.state == 22 or G.state == 23
        $('#' + attrs.id).click () ->
          window.hlib.INFO.working()

          window.hlib.Ajax
            url:		'/game/settlers/path_click'
            data:
              gid:		G.gid
              pid:		p.id
            handlers:
              h200:     (response, ajax) ->
                window.settlers.update_game_state()
              h403:	(response, ajax) ->
                window.hlib.error response.error

          return false

  __add_node = (n) ->
    attrs =
      id:		'settlers_board_node_' + n.id
      class:		'settlers-board-piece settlers-board-node '

    if n.owner == -1
      color = 'free'
      attrs.class += 'settlers-board-node-free settlers-board-node-' + bs + '-free settlers-board-node-free-' + n.id

      if G.current_active_nodes_map[n.id] == true
        attrs.class += ' settlers-board-node-' + bs + '-free-active settlers-board-node-active'

    else
      owner = G.players[n.owner]
    
      attrs.class += 'settlers-board-node-owned settlers-board-node-owned-' + n.id + ' settlers-board-node-' + bs + '-' + map_nodetype_to_str[n.type] + '-' + owner.color.name
      attrs.title = owner.user.name

      if G.current_active_nodes_map[n.id] == true
        attrs.class += '-active settlers-board-node-active'

    s = '<span ' +  ((attr_name + '="' + attr_value + '"' for own attr_name, attr_value of attrs).join ' ') + '></span>'
    $(eid).append(s)

    if G.current_active_nodes_map[n.id] == true
      if G.state == 1
        $('#' + attrs.id).click () ->
          window.hlib.INFO.working()

          window.hlib.Ajax
            url:		'/game/settlers/node_click'
            data:
              gid:		G.gid
              nid:		n.id
            handlers:
              h200:     (response, ajax) ->
                window.settlers.update_game_state()
              h403:	(response, ajax) ->
                window.hlib.error response.error

          return false

      else if G.state == 10
        $('#settlers_board_node_' + n.id).click () ->
          window.hlib.INFO.working()

          # cleanup - remove old selected village
          G.my_player.first_village = null

          if G.current_node
            G.current_node.type = 1
            G.current_node.owner = -1

          if G.current_path
            G.current_path.type = 1
            G.current_path.owner = -1

          # set new village
          G.my_player.first_village = n
          G.current_node = n
          G.current_path = null

          # update node
          n.type = 2
          n.owner = G.my_player.id

          # update maps
          G.current_active_nodes_map = window.settlers.game.active_nodes_map()
          G.current_active_paths_map = window.settlers.game.active_paths_map()

          # render
          window.settlers.update_game_ui()
          window.hlib.INFO._hide()

          return false

      else if G.state == 11
        $('#settlers_board_node_' + n.id).click () ->
          window.hlib.INFO.working()

          # cleanup - remove old selected village
          G.my_player.second_village = null

          if G.current_node
            G.current_node.type = 1
            G.current_node.owner = -1

          if G.current_path
            G.current_path.type = 1
            G.current_path.owner = -1

          # set new village
          G.my_player.second_village = n
          G.current_node = n
          G.current_path = null

          # update node
          n.type = 2
          n.owner = G.my_player.id

          # update maps
          G.current_active_nodes_map = window.settlers.game.active_nodes_map()
          G.current_active_paths_map = window.settlers.game.active_paths_map()

          # render
          window.settlers.update_game_ui()
          window.hlib.INFO._hide()

          return false

      else
        $('#settlers_board_node_' + n.id).click () ->
          window.hlib.Ajax
            url:			'/game/settlers/node_click'
            data:
              gid:		G.gid
              nid:		n.id
            handlers:
              h200:	(response, ajax) ->
                window.settlers.update_game_state()

          return false

  __add_port = (p) ->
    classes = 'settlers-board-piece settlers-board-sea settlers-board-sea-' + (2 * p.id + 1) + ' settlers-board-port-' + map_resource_to_str[p.resource + 2] + '-' + p.clock + '-' + bs
    s = '<span id="settlers_board_port_' + p.id + '" class="' + classes + '"></span>'
    $(eid).append(s)

  __add_sea = (i) ->
    classes = 'settlers-board-piece settlers-board-sea settlers-board-sea-' + (2 * i) + ' settlers-board-sea-' + bs
    s = '<span class="' + classes + '"></span>'
    $(eid).append(s)

  __add_field f for f in G.board.fields
  __add_number f for f in G.board.fields
  __add_node n for n in G.board.nodes
  __add_port p for p in G.board.ports
  __add_sea i for i in [1..9]
  __add_path p for p in G.board.paths

window.settlers.update_game_ui_status = () ->
  G = window.settlers.game
  eid = '.settlers-game-status'

  $(eid).hide()

  show_status = true

  if G.has_all_confirmed != true
    $(eid).html window.hlib._g 'Waiting for more players'

  else if not G.my_player.is_on_turn
    $(eid).html (window.hlib._g 'Waiting for {0}').format G.forhont_player.user.name

  else if G.state == 2
    $(eid).html window.hlib._g 'Game finished'

  else if G.state == 3
    $(eid).html window.hlib._g 'Game canceled'

  else if G.state == 0
    $(eid).html window.hlib._g 'Waiting for more players'

  else if G.state == 21
    $(eid).html window.hlib._g 'Choose 2 resources for free'

  else if G.state == 22
    $(eid).html window.hlib._g 'Place your first free road'

  else if G.state == 23
    $(eid).html window.hlib._g 'Place your second free road'

  else if G.state == 10
    $(eid).html window.hlib._g 'Place your first village, first road and press "Pass turn" button'

  else if G.state == 11
    $(eid).html window.hlib._g 'Place your second village and road'

  else if G.state == 13 or G.state == 15 or G.state == 19
    $(eid).html window.hlib._g 'Select new field for thief'

  else if G.state == 12
    $(eid).html window.hlib._g 'You can use your knight card, or roll dice'

  else if G.state == 14 or G.state == 16 or G.state == 20
    $(eid).html window.hlib._g 'Select player whom you want to relieve of resource'

  else if G.state == 1
    $(eid).html window.hlib._g 'Play ;)'

  else if G.state == 17
    $(eid).html window.hlib._g 'Roll the dice'

  else if G.state == 18
    $(eid).html window.hlib._g 'Choose what resource to steal'

  else
    show_status = false

  if show_status
    $(eid).show()

window.settlers.update_game_ui_cards = () ->
  G = window.settlers.game

  $('#new_card_form').hide()

  if G.state == 1
    $('#new_card_form').show()

  c.type_name = (window.hlib._g G.card_type_to_name[c.type]) for c in G.my_player.cards

  $('#cards_list').html window.hlib.render window.settlers.templates.game.cards, G.my_player

  decorate_card = (c) ->
    $('#card_use_' + c.id).click () ->
      window.hlib.Ajax
        url:			'/game/card_click'
        data:
          gid:			G.gid
          cid:			c.id
        handlers:
          h200:			(response, ajax) ->
            window.settlers.update_game_state()
            window.settlers.show_board()
      return false

  decorate_card c for c in G.my_player.cards

window.settlers.update_game_ui_history = () ->
  rendered = window.settlers.game.render_events window.settlers.events, window.settlers.templates.game.events
  $('#history_events').html rendered

window.settlers.update_game_ui_buttons = () ->
  # reset to default
  window.hlib.disableIcon '#show_exchange'
  window.hlib.disableIcon '#pass_turn'
  window.hlib.disableIcon '#roll_dice'

  G = window.settlers.game

  if G.state == 10 or G.state == 11
    if G.current_node and G.current_path
      window.hlib.enableIcon '#pass_turn', window.settlers.pass_turn

  else
    if window.settlers.game.my_player.can_pass
      window.hlib.enableIcon '#pass_turn', window.settlers.pass_turn

  if window.settlers.game.my_player.can_roll_dice
    window.hlib.enableIcon '#roll_dice', window.settlers.roll_dice

  if G.can_exchange()
    window.hlib.enableIcon '#show_exchange', window.settlers.show_exchange

window.settlers.update_game_ui = () ->
  window.settlers.update_game_ui_info()
  window.settlers.update_game_ui_players()
  window.settlers.update_game_ui_board()
  window.settlers.update_game_ui_status()
  window.settlers.update_game_ui_cards()
  window.settlers.update_game_ui_history()
  window.settlers.update_game_ui_exchange()
  window.settlers.update_game_ui_buttons()

window.settlers.show_board = () ->
  $('#views').tabs 'select', 3
  window.location.hash = '#board'

window.settlers.show_invention = () ->
  $('#invention').show()

window.settlers.hide_invention = () ->
  $('#invention').hide()

window.settlers.show_monopoly = () ->
  $('#monopoly').show()

window.settlers.hide_monopoly = () ->
  $('#monopoly').hide()

window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:		'exchange_4'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Exchanged'
        window.settlers.update_game_state()

  new window.hlib.Form
    fid:		'exchange_3'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Exchanged'
        window.settlers.update_game_state()

  new window.hlib.Form
    fid:		'exchange_2'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Exchanged'
        window.settlers.update_game_state()

  new window.hlib.Form
    fid:		'new_card'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Bought'
        window.settlers.update_game_state()
        show_cards()

  form_invention = new window.hlib.Form
    fid:		'invention'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Received'
        window.settlers.hide_invention()
        window.settlers.update_game_state()
        window.settlers.show_board()

  $(form_invention.field_id 'gid').val window.settlers.game.gid

  form_monopoly = new window.hlib.Form
    fid:		'monopoly'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Stolen'
        window.settlers.hide_monopoly()
        window.settlers.update_game_state()
        window.settlers.show_board()

  $(form_monopoly.field_id 'gid').val window.settlers.game.gid

  $('#new_card_gid').val window.settlers.game.gid

  show_chat = () ->
    $('#views').tabs 'select', 1
    window.location.hash = '#chat'

  show_cards = () ->
    $('#views').tabs 'select', 4
    window.location.hash = '#cards'

  show_history = () ->
    $('#views').tabs 'select', 2
    window.location.hash = '#history'

  window.settlers.show_exchange = () ->
    $('#views').tabs 'select', 5
    window.location.hash = '#exchange'

  window.settlers.pass_turn = () ->
    G = window.settlers.game

    config =
      url:			''
      data:
        gid:			G.gid

      handlers:
        h200:		(response, ajax) ->
          window.settlers.update_game_state()

    if G.state == 10
      config.url = '/game/settlers/pass_turn_first'
      config.data.first_village = G.current_node.id
      config.data.first_path = G.current_path.id

    else if G.state == 11
      config.url = '/game/settlers/pass_turn_second'
      config.data.second_village = G.current_node.id
      config.data.second_path = G.current_path.id

    else
      config.url = '/game/pass_turn'

    new window.hlib.Ajax config

  window.settlers.roll_dice = () ->
    new window.hlib.Ajax
      url:			'/game/settlers/roll_dice?gid=' + window.settlers.game.gid
      handlers:
        h200:		(response, ajax) ->
          window.hlib.INFO._hide()
          window.settlers.update_game_state()

    return false

  $('#views').tabs()

  chat_pager = window.settlers.setup_chat
    id_prefix:			'chat'
    eid:                        '#chat_posts'
    url:                        '/game/chat/page'
    data:
      gid:			window.settlers.game.gid

  window.settlers.setup_chat_form
    eid:                        '#chat_post'
    handlers:
      h200:		() ->
        chat_pager.refresh()

  window.settlers.update_game_state()

  $('#refresh').click () ->
    window.settlers.update_game_state()
    return false

  $('#show_board').click () ->
    window.settlers.show_board()
    return false

  $('#show_cards').click () ->
    show_cards()
    return false

  $('#show_exchange').click () ->
    window.settlers.show_exchange()
    return false

  $('#show_history').click () ->
    show_history()
    return false

  $('#show_chat').click () ->
    show_chat()
    return false

  if window.settlers.game.state == 21
    window.settlers.show_invention()

  else if window.settlers.game.state == 18
    window.settlers.show_monopoly()

  if window.location.hash == '#chat'
    show_chat()

  else if window.location.hash == '#board'
    window.settlers.show_board()

  else if window.location.hash == '#cards'
    show_cards()

  else if window.location.hash == '#history'
    show_history()

  else if window.location.hash == '#exchange'
    window.settlers.show_exchange()

  else
    window.settlers.show_board()

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
