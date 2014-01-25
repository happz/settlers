<%!
  import time
  import os.path
  import hruntime

  import lib
%>

<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header(player.name + ('&nbsp;<span class="user-online">(online)</span>' if player.is_online else ''))}

<div class="row-fluid">
  <div class="span2">
    % if os.path.exists(player.avatar_filename):
      <%
        avatar_image = '/static/images/avatars/' + player.avatar_name + '.jpg'
      %>
      <img class="img-polaroid" src="${avatar_image}${lib.version_stamp(avatar_image)}" />
    % endif
  </div>

  % if player_stats != None:
  <div class="span10">
    ${ui_section_header('stats_settlers', 'Settlers stats')}
      <table class="table table-hover">
        <tr>
          <td>${_('Total games')}</td>
          <td>${player_stats.games}</td>
        </tr>
        <tr>
          <td>${_('Won games')}</td>
          <td>${player_stats.wons}</td>
        </tr>
        <tr>
          <td>${_('Finished games')}</td>
          <td>${player_stats.finished}</td>
        </tr>
        <tr>
          <td>${_('Points')}</td>
          <td>${player_stats.points}</td>
        </tr>
        <tr>
          <td>${_('Points per game')}</td>
          <td>${'%.3f' % player_stats.points_per_game}</td>
        </tr>
      </table>
    </section>
  </div>
  % endif
</div>

