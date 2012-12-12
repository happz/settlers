<%!
  import pprint
  import types

  import hlib.stats

  import hruntime

  def pformat(d):
    return pprint.pformat(d).replace('<', '&lt;').replace('>', '&gt;')
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

<%def name="fmt(n, precision = 2)">
  <%
    if type(n) in types.StringTypes:
      return n

    suffixes = ['','K','M','G','T']
    si = 0

    while n > 1000:
      si += 1
      n /= 1000

    return '%.*f %s' % (precision, n, suffixes[si])
  %>
</%def>

<%def name="page_header()">
  ${parent.page_header()}

  <script type="text/javascript" src="/static/script/sh_main.js"></script>
  <script type="text/javascript" src="/static/script/sh_python.js"></script>
  <link rel="stylesheet" href="/static/css/sh_style.css" type="text/css" />
</%def>

${ui_page_header('Monitor')}

<div class="row-fluid">
  <div class="offset2 span10">

  ${ui_section_header('runtime', 'Runtime status')}

<table class="table table-striped">
  <tbody>

% for namespace_name, namespace in stats.items():
  <%
    collections = []

    ns_fmt = hlib.stats.stats_fmt.get(namespace_name, {})
  %>

  <tr>
    <th colspan="2">${namespace_name}</th>
  </tr>

  % for record_name, record_value in namespace.items():
    % if type(record_value) not in [types.DictType, types.ListType]:
      <tr>
        <td>${record_name}</td>
        <td class="pull-right">
          <%
            if record_name in ns_fmt:
              record_value = ns_fmt[record_name] % record_value
            else:
              record_value = fmt(record_value)
          %>
          ${record_value}
        </td>
      </tr>
    % else:
      <%
        collections.append(record_name)
      %>
    % endif
  % endfor

  % for collection_name in collections:
    <%
      collection = namespace[collection_name]
    %>

    % if len(collection) > 0:
      <tr>
        <td></td>
        <td>
          <table class="table table-striped">
            <caption>${collection_name}</caption>
            % if len(collection) > 0:
              <thead>
                <tr>
                  <%
                    keys = ['ID'] + collection.values()[0].keys()
                  %>
                  % for key in keys:
                    <th>${key}</th>
                  % endfor
                </tr>
              </thead>
              <tbody>
                % for record in hlib.stats.iter_collection(collection):
                  <tr>
                    % for k in keys:
                      <td>${record[k]}</td>
                    % endfor
                  </tr>
                % endfor
              </tbody>
            % endif
          </table>
        </td>
      </tr>
    % endif
  % endfor
% endfor

  </tbody>
</table>

  </div>
</div>

<div class="row-fluid">
  <div class="offset2 span10">
    ${ui_section_header('config', 'Config')}

    <h4>Application</h4>
    <pre class="sh_python">
${pformat(hruntime.app.config)}
    </pre>

    % for engine in hruntime.app.engines:
      % for server in engine.servers:
        <h4>${engine.stats_name} - ${server.name}</h4>
        <pre class="sh_python">
${pformat(server.config)}
        </pre>
      % endfor
    % endfor
  </div>
</div>
