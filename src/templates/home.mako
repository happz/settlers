<%!
  import hlib
  import hruntime
%>

<%namespace file="hlib_ui.mako" import="*" />

<%def name="page_header()">
  ${parent.page_header()}

  <link rel="stylesheet" href="/static/css/jquery.qtip.css" type="text/css" />
  <script type="text/javascript" src="/static/script/jquery.qtip.js"></script>
</%def>

<%inherit file="page.mako" />

${ui_page_header('Home')}

<div class="row-fluid">
  <div class="span12">

    <%def name="ui_section(id, label)">
      <!-- "${label}" section -->
      ${ui_section_header('s' + id, label)}
        <div id="${id}" class="listview-container grid-layout"></div>
      </section>
    </%def>

    ${ui_section('active', 'Active')}
    ${ui_section('free', 'Free')}
    ${ui_section('finished', 'Finished')}

  </div>
</div>
