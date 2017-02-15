<%!
  import hlib
  import hruntime
%>

<%inherit file="hlib_page.mako" />

<%def name="page_title()">
  ${error.message}
</%def>


    <div class="error_header">
      <h1>${error.http_status} ${error.msg % error.params}</h1>
    </div>

    <div id="accordion">
      <fieldset>
        <legend class="accordion_toggle">Call stack</legend>
        <div class="accordion_content">
          <% i = 0 %>
          <br />
          <table>
            % for entry in error.tb:
              <% i = i + 1 %>
              <tr>
                <td>${i}.</td>
                <td>${entry[0]}:${entry[1]} ${entry[2]}</td>
              </tr>
              <tr>
                <td />
                <td>${entry[3]}</td>
              </tr>
            % endfor
          </table>
        </div>
      </fieldset>

      <fieldset>
        <legend class="accordion_toggle">HTTP Request</legend>
        <div class="accordion_content">
          <table>
            % for (name, value) in hruntime.request.headers.iteritems():
              <tr><td>${name}</td><td>${value}</td></tr>
            % endfor
          </table>
        </div>
      </fieldset>
    </div>
