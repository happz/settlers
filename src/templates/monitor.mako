<%!
  import sys
  import types

  import hlib.stats
%>

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

% for namespace_name, namespace in stats.items():
  <%
    collections = []

    ns_fmt = hlib.stats.stats_fmt.get(namespace_name, {})
  %>

  ${row_start(width = 10)}
    <ul class="monitor-namespace">
      <li class="header">${namespace_name}</li>

      % for record_name, record_value in namespace.items():
        % if type(record_value) not in [types.DictType, types.ListType]:
          <li class="info info-with-border">
            <span class="monitor-record-name">${record_name}</span>
            <%
              if record_name in ns_fmt:
                record_value = ns_fmt[record_name] % record_value
              else:
                record_value = fmt(record_value)
            %>            
            <span class="monitor-record-value right">${record_value}</span>
          </li>
        % else:
          <%
            collections.append(record_name)
          %>
        % endif
      % endfor
    </ul>
  ${row_end()}

  % for collection_name in collections:
    <%
      collection = namespace[collection_name]
    %>

    % if len(collection) > 0:
    ${row_start(width = 10, offset = 1)}
      <table class="content-table">
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
    ${row_end()}
    % endif
  % endfor
% endfor
