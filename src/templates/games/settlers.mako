<%!
  import hlib
%>

<%namespace file="../hlib_widgets.mako"  import="*"/>
<%namespace file="../event.mako"         import="*" />
<%namespace file="../lib.mako"           import="*" />

<%inherit file="../page.mako" />

<%def name="page_title()">
  ${' '.join([_('Settlers'), '-', _('Game'), str(game.id) + ':']) + ', '.join([p.user.name for p in game.players.itervalues()])}
</%def>

<%def name="page_header()">
  ${parent.page_header()}

  <script type="text/javascript">
    $(window).bind('hlib_prestartup', function () {
      window.settlers = window.settlers || {};
      window.settlers.game = {
        gid:	${game.id}
      };
    });
  </script>
</%def>

<div class="span-2 prepend-top">
  <div class="game-info">
    <div                class="header corners-top">Hra #<span id="game_id" class="game-id"></span></div>
    <div id="game_name" class="game-name info"></div>
    <div                class="game-round corners-bottom info important-info"><span id="game_round"></span>. kolo</div>
  </div>

  <div class="settlers-last-numbers">
    <div class="header corners-top">Last numbers</div>
    <span id="settlers_last_numbers" class="info important-info corners-bottom"></span>
  </div>

 <div class="settlers-game-status framed hidden">
 </div>

  <div class="framed centered">
    <span id="pass_turn"     class="icon icon-medium icon-game-pass-turn" title="Pass turn"></span>
    <span id="roll_dice"     class="icon icon-medium icon-game-roll-dice" title="Roll dice"></span>
    <span id="refresh"       class="icon icon-medium icon-game-refresh" title="Refresh"></span>
    <span id="show_board"    class="icon icon-medium icon-game-board" title="Show board"></span>
    <span id="show_cards"    class="icon icon-medium icon-game-cards" title="Show cards"></span>
    <span id="show_chat"     class="icon icon-medium icon-game-chat" title="Show chat"></span>
    <span id="show_exchange" class="icon icon-medium settlers-icon-game-exchange" title="Exchange resources"></span>
    <span id="show_history"  class="icon icon-medium icon-game-history" title="Show history"></span>
  </div>
</div>

<div class="span-10 prepend-top append-bottom">
  <div id="views">

    <ul class="hidden">
      <li><a href="#empty">Empty</a></li>
      <li><a href="#chat">Chat</a></li>
      <li><a href="#history">History</a></li>
      <li><a href="#board">Board</a></li>
      <li><a href="#cards">Cards</a></li>
      <li><a href="#exchange">Exchange</a></li>
    </ul>

    <div id="empty" class="hidden" ></div>

    <div id="chat" class="hidden">
      <div class="prepend-1 span-8 append-1 last">
        ${chat_new_post('/game/chat', gid = game.id)}
      </div>

      ${chat_table(10)}
    </div>

    <div id="history" class="hidden">
      <div class="prepend-1 span-8 append-1 last" style="height: 798px; overflow: auto">
        <table>
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

    <div id="board" class="hidden">
      <div class="game-board">
      </div>
    </div>

    <div id="cards" class="hidden">
      ${w_form_start('/game/settlers/cards/new', 'Buy new action card', 'new_card')}
        ${w_submit_button('Buy')}
      ${w_form_end()}

      <div id="cards_list"></div>
    </div>

    <div id="exchange" class="hidden">
    </div>
  </div>
</div>

<div class="span-2 prepend-top last">
  <div>
    <div id="game-player-0-placeholder"></div>
    <div id="game-player-1-placeholder"></div>
    <div id="game-player-2-placeholder"></div>
    <div id="game-player-3-placeholder"></div>
  </div>
</div>
