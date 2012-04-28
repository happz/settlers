<%!
  import hlib.stats
%>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>



${header(plugins = 'tablesorter')}


<table class="list sortable">
  <thead>
    <tr>
      <th>ID</th>
      <th>Idle Time</th>
      <th>Last Request Time</th>
      <th>IP</th>
      <th>URL</th>
      <th>User</th>
    </tr>
  </thead>
  <tbody>
    % for thread in threads:
      <tr>
        <td>${thread[0]}</td>
        <td>${time.strftime('%H:%M:%S', time.gmtime(thread[1].idle_time))}</td>
        <td>${time.strftime('%H:%M:%S', time.gmtime(thread[1].last_req_time))}</td>
        <td>${thread[1].ip}</td>
        <td>${thread[1].url}</td>
        <td>${thread[1].user}</td>
      </tr>
    % endfor
  </tbody>
</table>

<br />

<script type="text/javascript">
  $(document).ready(function() {
    $(".sortable")
    .tablesorter({
      cssAsc:     'headerSortUp',
      cssDesc:    'headerSortDown',
      dateFormat: 'uk',
      widgets:    ['cookie']
    });
  });
</script>

  <a href="http://www.happz.cz:8080/osadnici/wiki" target="_blank">Help</a>
| <a href="/login/">Log in</a>
| <a href="/registration/">Registration</a>
| <a href="/registration/password/">Forgot password?</a>
| <a href="/cpstatus/">Status</a>

<%include file="footer.mako" />
