<%!
  import hlib
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

<%def name="page_header()">
  ${parent.page_header()}

  <script type="text/javascript">
    $(window).bind('hlib_prestartup', function () {
      window.settlers = window.settlers || {};
      window.settlers.tournament = {
        tid:			${tournament.id},
        stage:			${tournament.stage}
      };
    });
  </script>
</%def>    

</div>
<div class="container">
  <div class="row">

  <div class="span2">&nbsp;</div>

  <div class="span8">
    <div id="views">
      <ul class="hide">
        <li><a href="#empty">Empty</a></li>
        <li><a href="#players">Players</a></li>
        <li><a href="#chat">Chat</a></li>
        <li><a href="#history">History</a></li>
        <li><a href="#rounds">Rounds</a></li>
        <li><a href="#stats">Statistics</a></li>
      </ul>

      <div id="empty" class="hide">
      </div>

      <div id="players" class="hide">
      </div>

      <div id="chat" class="hide">
        <div style="height: 798px; overflow: auto">
          <div class="span6">
          ${ui_form_start(action = '/tournament/chat/add?tid=' + str(tournament.id), legend = 'New message', id = 'chat_post')}
            ${ui_textarea(form_name = 'text', size = 'xlarge')}
            ${ui_submit(value = 'Add')}
          ${ui_form_end()}
          </div>

          ${chat_table()}
        </div>
      </div>

      <div id="history" class="hide">
        <div style="height: 798px; overflow: auto">
          <table class="table table-hover">
            <thead>
              <tr>
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

      <div id="rounds" class="hide">
      </div>

      <div id="stats" class="hide">
      </div>
    </div>
  </div>

  <div class="span2">
    <div>
      <header><h3>${_('Tournament')}&nbsp;#<span id="tournament_id"></span></h3></header>

      <div id="tournament_name"></div>
      <div><span id="tournament_round"></span>. ${_('round')}</div>
      <div><span id="tournament_num_players"></span> ${_('players')}</span></div>
    </div>

    <hr />

    <div id="tournament_status" class="hide text-success"><p></p></div>

    <%def name="menu_entry(id, icon, label, content = None)">
      <% content = content or '' %>

      <button class="win-command" title="${_(label)}" rel="tooltip" data-placement="left" id="${id}" style="position: relative">
        <span class="win-commandimage win-commandring">${icon}</span>
        ${content}
      </button>
    </%def>

    <hr />

    <div class="win-commandlayout" style="text-align: center">
      ${menu_entry('show_players',  '&#x0060;', 'Show players')}
      ${menu_entry('show_rounds',   '&#xe1a5;', 'Show rounds')}
      ${menu_entry('show_chat',     '&#x005a;', 'Show chat')}
      ${menu_entry('show_history',  '&#xe015;', 'Show history')}
      ${menu_entry('refresh',       '&#xe124;', 'Refresh')}
      ${menu_entry('show_stats',    '&#x0072;', 'Show stats')}
    </div>
  </div>

  </div>
</div>
