<%!
  import time
  import hlib.format
  import hlib
%>

<%namespace file="hlib_ui.mako" import="*" />

<%!
  import types
  import hlib.i18n
%>

<%def name="chat_new_post(url_root, **kwargs)">
  <%
    params = '&'.join(['%s=%s' % (k, v) for k, v in kwargs.items()])
    if len(params) > 0:
      params = '?' + params
  %>

  ${ui_form_start(action = url_root + '/add' + params, legend = 'New message', id = 'chat_post')}
    ${ui_textarea(form_name = 'text', size = 'xxlarge')}

    ${ui_submit(value = 'Add')}
  ${ui_form_end()}
</%def>

<%def name="chat_table(id_prefix = 'chat')">
  <div id="chat_posts">
    <div class="pagination pagination-right">
      <ul>
        <li><a href="#" class="chat-first">${_('First')}</a></li>
        <li><a href="#" class="chat-previous">${_('Previous')}</a></li>
        <li></li>
        <li><a href="#" class="chat-next">${_('Next')}</a></li>
        <li><a href="#" class="chat-last">${_('Last')}</a></li>
      </ul>
    </div>

    <table class="table">
      <tbody>
      </tbody>
    </table>

    <div class="pagination pagination-right">
      <ul>
        <li><a href="#" class="chat-first">${_('First')}</a></li>
        <li><a href="#" class="chat-previous">${_('Previous')}</a></li>
        <li></li>
        <li><a href="#" class="chat-next">${_('Next')}</a></li>
        <li><a href="#" class="chat-last">${_('Last')}</a></li>
      </ul>
    </div>
  </div>
</%def>
