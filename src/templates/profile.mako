<%!
  import time
  import hruntime
%>

<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header(player.name + ('&nbsp;<span class="user-online">(online)</span>' if player.is_online else ''))}

<div class="row-fluid">
  <div class="offset2 span10">

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
</div>

