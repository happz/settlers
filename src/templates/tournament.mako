<%!
  import hlib
%>

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="event.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

<%def name="page_header()">
  ${parent.page_header()}

  <script type="text/javascript">
    $(window).bind('hlib_prestartup', function () {
      window.settlers = window.settlers || {};
      window.settlers.tournament = {
        tid:	${tournament.id}
      };
    });
  </script>
</%def>    

<div class="row prepend-top append-bottom" style="overflow: visible">
  <div class="prepend-2 span-8">
  <div id="views">

    <ul class="hide">
      <li><a href="#players">Players</a></li>
      <li><a href="#chat">Chat</a></li>  
      <li><a href="#history">History</a></li>
    </ul>

    <div id="players" class="hide">
    </div>

    <div id="chat" class="hide">
      <div class="row">
        <div class="prepend-2 span-8 last">
          ${chat_new_post('/tournament/chat', tid = tournament.id)}
        </div>
      </div>  

      <div class="row">
        <div class="span-12 last">
          ${chat_table(12, prepend = 1)}
        </div>
      </div>  
    </div>    

    <div id="history" class="hide">
      <div style="height: 798px; overflow: auto">
        <table class="content-table">
          <caption>${_('Tournament history')}</caption>
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

  </div>
  </div>

  <div class="span-2 last">
    <div class="playable-info">
      <div                class="header corners-top">Hra #<span id="tournament_id" class="playable-id"></span></div>
      <div id="tournament_name" class="playable-name info"></div>
      <div                class="playable-round corners-bottom info important-info"><span id="tournament_round"></span>. kolo</div>
    </div>

    <div class="framed centered">
      <span id="show_chat"     class="icon icon-giant icon-playable-chat" title="${_('Show chat')}"></span>
      <span id="show_history"  class="icon icon-giant icon-playable-history" title="${_('Show history')}"></span>
    </div>
  </div>
</div>
