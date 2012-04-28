<%!
  import hlib
  import hruntime
%>

<%def name="page_header()">
  ${parent.page_header()}

  <link rel="stylesheet" href="/static/css/jquery.qtip.css" type="text/css" />
  ${parent.script_file('jquery.qtip', 'js')}
</%def>

<%inherit file="page.mako" />

<div class="prepend-top span-14">
  <ul id="recent_events" class="recent-events">
  </ul>
</div>
