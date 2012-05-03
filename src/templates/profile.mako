<%!
  import time
%>

<%namespace file="hlib_header.mako" import="*" />
<%namespace file="header.mako"   import="*" />

${header(plugins = 'accordion', functions = ['start_game_on_turn_timer'])}

${error_msg()}
${menu_level1()}
<br />

<b>Player ${profile_user.name}</b>

<table>
  <tr>
    <td>Last online:</td>
    <td>${time.strftime(user.date_format, time.localtime(profile_user.atime))}</td>
  </tr>

  <tr>
    <td>Free games:</td>
    <td>${profile_user.free_games_count}</td>
  </tr>
  <tr>
    <td>Current games:</td>
    <td>${profile_user.current_games_count}</td>
  </tr>
  <tr>
    <td>Finished games:</td>
    <td>${profile_user.finished_games_count}</td>
  </tr>
  <tr>
    <td>Canceled games:</td>
    <td>${profile_user.canceled_games_count}</td>
  </tr>
</table>

<%include file="footer.mako" />
<%include file="hlib_footer.mako" />
