<%!
  import hlib
%>

<%namespace file="../hlib_ui.mako" import="*" />
<%namespace file="../lib.mako"           import="*" />

<%inherit file="../page.mako" />

<%def name="page_title()">
  ${' '.join([_('Settlers'), '-', _('Game'), str(game.id) + ':']) + ', '.join([p.user.name for p in game.players.values()])}
</%def>

<%def name="page_header()">
  ${parent.page_header()}

  <!--[if lte IE 8]><script language="javascript" type="text/javascript" src="/static/script/flot/excanvas.min.js"></script><![endif]-->
  <script language="javascript" type="text/javascript" src="/static/script/flot/jquery.flot.js"></script>

  <script type="text/javascript">
    $(window).bind('hlib_prestartup', function () {
      window.settlers = window.settlers || {};
      window.settlers.game = {
        gid:	${game.id},
        state:	${game.type}
      };
    });
  </script>
</%def>

</div>
<div class="container">

<div class="row" style="overflow: visible">
  <div class="span2 players-column">
    <div id="game-player-0-placeholder"></div>
    <hr />
    <div id="game-player-1-placeholder"></div>
    <hr />
    <div id="game-player-2-placeholder"></div>
    <hr />
    <div id="game-player-3-placeholder"></div>
  </div>

  <div class="span8 board-column">
    <div id="views">

    <ul class="hide">
      <li><a href="#empty">Empty</a></li>
      <li><a href="#chat">Chat</a></li>
      <li><a href="#history">History</a></li>
      <li><a href="#board">Board</a></li>
      <li><a href="#cards">Cards</a></li>
      <li><a href="#exchange">Exchange</a></li>
      <li><a href="#stats">Stats</a></li>
    </ul>

    <div id="empty" class="hide" ></div>

    <div id="chat" class="hide">
      <div class="settlers-view-list">
        <div class="span6">
          ${ui_form_start(action = '/game/chat/add?gid=' + str(game.id), legend = 'New message', id = 'chat_post')}
            ${ui_textarea(form_name = 'text', size = 'xlarge')}

            <div class="control-group">
              <div class="hide chat-preview well" id="preview"></div>
            </div>

            <div class="control-group">
              <div class="controls">
                <input class="btn" type="submit" value="${_('Add')}">
                <input class="btn btn-info btn-preview" type="button" value="${_('Preview')}">
                <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" rel="tooltip" data-placement="right" title="${_('Syntax help')}" target="_new"><i class="icon-help-4"></i></a>
              </div>
            </div>
          ${ui_form_end()}
        </div>

        ${chat_table()}
      </div>
    </div>

    <div id="history" class="hide">
      <div class="settlers-view-list">
        <table class="table table-hover">
          <thead>
            <tr>
              <th></th>
              <th>${_('Time')}</th>
              <th>${_('Round')}</th>
              <th>${_('Event')}</th>
            </tr>
          </thead>
          <tbody id="history_events">
          </tbody>
        </table>
      </div>
    </div>

    <div id="board" class="hide board-view">
      <div id="invention" class="hide">
        ${ui_form_start(action = '/game/settlers/invention', legend = 'Invention', id = 'invention')}
          ${ui_input(form_name = 'gid', type = 'hidden')}
          ${ui_select_start(form_name = 'resource1', label = 'First resource')}
            <option value="1">${_('Wood')}</option>
            <option value="4">${_('Clay')}</option>
            <option value="0">${_('Sheep')}</option>
            <option value="3">${_('Grain')}</option>
            <option value="2">${_('Rock')}</option>
          ${ui_select_end()}
          ${ui_select_start(form_name = 'resource2', label = 'Second resource')}
            <option value="1">${_('Wood')}</option>
            <option value="4">${_('Clay')}</option>
            <option value="0">${_('Sheep')}</option>
            <option value="3">${_('Grain')}</option>
            <option value="2">${_('Rock')}</option>
          ${ui_select_end()}
          ${ui_submit(value = 'Add')}
        ${ui_form_end()}
      </div>

      <div id="monopoly" class="hide">
        ${ui_form_start(action = '/game/settlers/monopoly', legend = 'Monopoly', id = 'monopoly')}
          ${ui_input(form_name = 'gid', type = 'hidden')}
          ${ui_select_start(form_name = 'resource', label = 'Resource')}
            <option value="1">${_('Wood')}</option>
            <option value="4">${_('Clay')}</option>
            <option value="0">${_('Sheep')}</option>
            <option value="3">${_('Grain')}</option>
            <option value="2">${_('Rock')}</option>
          ${ui_select_end()}
          ${ui_submit(value = 'Steal')}
        ${ui_form_end()}
      </div>

      <div class="game-board">
      </div>
    </div>

    <div id="cards" class="hide">
      ${ui_form_start(action = '/game/buy_card', legend = 'Buy new action card', id = 'new_card')}
        ${ui_input(form_name = 'gid', type = 'hidden')}
        ${ui_submit(value = 'Buy')}
      ${ui_form_end()}

      <div id="apply_points" class="hide">
        ${ui_form_start(action = '/game/settlers/apply_points', legend = 'Apply Point cards to win', id = 'apply_points')}
          ${ui_input(form_name = 'gid', type = 'hidden')}
          ${ui_submit(value = 'Apply')}
        ${ui_form_end()}
      </div>

      <div id="cards_list" class="settlers-view-list"></div>
    </div>

    <div id="exchange" class="hide">
      <div id="exchange_no"></div>

      <%def name="exchange_form(ratio)">
        <div id="exchange_${ratio}" class="hide">
          ${ui_form_start(action = '/game/settlers/exchange', legend = 'Exchange ' + str(ratio) + ':1', id = 'exchange_' + str(ratio), horizontal = False)}
            ${ui_input(form_name = 'gid', type = 'hidden')}
            ${ui_input(form_name = 'ratio', type = 'hidden')}

            ${ui_select_start(form_name = 'amount', default = False, minimal_struct = True, size = 'medium')}
            ${ui_select_end()}

            ${ui_select_start(form_name = 'src', default = False, minimal_struct = True, size = 'medium')}
            ${ui_select_end()}

            ${ui_select_start(form_name = 'dst', default = False, minimal_struct = True, size = 'medium')}
            ${ui_select_end()}

            <div class="control-group">
              <div class="controls">
                <input type="submit" value="${_('Exchange and return to board')}" id="exchange_${ratio}_submit_board" />
                <input type="submit" value="${_('Exchange')}" />
              </div>
            </div>
          ${ui_form_end()}
        </div>
      </%def>

      ${exchange_form(2)}
      ${exchange_form(3)}
      ${exchange_form(4)}
    </div>

    <div id="stats" class="hide">
      <div id="stats_dice_rolls" style="width: 510px; height: 200px; margin-left: auto; margin-right: auto;"></div>
      <p style="text-align: center">${_('Dice rolls')}</p>
    </div>

    </div>
  </div>

  <div class="span2 menu-column">
    <div>
      <header><h3>Hra #<span id="game_id"></span></h3></header>

      <div id="game_name"></div>
      <div><span id="game_round"></span>. kolo</div>
    </div>

    <hr />

    <div id="last_numbers">
      <header><h4>${_('Last numbers')}</h4></header>

      <div><p></p></div>
    </div>

    <hr />

    <div id="game_status" class="hide text-success"><p></p></div>

    <%def name="menu_entry(id, icon, label, content = None)">
      <%
        content = content or ''
      %>

      <button class="win-command" title="${_(label)}" rel="tooltip" data-placement="left" id="${id}" style="position: relative">
        <span class="win-commandimage win-commandring">${icon}</span>
        ${content}
      </button>
    </%def>

    <hr />

    <div class="win-commandlayout" style="text-align: center">
      ${menu_entry('show_board',    '&#xe1a5;', 'Show board')}
      ${menu_entry('show_chat',     '&#x005a;', 'Show chat')}
      ${menu_entry('roll_dice',     '&#xe017;', 'Roll dice')}
      ${menu_entry('pass_turn',     '&#x0060;', 'Pass turn')}
      ${menu_entry('buy_card',      '&#xe11b;', 'Buy card')}
      ${menu_entry('show_cards',    '&#xe11a;', 'Show cards', content = '<span class="badge badge-info menu-alert"></span>')}
      ${menu_entry('show_exchange', '&#xe1d4;', 'Exchange resources')}
      ${menu_entry('refresh',       '&#xe124;', 'Refresh')}
      ${menu_entry('show_history',  '&#xe015;', 'Show history')}
      ${menu_entry('show_stats',    '&#x0072;', 'Show stats')}
    </div>
  </div>
</div>
