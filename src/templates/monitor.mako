<%!
  import types
  import hlib.stats
%>

<%inherit file="page.mako" />

<div class="prepend-top span-14">
  % for namespace_name, namespace in stats.iteritems():
    <%
      collections = []
    %>
    <div class="span-8 last">
      <h3>${namespace_name}</h3>

      <table>
        % for record_name, record_value in namespace.iteritems():
          % if type(record_value) not in [types.DictType, types.ListType]:
            <tr>
              <td>${record_name}</td>
              <td>${record_value}</td>
            </tr>
          % else:
            <%
              collections.append(record_name)
            %>
          % endif
        % endfor
      </table>
    </div>

    % for collection_name in collections:
      <%
        collection = namespace[collection_name]
      %>
      <div class="prepend-1 span-13 last">
        <h4>${collection_name}</h4>
        <table>
          % if len(collection) > 0:
            <tr>
              <%
                if type(collection) == types.DictType:
                  keys = collection.values()[0].keys()
                else:
                  keys = ['ID'] + collection[0].keys()
              %>
              % for key in keys:
                <th>${key}</th>
              % endfor
            </tr>
            % for record in hlib.stats.iter_collection(collection):
              <tr>
                % for k in keys:
                  <td>${record[k]}</td>
                % endfor
              </tr>
            % endfor
          % endif
        </table>
      </div>
    % endfor
    <hr />
  % endfor
</div>
