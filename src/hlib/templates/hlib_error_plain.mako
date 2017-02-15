<%!
  import pprint
  import time
  import hlib
  import hlib.server
  import hruntime
%>

<%def name="trace()">
<%
    s = []
    i = 0

    for entry in error.tb:
      i = i + 1
      sl = len(str(i))

      s.append('    %i. %s:%s %s' % (i, entry[0], entry[1], entry[2]))
      s.append('  %s %s' % (' ' * (sl + 1), entry[3]))
  %>${'\r\n'.join(s)}
</%def>


----- ** ----- ** -----
Exception occured at ${error.file}:${error.line}
  Stamp: ${time.strftime('%d/%m/%Y %H:%M:%S', hruntime.localtime)}
  Message: ${error.message}
  Request: ${hruntime.request.requested_line.encode('ascii', 'replace')} - ${hlib.server.ips_to_str(hruntime.request.ips)}
  % if hruntime.user:
  User: ${hruntime.user.name}
  % else:
  User: <unknown>
  % endif
  TID: ${hruntime.tid}

  Runtime:
  % for p in (hruntime.PROPERTIES + ['cache', 'time', 'localtime']):
    ${p}: ${getattr(hruntime, p)}
  % endfor

  Request headers:
  % for (name, value) in hruntime.request.headers.iteritems():
    ${name}: ${value.encode('ascii', 'replace')}
  % endfor

  Input data:
    % for name, value in hruntime.request.params.iteritems():
      ${name}: ${unicode(value).encode('ascii', 'replace')}
    % endfor

  Call stack:${trace().strip()}

----- ** ----- ** -----
