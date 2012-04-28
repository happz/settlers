<%!
  PLUGINS = ['Accordion', 'Sound']
  FUNCTIONS = ['bind_change']
%>

<%
  import gc
%>

<%inherit file="page.mako" />

<pre>

<%
  gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE)
%>

${gc.collect(2)}

</pre>
