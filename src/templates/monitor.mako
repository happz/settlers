<%!
  import types

  import hlib.stats
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

${ui_page_header('Monitor')}

<div class="row-fluid">
  <div class="offset2 span10">

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
