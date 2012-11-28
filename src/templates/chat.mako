<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*"/>

<%inherit file="page.mako" />

${ui_page_header('Chat')}

<div class="row-fluid">
  <div class="span12">
    ${chat_new_post('/chat')}
  </div>
</div>

<div class="row-fluid">
  <div class="span12">
    ${chat_table()}
  </div>
</div>
