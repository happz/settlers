window.settlers = window.settlers or {}

window.settlers.templates = window.settlers.templates or {}
window.settlers.templates.game = {}
window.settlers.templates.game.player = doT.template '
  <div class="playable-player">
    <div class="game-player-header settlers-game-player-header-{{= it.color.name}}">
      <h4>
        {{= it.user.name}}
        <div class="pull-right">
          {{? it.has_mightest_chilvary}}
            <span class="settlers-player-title-icon settlers-icon-chilvary-on"></span>
          {{?}}
          {{? it.has_longest_path}}
            <span class="settlers-player-title-icon settlers-icon-path-on"></span>
          {{?}}
        </div>
      </h4>
    </div>

    <table class="table table-condensed">
      {{? it.my_player}}
        <tr class="info"><td colspan="2"><strong>{{= it.points}} {{= window.hlib._g("points")}}</strong></td></tr>
        <tr><td><img src="/static/images/games/settlers/board/{{= window.settlers.game.render_info.board_skin}}/icons/wood.gif" />{{= window.hlib._g("Wood")}}:</td><td>{{= it.resources.wood}}</td></tr>
        <tr><td><img src="/static/images/games/settlers/board/{{= window.settlers.game.render_info.board_skin}}/icons/clay.gif" />{{= window.hlib._g("Clay")}}:</td><td>{{= it.resources.clay}}</td></tr>
        <tr><td><img src="/static/images/games/settlers/board/{{= window.settlers.game.render_info.board_skin}}/icons/sheep.gif" />{{= window.hlib._g("Sheep")}}:</td><td>{{= it.resources.sheep}}</td></tr>
        <tr><td><img src="/static/images/games/settlers/board/{{= window.settlers.game.render_info.board_skin}}/icons/grain.gif" />{{= window.hlib._g("Grain")}}:</td><td>{{= it.resources.grain}}</td></tr>
        <tr><td><img src="/static/images/games/settlers/board/{{= window.settlers.game.render_info.board_skin}}/icons/rock.gif" />{{= window.hlib._g("Rock")}}:</td><td>{{= it.resources.rock}}</td></tr>
        <tr class="info"><td colspan="2"><strong>{{= it.resources.total}} {{= window.hlib._g("resources totally")}}</strong></td></tr>
      {{??}}
        <tr class="info"><td><strong>{{= window.hlib._g("Points")}}:</strong></td><td><strong>{{= it.points}}</strong></td></tr>
        <tr class="info"><td><strong>{{= window.hlib._g("Resources")}}:</td><td><strong>{{= it.resources.total}}</td></tr>
      {{?}}

      {{? it.my_player}}
        <tr rel="tooltip" data-placement="right" title="{{= it.cards.unused_cards_str}}"><td>{{= window.hlib._g("Cards")}}:</td><td>{{= it.cards.unused_cards}}</td></tr>
      {{??}}
        <tr><td>{{= window.hlib._g("Cards")}}:</td><td>{{= it.cards.unused_cards}}</td></tr>
      {{?}}
      <tr><td>{{= window.hlib._g("Knights")}}:</td><td>{{= it.cards.used_knights}}</td></tr>
    </table>
  </div>
'
window.settlers.templates.game.cards = doT.template '
  <table class="table">
    {{~ it.cards :card:index}}
      <tr>
        <td>
          <div id="card_{{= card.id}}" class="mediumListIconTextItem">
            {{? card.used}}
              <div class="icon-document mediumListIconTextItem-Image card-used" />
            {{??}}
              <div class="icon-document mediumListIconTextItem-Image card-unused" />
            {{?}}
            <div class="mediumListIconTextItem-Detail">
              <h4>{{= window.hlib._g(window.settlers.game.card_type_to_name[card.type])}}</h4>
              {{? card.used}}
                <p>{{= window.hlib._g("Used in round")}} #{{= card.used}}.</p>
              {{?}}
            </div>
          </div>
        </td>
      </tr>
    {{~}}
  </table>
'
window.settlers.templates.game.events = doT.template '
  {{ prev_round = null; }}
  {{~ it.events :event:index}}
    {{ if (prev_round == null) { prev_round = event.round; }; }}
    {{? prev_round != event.round}}
      <tr><td colspan="4"><hr /></td></tr>
      {{ prev_round = event.round; }}
    {{?}}
    {{? !event.hidden}}
      <tr>
        {{
          var color_by = null;
          if (event.user) {
            color_by = event.user;
          } else if (event.thief) {
            color_by = event.thief;
          } else if (event.prev) {
            color_by = event.prev;
          }
        }}
        {{? color_by}}
          <td class="event-player-color settlers-game-player-header-{{= window.settlers.game.username_to_color[color_by.name].name}}">&nbsp;</td>
        {{??}}
          <td class="event-player-color">&nbsp;</td>
        {{?}}
        <td class="event-stamp">{{= new Date(event.stamp * 1000).strftime("%d/%m %H:%M")}}</td>
        <td class="event-round">{{= event.round}}.</td>
        <td class="event-message">{{= window.settlers.events[event.ename](event)}}</td>
      </tr>
    {{?}}
  {{~}}
'
window.settlers.templates.game.exchange = window.settlers.templates.game.exchange or {}
window.settlers.templates.game.exchange.amount = doT.template '
  <option value="" selected="selected">{{= window.hlib._g("# pieces of ...")}}</option>
  {{~ it.amounts :amount:index}}
    <option value="{{= amount.amount}}">{{= amount.amount}}</option>
  {{~}}
'
window.settlers.templates.game.exchange.resources = doT.template '
  <option value="" selected="selected">{{= window.hlib._g(it.hint)}}</option>
  {{~ it.resources :resource:index}}
    <option value="{{= resource.resource}}">{{= resource.resource_label}}</option>
  {{~}}
'

window.settlers.format_event_resources = (rs) ->
  return (window.hlib._g '{0} wood, {1} clay, {2} sheep, {3} grain, {4} rock').format rs.wood, rs.clay, rs.sheep, rs.grain, rs.rock

window.settlers.events['game.CardUsed']					= (e) ->
  return (window.hlib._g '{0} used card {1} from round {2}').format e.user.name, (window.hlib._g window.settlers.game.card_type_to_name[e.card.type]), e.card.bought

window.settlers.events = window.settlers.events or {}
window.settlers.events['game.settlers.LongestPathBonusEarned']		= (e) ->
  return (window.hlib._g '{0} earned bonus for longest path').format e.user.name

window.settlers.events['game.settlers.MightestChilvaryBonusEarned']	= (e) ->
  return (window.hlib._g '{0} earned bonus for mightest chilvary').format e.user.name

window.settlers.events['game.settlers.ResourceStolen']			= (e) ->
  if e.am_i_thief == true
    return (window.hlib._g 'You stole 1 piece of {0} from {1}').format (window.hlib._g window.settlers.game.resource_id_to_name[e.resource]), e.victim.name

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
  return (window.hlib._g '{0} rolled a dice').format e.user.name

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
    $.extend true, @, data

    @my_player = @players[@my_player]
    @forhont_player = @players[@forhont_player]

    @username_to_color = {}

    G = @

    __per_player = (p) ->
      if p.first_village
        p.first_village = G.board.nodes[p.first_village - 1]

      if p.second_village
        p.second_village = G.board.nodes[p.second_village - 1]

      G.username_to_color[p.user.name] = p.color

    __per_player p for p in @players

    @current_node = null
    @current_path = null

    @current_active_nodes_map = null
    @current_active_paths_map = null

    @events.reverse()

  has_enough_resources:		(what) ->
    if what == 'card'
      return (@my_player.resources.rock >= 1 and @my_player.resources.grain >= 1 and @my_player.resources.sheep >= 1)

    if what == 'village'
      return (@my_player.resources.wood >= 1 and @my_player.resources.clay >= 1 and @my_player.resources.grain >= 1 and @my_player.resources.sheep >= 1)

    if what == 'town'
      return (@my_player.resources.grain >= 2 and @my_player.resources.rock >= 3)

    if what == 'path'
      return (@my_player.resources.wood >= 1 and @my_player.resources.clay >= 1)

    return true

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

      if not @has_enough_resources('village') and not @has_enough_resources('town')
        return jQuery.extend {}, window.settlers.board_defs.active_nodes_map_negative

      m = jQuery.extend {}, window.settlers.board_defs.active_nodes_map_positive

      __per_node = (node) ->
        if m[node.id] == false
          return

        if node.type == 1
          # empty node, do we have resources for village?
          if not G.has_enough_resources('village')
            m[node.id] = false
            return

          # can we build another village?
          if not P.has_free_village
            m[node.id] = false
            return

        else
          # node is not empty, disable all adjacent nodes
          m[neighbour_id] = false for neighbour_id in window.settlers.board_defs.nodes[node.id].neighbours

          # owner is not current player
          if node.owner != P.id
            m[node.id] = false
            return

          # node is town
          if node.type == 3
            m[node.id] = false
            return

          # OK, it's a village, we own it, but do we have enough resources?
          if not G.has_enough_resources('town')
            m[node.id] = false
            return

          # can we build another town?
          if not P.has_free_town
            m[node.id] = false
            return

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

        if G.state == 1 and not G.has_enough_resources('path')
          m[path.id] = false
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

window.settlers.refresh_game_state = (response) ->
  window.settlers.game = new window.settlers.GameObject response.game
  window.settlers.update_game_ui()
  window.hlib.MESSAGE.hide()

window.settlers.update_game_state = (after_update) ->
  gid = window.settlers.game.gid

  req = new window.hlib.Ajax
    url:		'/game/state'
    data:
      gid:		gid
    handlers:
      h200:		(response, ajax) ->
        window.settlers.refresh_game_state response

        if after_update
          after_update(window.settlers.game)

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
    hint:		'To ...'
    resources:		[
      __mk_resource_option 1
      __mk_resource_option 4
      __mk_resource_option 0
      __mk_resource_option 3
      __mk_resource_option 2
    ]

  src_resources =
    hint:		'From ...'
    resources:		[
    ]

  if i == 4
    if my_player.resources.wood >= i
      src_resources.resources.push __mk_resource_option 1
    if my_player.resources.clay >= i
      src_resources.resources.push __mk_resource_option 4
    if my_player.resources.sheep >= i
      src_resources.resources.push __mk_resource_option 0
    if my_player.resources.grain >= i
      src_resources.resources.push __mk_resource_option 3
    if my_player.resources.rock >= i
      src_resources.resources.push __mk_resource_option 2

  else if i == 3 and G.can_exchange_three() == true
    if my_player.resources.wood >= i
      src_resources.resources.push __mk_resource_option 1
    if my_player.resources.clay >= i
      src_resources.resources.push __mk_resource_option 4
    if my_player.resources.sheep >= i
      src_resources.resources.push __mk_resource_option 0
    if my_player.resources.grain >= i
      src_resources.resources.push __mk_resource_option 3
    if my_player.resources.rock >= i
      src_resources.resources.push __mk_resource_option 2

  else if i == 2
    if G.my_player.resources.wood >= 2 and (G.get_used_ports G.my_player, 1).length > 0
      src_resources.resources.push __mk_resource_option 1
    if G.my_player.resources.clay >= 2 and (G.get_used_ports G.my_player, 4).length > 0
      src_resources.resources.push __mk_resource_option 4
    if G.my_player.resources.sheep >= 2 and (G.get_used_ports G.my_player, 0).length > 0
      src_resources.resources.push __mk_resource_option 0
    if G.my_player.resources.grain >= 2 and (G.get_used_ports G.my_player, 3).length > 0
      src_resources.resources.push __mk_resource_option 3
    if G.my_player.resources.rock >= 2 and (G.get_used_ports G.my_player, 2).length > 0
      src_resources.resources.push __mk_resource_option 2

  $(eid_prefix + '_gid').val G.gid
  $(eid_prefix + '_ratio').val i
  $(eid_prefix + '_amount').html window.settlers.templates.game.exchange.amount amounts
  $(eid_prefix + '_src').html window.settlers.templates.game.exchange.resources src_resources
  $(eid_prefix + '_dst').html window.settlers.templates.game.exchange.resources dst_resources

  $(eid_prefix).show()

window.settlers.update_game_ui_exchange = () ->
  window.settlers.__refresh_game_ui_exchange i for i in [2, 3, 4]

  if window.settlers.game.can_exchange() == true
    $('#exchange_no').hide()
  else
    $('#exchange_no').show()

window.settlers.update_game_ui_info = () ->
  $('#last_numbers').hide()
  $('#game_status').hide()

  G = window.settlers.game

  $('#game_id').html G.gid
  $('#game_name').html G.name
  $('#game_round').html G.round

  if G.last_numbers.length > 0
    s = G.last_numbers.slice()
    s[0] = '<span class="badge badge-success">' + s[0] + '</span>'
    $('#last_numbers p').html s.join ' '
    $('#last_numbers').show()

window.settlers.update_game_ui_player = (player) ->
  dst_id = '#game-player-' + player.id + '-placeholder'

  player.game = window.settlers.game

  if player.my_player
    unused_cards_desc =
      Knight:			0
      Monopoly:			0
      Paths:			0
      Invention:		0
      Point:			0

    __per_card = (c) ->
      if c.used != false
        return

      k = window.settlers.game.card_type_to_name[c.type]

      unused_cards_desc[k] = unused_cards_desc[k] + 1

    __per_card c for c in player.cards.cards

    unused_cards_arr = []
    __per_type = (t) ->
      if not unused_cards_desc.hasOwnProperty t
        return
      if unused_cards_desc[t] <= 0
        return

      unused_cards_arr.push ('' + unused_cards_desc[t] + 'x ' + window.hlib._g t)

    __per_type t for t in window.settlers.game.card_type_to_name

    player.cards.unused_cards_str = unused_cards_arr.join '<br />'

  $(dst_id).html window.settlers.templates.game.player player

window.settlers.update_game_ui_players = () ->
  window.settlers.update_game_ui_player p for p in window.settlers.game.players

  if window.hlib.mobile == false
    $('tr[rel=tooltip]').tooltip
      html:			true

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
        id:		'settlers_board_thief'
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
        window.hlib.WORKING.show()

        new window.hlib.Ajax
          url:			'/game/settlers/number_click'
          data:
            gid:		G.gid
            nid:		f.id
          handlers:
            h200:     (response, ajax) ->
              window.settlers.refresh_game_state response

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
          window.hlib.WORKING.show()

          new window.hlib.Ajax
            url:		'/game/settlers/path_click'
            data:
              gid:		G.gid
              pid:		p.id
            handlers:
              h200:     (response, ajax) ->
                window.settlers.refresh_game_state response

          return false

      else if G.state == 10 or G.state == 11
        $('#' + attrs.id).click () ->
          window.hlib.WORKING.show()

          if G.current_path
            G.current_path.type = 1
            G.current_path.owner = -1

          G.current_path = p

          p.type = 2
          p.owner = G.my_player.id

          G.current_active_paths_map = window.settlers.game.active_paths_map()

          window.settlers.update_game_ui()
          window.hlib.MESSAGE.hide()

          return false

      else if G.state == 22 or G.state == 23
        $('#' + attrs.id).click () ->
          window.hlib.WORKING.show()

          new window.hlib.Ajax
            url:		'/game/settlers/path_click'
            data:
              gid:		G.gid
              pid:		p.id
            handlers:
              h200:     (response, ajax) ->
                window.settlers.refresh_game_state response

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
          window.hlib.WORKING.show()

          new window.hlib.Ajax
            url:		'/game/settlers/node_click'
            data:
              gid:		G.gid
              nid:		n.id
            handlers:
              h200:     (response, ajax) ->
                window.settlers.refresh_game_state response

          return false

      else if G.state == 10
        $('#settlers_board_node_' + n.id).click () ->
          window.hlib.WORKING.show()

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
          window.hlib.MESSAGE.hide()

          return false

      else if G.state == 11
        $('#settlers_board_node_' + n.id).click () ->
          window.hlib.WORKING.show()

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
          window.hlib.MESSAGE.hide()

          return false

      else
        $('#settlers_board_node_' + n.id).click () ->
          new window.hlib.Ajax
            url:			'/game/settlers/node_click'
            data:
              gid:		G.gid
              nid:		n.id
            handlers:
              h200:	(response, ajax) ->
                window.settlers.refresh_game_state response

          return false

  __add_port = (p) ->
    classes = 'settlers-board-piece settlers-board-sea settlers-board-sea-' + (2 * p.id + 1) + ' settlers-board-port-' + map_resource_to_str[p.resource + 2] + '-' + p.clock + '-' + bs
    s = '<span id="settlers_board_port_' + p.id + '" class="' + classes + '"></span>'
    $(eid).append(s)

  __add_sea = (i) ->
    classes = 'settlers-board-piece settlers-board-sea settlers-board-sea-' + (2 * i) + ' settlers-board-sea-' + bs
    s = '<span id="settlers_board_sea_' + i + '" class="' + classes + '"></span>'
    $(eid).append(s)

  __add_field f for f in G.board.fields
  __add_number f for f in G.board.fields
  __add_node n for n in G.board.nodes
  __add_port p for p in G.board.ports
  __add_sea i for i in [1..9]
  __add_path p for p in G.board.paths

window.settlers.update_game_ui_status = () ->
  G = window.settlers.game
  eid = '#game_status'

  $(eid).hide()

  show_status = true

  if G.state == 2
    $(eid).html (window.hlib._g 'Game finished, winner is {0}').format G.forhont_player.user.name

  else if G.has_all_confirmed != true
    $(eid).html window.hlib._g 'Waiting for more players'

  else if not G.my_player.is_on_turn
    $(eid).html (window.hlib._g 'Waiting for {0}').format G.forhont_player.user.name

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
    $(eid).html window.hlib._g 'Roll dice'

  else if G.state == 18
    $(eid).html window.hlib._g 'Choose what resource to steal'

  else
    show_status = false

  if show_status
    $(eid).show()

window.settlers.update_game_ui_cards = () ->
  G = window.settlers.game

  window.settlers.hide_menu_alert 'show_cards', 'badge-info'
  $('#new_card_form').hide()

  if G.state == 1 and G.my_player.resources.rock >= 1 and G.my_player.resources.grain >= 1 and G.my_player.resources.sheep >= 1
    $('#new_card_form').show()

  $('#cards_list').html window.settlers.templates.game.cards G.my_player.cards

  decorate_card = (c) ->
    if not c.can_be_used
      return

    $('#card_' + c.id).click () ->
      new window.hlib.Ajax
        url:			'/game/card_click'
        data:
          gid:			G.gid
          cid:			c.id
        handlers:
          h200:			(response, ajax) ->
            window.settlers.refresh_game_state response
            window.settlers.show_board()
      return false

  decorate_card c for c in G.my_player.cards.cards

  if G.my_player.cards.unused_cards > 0
    window.settlers.show_menu_alert 'show_cards', G.my_player.cards.unused_cards, 'badge-info', (window.hlib.format_string (window.hlib._g '%(count)s unused cards'), {count: G.my_player.cards.unused_cards})

  $('#apply_points').hide()
  if G.state == 12 or G.state == 1
    cnt = 0
    (cnt += 1 if c.type == 5 and c.used == false) for c in G.my_player.cards.cards
    if cnt + G.my_player.points >= 10
      $('#apply_points_gid').val G.gid
      $('#apply_points').show()

window.settlers.update_game_ui_history = () ->
  $('#history_events').html window.settlers.templates.game.events window.settlers.game

window.settlers.update_game_ui_buttons = () ->
  # reset to default
  window.hlib.disableIcon '#show_exchange'
  window.hlib.disableIcon '#pass_turn'
  window.hlib.disableIcon '#roll_dice'
  window.hlib.disableIcon '#show_stats'
  window.hlib.disableIcon '#buy_card'

  G = window.settlers.game

  if G.state == 1 and G.has_enough_resources('card')
    window.hlib.enableIcon '#buy_card', window.settlers.buy_card

  if G.state == 10 or G.state == 11
    if G.current_node and G.current_path
      window.hlib.enableIcon '#pass_turn', window.settlers.pass_turn

  else
    if window.settlers.game.my_player.can_pass
      window.hlib.enableIcon '#pass_turn', window.settlers.pass_turn

  if window.settlers.game.my_player.can_roll_dice
    window.hlib.enableIcon '#roll_dice', window.settlers.roll_dice

  if G.state == 2
    window.hlib.enableIcon '#show_stats', window.settlers.show_stats

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

  if window.settlers.game.state == 21
    window.settlers.show_invention()

  else if window.settlers.game.state == 18
    window.settlers.show_monopoly()

  else
    window.settlers.show_game_board()

window.settlers.buy_card = () ->
  $('#new_card_form').submit()

window.settlers.show_stats = () ->
  G = window.settlers.game

  serie_with =
    color:			'#4E9258'
    data:			G.dice_rolls.with
    label:			window.hlib._g 'With first 3 rounds'
    points:
      show:			true

  serie_without =
    color:			'#5E767E'
    data:			G.dice_rolls.without
    label:			window.hlib._g 'Without first 3 rounds'
    points:
      show:			true

  options =
    xaxis:
      min:			2
      max:			12
      ticks:			11
      tickDecimals:		0
    yaxis:
      min:			0
      tickDecimals:		0
    grid:
      hoverable:		true

  $.plot $('#stats_dice_rolls'), [serie_with, serie_without], options

  __show_tooltip = (x, y, dice_value, rolled) ->
    dice_value = parseInt dice_value
    rolled = parseInt rolled

    G = window.settlers.game

    if G.dice_rolls.with[dice_value - 2][1] == G.dice_rolls.without[dice_value - 2][1]
      contents = (window.hlib._g '{0} was rolled {1} times').format dice_value, rolled
      bgcolor = '#bfbfbf'

    else if G.dice_rolls.with[dice_value - 2][1] == rolled
      contents = (window.hlib._g 'With first 3 rounds') + ': ' + ((window.hlib._g '{0} was rolled {1} times').format dice_value, rolled)
      bgcolor = '#4E9258'

    else if G.dice_rolls.without[dice_value - 2][1] == rolled
      contents = (window.hlib._g 'Without first 3 rounds') + ': ' + ((window.hlib._g '{0} was rolled {1} times').format dice_value, rolled)
      bgcolor = '#5E767E'

    else
      contents = 'Missing values?'

    $('<div id="stats_dice_roll_tooltip" class="tooltip">' + contents + '</div>').css({
      position:			'absolute'
      display:			'none'
      top:			y + 5
      left:			x + 5
      'background-color':	bgcolor
      opacity:			1
    }).appendTo('body').fadeIn(200)

  previousPoint = null

  $('#stats_dice_rolls').unbind 'plothover'
  $('#stats_dice_rolls').bind 'plothover', (event, pos, item) ->
    if item
      if previousPoint != item.dataIndex
        previousPoint = item.dataIndex

        x = item.datapoint[0].toFixed(0)
        y = item.datapoint[1].toFixed(0)

        $('#stats_dice_roll_tooltip').remove()
        __show_tooltip item.pageX, item.pageY, x, y

    else
      $('#stats_dice_roll_tooltip').remove()
      previousPoint = null

  $('#views').tabs 'select', 6
  window.location.hash = '#stats'

window.settlers.show_board = () ->
  $('#views').tabs 'select', 3
  window.location.hash = '#board'

window.settlers.hide_board_view_sections = () ->
  $('#invention').hide()
  $('#monopoly').hide()
  $('.game-board').hide()

window.settlers.show_invention = () ->
  window.settlers.hide_board_view_sections()
  $('#invention').show()

window.settlers.show_monopoly = () ->
  window.settlers.hide_board_view_sections()
  $('#monopoly').show()

window.settlers.show_game_board = () ->
  window.settlers.hide_board_view_sections()
  $('.game-board').show()

$(window).bind 'page_startup', () ->
  exchange_form = (ratio) ->
    f = new window.hlib.Form
      fid:		'exchange_' + ratio
      handlers:
        s200:		(response, form) ->
          form.info.success 'Exchanged'
          window.settlers.refresh_game_state response

    $('#exchange_' + ratio + '_submit_board').click () ->
      f.submit()
      window.settlers.show_board()
      return false

  exchange_form '4'
  exchange_form '3'
  exchange_form '2'

  new window.hlib.Form
    fid:		'new_card'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Bought'
        window.settlers.refresh_game_state response
        show_cards()

  new window.hlib.Form
    fid:		'apply_points'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Applied'
        window.settlers.update_game_state()
        show_cards()

  form_invention = new window.hlib.Form
    fid:		'invention'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Received'
        window.settlers.refresh_game_state response
        window.settlers.show_board()

  $(form_invention.field_id 'gid').val window.settlers.game.gid

  form_monopoly = new window.hlib.Form
    fid:		'monopoly'
    handlers:
      s200:		(response, form) ->
        form.info.success 'Stolen'
        window.settlers.refresh_game_state response
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
          window.settlers.refresh_game_state response

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
          window.hlib.MESSAGE.hide()
          window.settlers.refresh_game_state response

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

  window.settlers.update_game_state (G) ->
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

    else if window.location.hash == '#stats' and G and G.state == 2
      window.settlers.show_stats()

    else
      window.settlers.show_board()

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

  $('#show_stats').click () ->
    window.hlib.show_stats()
    return false

window.settlers.templates.chat_post = doT.template '
 <tr id="chat_post_{{= it.id}}">
    <td>
      <h3>
        <span class="chat-post-unread label label-important hide">{{= window.hlib._g("Unread")}}</span>
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
