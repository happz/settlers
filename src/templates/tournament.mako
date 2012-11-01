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
  <div class="prepend-2 span-8 last">
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
          ${chat_new_post('/tournament/chat', gid = tournament.id)}
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
</div>
