<%!
  import time
  import games
  import games.settlers

  import hlib
  import hlib.event
  import hlib.events
  import hlib.events.system
  import events.system
  import events.game
  import events.game.settlers

  import hruntime
%>

<%def name="event_game_settlers_resources(rc)">${_('%(wood)i wood, %(clay)i clay, %(sheep)i sheep, %(grain)i grain, %(rock)i rock', wood = rc.wood, clay = rc.clay, sheep = rc.sheep, grain = rc.grain, rock = rc.rock)}</%def>

<%def name="event_message(e)">
  % if  e.type == hlib.events.system.SystemEvent.USER_LOGGED_IN:
    ${_('User %(user)s logged in', user = e.user.name)}

  % elif e.type == hlib.events.system.SystemEvent.USER_LOGGED_OUT:
    ${_('User %(user)s logged out', user = e.user.name)}

  % elif e.type == events.system.SystemEvent.CHAT_POST:
    ${_('Player %(player)s post new message on chat', player = e.user.name)}

  % elif e.type == events.game.GameEvent.CREATED:
    ${_('Game has been created')}

  % elif e.type == events.game.GameEvent.CANCELED:
    % if   e.reason == events.game.GameCanceled.REASON_MASSIVE:
      ${_('Game has been canceled due to massive timeouts')}

    % elif e.reason == events.game.GameCanceled.REASON_ABSENTEE:
      ${_('Game has been canceled due to missing player %(player)s', player = e.user.name)}

    % elif e.reason == events.game.GameCanceled.REASON_EMPTY:
      ${_('Game has been canceled due to lack of interest')}
    % endif

  % elif e.type == events.game.GameEvent.FINISHED:
    ${_('Game has been finished')}

  % elif e.type == events.game.GameEvent.STARTED:
    ${_('Game has started')}

  % elif e.type == events.game.GameEvent.PLAYER_JOINED:
    ${_('Player %(player)s joined game', player = e.user.name)}

  % elif e.type == events.game.GameEvent.CHAT_POST:
    ${_('Player %(player)s post new message on chat', player =e.user.name)} 

  % elif e.type == events.game.GameEvent.PLAYER_MISSED:
    ${_('Player %(player)s missed his turn', player = e.user.name)}

  % elif e.type == events.game.GameEvent.PASS:
    ${_('Player %(prev)s passed turn, next player is %(next)s', prev = e.prev.name, next = e.next.name)}

  % elif e.type == events.game.settlers.SettlersEvent.CARD_USED:
    ${_('Player %(player)s used card %(card)s from round %(round)s', player = e.user.name, card = _(games.settlers.Card.map_card2str[e.card.type].capitalize()), round = e.card.bought)}

  % elif e.type == events.game.settlers.SettlersEvent.CARD_BOUGHT:
    ${_('Player %(player)s bought new card', player = e.user.name)}

  % elif e.type == events.game.settlers.SettlersEvent.LONGEST_PATH_BONUS_EARNED:
    ${_('Player %(player)s earned longest path bonus', player = e.user.name)}

  % elif e.type == events.game.settlers.SettlersEvent.MIGHTEST_CHILVARY_BONUS_EARNED:
    ${_('Player %(player)s earned mightest chilvary bonus', player = e.user.name)}

  % elif e.type == events.game.settlers.SettlersEvent.RESOURCE_STOLEN:
    % if e.am_i_thief():
      ${_('You stole 1 piece of %(resource)s from player %(victim)s', resource = _(games.settlers.Resource.map_resource2str[e.resource].capitalize()), victim = e.victim.name)}
    % else:
      % if e.am_i_victim():
        ${_('Player %(thief)s stole 1 piece of %(resource)s from you', thief = e.thief.name, resource = _(games.settlers.Resource.map_resource2str[e.resource].capitalize()))}
      % else:
        ${_('Player %(thief)s stole 1 piece of resources from player %(victim)s', thief = e.thief.name, victim = e.victim.name)}
      % endif
    % endif

  % elif e.type == events.game.settlers.SettlersEvent.RESOURCES_STOLEN:
    % if e.am_i_thief() != True:
      % if e.am_i_victim():
        ${_('Thief stole you resources')}: ${event_game_settlers_resources(e.resources)}
      % else:
        ${_('Thief stole player %(victim)s %(resources)s resources', victim = e.victim.name, resources = len(e.resources))}
      % endif
    % endif

  % elif e.type == events.game.settlers.SettlersEvent.DICE_ROLLED:
     ${_('Player %(player)s got %(dice)s on dice', player = e.user.name, dice = e.dice)}

  % elif e.type == events.game.settlers.SettlersEvent.VILLAGE_BUILT:
    ${_('Player %(player)s built new village on node %(node)s', player = e.user.name, node = e.node)}

  % elif e.type == events.game.settlers.SettlersEvent.TOWN_BUILT:
    ${_('Player %(player)s built new town on node %(node)s', player = e.user.name, node = e.node)}

  % elif e.type == events.game.settlers.SettlersEvent.PATH_BUILT:
    ${_('Player %(player)s built new path on join %(join)s', player = e.user.name, join = e.id)}

  % elif e.type == events.game.settlers.SettlersEvent.RESOURCES_RECEIVED:
    ${_('Player %(player)s received these resources', player = e.user.name)}: ${event_game_settlers_resources(e.resources)}

  % elif e.type == events.game.settlers.SettlersEvent.RESOURCES_EXCHANGED:
    ${_('Player %(player)s exchanged resources', player = e.user.name)}: ${event_game_settlers_resources(e.src)} -&gt; ${event_game_settlers_resources(e.dst)}

  % elif e.type == events.game.settlers.SettlersEvent.MONOPOLY:
    ${_('Player %(thief)s stole resources from player %(victim)s', thief = e.thief.name, victim = e.victim.name)}: ${event_game_settlers_resources(e.resources)}

  % elif e.type == events.game.settlers.SettlersEvent.THIEF_PLACED:
    ${_('Player %(player)s moved thief', player = e.user.name)}

  % elif e.type == events.game.settlers.SettlersEvent.NEW_DICE_LINE:
    ${_('New dice line created')}

  % else:
    ${_('Unknown event:')} ${e.type}

  % endif
</%def>

<%def name="event_viewer(gid, hidden)">
  <div style="height: 798px; overflow: auto">
    <table class="list" id="event_list">
      <thead>
        <tr>
          <th>${_('Time')}</th>
          % if gid != 0:
            <th>${_('Round')}</th>
          % endif
          <th>${_('Event')}</th>
        </tr>
      </thead>
      <tbody>
        % for event in hlib.event.history(gid, hidden=hidden):
          <tr>
            <td class="history_stamp">${time.strftime(user.date_format, time.localtime(event.stamp))}</td>
            % if gid != 0:
              <td>${event.round}</td>
            % endif
            <td style="text-align: left">${event_message(event)}</td>
          </tr>
        % endfor
      </tbody>
    </table>
  </div>
</%def>

<%def name="game_history_viewer(game)">
  ${event_viewer(game.id, False)}
</%def>

<%def name="system_history_viewer()">
  ${event_viewer(0, False)}
</%def>
