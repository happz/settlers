<%!
  import hlib
  import hruntime
%>

<%def name="page_header()">
  ${parent.page_header()}

  <link rel="stylesheet" href="/static/css/jquery.qtip.css" type="text/css" />
  <script type="text/javascript" src="/static/script/jquery.qtip.js"></script>
</%def>

<%inherit file="page.mako" />

<div class="row">
  <div class="prepend-top span-12 last">
    <ul id="recent_events" class="recent-events">
    </ul>
  </div>
</div>
