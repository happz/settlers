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

    <div class="control-group">
      <div class="hide chat-preview well" id="preview">
      </div>
    </div>

    <div class="control-group">
      <div class="controls">
        <input class="btn" type="submit" value="${_('Add')}">
        <input class="btn btn-info btn-preview" type="button" value="${_('Preview')}">
        <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" rel="tooltip" data-placement="right" title="${_('Syntax help')}" target="_new"><i class="icon-help-4"></i></a>
      </div>
    </div>
  ${ui_form_end()}
</%def>

<%def name="chat_table()">
  <div id="chat_posts">
    <div class="pagination pagination-right">
      <ul>
        <li><a href="#" class="chat-first">${_('First')}</a></li>
        <li><a href="#" class="chat-prev">${_('Previous')}</a></li>
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
        <li><a href="#" class="chat-prev">${_('Previous')}</a></li>
        <li></li>
        <li><a href="#" class="chat-next">${_('Next')}</a></li>
        <li><a href="#" class="chat-last">${_('Last')}</a></li>
      </ul>
    </div>
  </div>
</%def>
