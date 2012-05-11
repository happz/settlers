<%namespace file="lib.mako"          import="*"/>
<%namespace file="hlib_widgets.mako" import="*"/>

<%inherit file="page.mako" />

<div class="row">
  <div class="prepend-3 span-6 last">
    ${chat_new_post('/chat')}
  </div>
</div>

<div class="row">
  <div class="span-12">
    ${chat_table(12, prepend = 1)}
  </div>
</div>
