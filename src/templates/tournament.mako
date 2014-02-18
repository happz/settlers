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
        <li><a href="#players" location-hash="#players">Players</a></li>
        <li><a href="#chat" location-hash="#chat">Chat</a></li>
        <li><a href="#history" location-hash="#history">History</a></li>
        <li><a href="#rounds" location-hash="#rounds">Rounds</a></li>
        <li><a href="#stats" location-hash="#stats">Statistics</a></li>
      </ul>

      <div id="empty" class="hide">
      </div>

      <div id="players" class="hide">
        <table class="table table-bordered table-hover">
          <thead>
            <tr>
              <th style="width: 25%;">${_('Name')}</th>
              <th style="width: 15%;">${_('Points')}</th>
            </tr>
          </thead>
          <tbody>
          </tbody>
        </table>
      </div>

      <div id="chat" class="hide">
        <div class="settlers-view-list">
          <div class="span6">
            ${ui_form_start(action = '/tournament/chat/add?tid=' + str(tournament.id), legend = 'New message', id = 'chat_post')}
              ${ui_textarea(form_name = 'text', size = 'xlarge')}

              <div class="control-group">
                <div class="hide chat-preview well" id="preview"></div>
              </div>
              <div class="control-group">
                <div class="controls">
                  <input class="btn" type="submit" value="${_('Add')}">
                  <input class="btn btn-info btn-preview" type="button" value="${_('Preview')}">
                  <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" rel="tooltip" data-placement="right" title="${_('Syntax help')}" target="_new"><span class="icon-question-mark"></i></a>
                </div>
              </div>
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
        <span class="win-commandicon win-commandring icon-${icon}"></span>
        ${content}
      </button>
    </%def>

    <hr />

    <div class="win-commandlayout" style="text-align: center">
      ${menu_entry('show_players', 'users', 'Show players')}
      ${menu_entry('show_rounds', 'table-2', 'Show rounds')}
      ${menu_entry('show_chat', 'comment-3', 'Show chat')}
      ${menu_entry('show_history', 'clipboard', 'Show history')}
      ${menu_entry('refresh', 'refresh', 'Refresh')}
      ${menu_entry('show_stats', 'bars-3', 'Show stats')}
    </div>
  </div>

  </div>
</div>
