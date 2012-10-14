<%!
  import sys
  import hlib
  import lib.chat
%>

<%
  import time
  import types
  import games
  import hlib
  import tournament
  import hruntime
%>

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

<%def name="page_script()">
  ${parent.page_script()}

  ${chat_script('chat_table', '/tournament/chat/lister')}
</%def>

<%def name="tournament_action(view, tour)">
  % if view.type == 'free':
    % if tour.has_player(user) == True:
      % if tour.has_confirmed_player(user) == True:
          ${chat_header('/tournament/open?id=' + str(tour.id), tour.my_player.chat)}
        | <a href="/tournament/open?id=${tour.id}">${_('Enter')}</a>

      % else:
        <a href="/tournament/join?id=${tour.id}">${_('Join')}</a>

      % endif

    % else:
      % if tour.has_password != True:
        <a href="/tournament/join?id=${tour.id}">${_('Join')}</a>

      % else:
        <form action="/tournament/join?id=${tour.id}" method="post">
          <input type="password" name="password" class="textbox" />
          <input type="submit" value="${_('Join')}" class="button" />
        </form>
      % endif
    % endif

  % else:
      ${chat_header('/tournament/open?id=' + str(tour.id), tour.my_player.chat)}
    | <a href="/tournament/open?id=${tour.id}">${_('Enter')}</a>

  % endif
</%def>

<div id="accordion">

<fieldset>
  <legend class="accordion_toggle">${_('Tournament')}</legend>
  <table class="accordion_content">
    <tr>
      <td>${_('Tournament number')}:</td>
      <td>${tour.id}</td>
    </tr>
    <tr>
      <td>${_('Tournament name')}:</td>
      <td>${tour.name}</td>
    </tr>
    <tr>
      <td>${_('Number of players')}:</td>
      <td>${tour.num_players}</td>
    </tr>
    <tr>
      <td>${_('Number of signed players')}:</td>
      <td>${len(tour.players)}</td>
    </tr>
    % if user.is_admin:
      <tr>
        <td><a href="/tournament/begin">Begin</a></td>
      </tr>
    % endif
  </table>
</fieldset>

<fieldset>
  <legend class="accordion_toggle">${_('Signed players')}</legend>
  <table class="accordion_content">
    % for player in tour.players.values():
      <tr>
        <td>${player.user.name}</td>
      </tr>
    % endfor
  </table>
</fieldset>

% if tour.stage != tournament.Tournament.STAGE_FREE:

% for i in range(1, tour.round + 1):
  <fieldset>
    <legend class="accordion_toggle">${i}. ${_('round')}</legend>
    <table class="accordion_content">
      <%
        groups, byes = tour.get_groups(round = i)
      %>

      % for j, group in groups.items():
        <tr>
          <td>${j}. ${_('group')}:</td>
          <td>${', '.join([p.user.name for p in group.players.values()])}</td>
          <td>${len(group.closed_games)} of 1 games finished</td>
        </tr>
      % endfor
      <tr>
        <td>${_('Bye players')}:</td>
        <td>${', '.join([u.name for u in byes])}</td>
      </tr>

      % if tour.get_has_closed_all_games(round = i):
        <tr>
          <td>Poradi hracu</td>
        </tr>
        <tr>
          <td />
          <td />
          <td>Poradi</td>
          <td>Body</td>
        </tr>

      % endif
    </table>
  </fieldset>
% endfor

% endif

</div>

${chat_panel('/tournament/chat', lib.chat.ChatPagerTournament(tour))}
