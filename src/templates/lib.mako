<%!
  import time
  import hlib.format
  import hlib
%>

<%namespace file="hlib_widgets.mako" import="*" />

<%def name="row_start(width = 6, offset = 0)">
  <div class="row"><div class="prepend-${(12 - width) / 2 + offset} span-${width - offset} last">
</%def>

<%def name="row_end()">
  </div></div>
</%def>

<%def name="stamp_to_days_hours(s)">
  ${int(s / 86400)} days, ${int((s % 86400) / 3600)} hours, ${int(((s % 86400) % 3600) / 60)} minutes
</%def>

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
  ${w_form_start(url_root + '/add' + params, 'New message', 'chat_post')}
    ${w_form_text('text')}

    ${w_submit_row('Add')}
  ${w_form_end()}
</%def>

<%def name="chat_table(width, prepend = None, id_prefix = 'chat')">
  <%
    if prepend != None:
      classes = 'prepend-%i span-%i' % (prepend, width - 2 * prepend)
    else:
      classes = 'span-' + str(width)
  %>

  <div id="chat_posts">
    <div class="${classes} last centered">
      <span class="${id_prefix}-first">&lt;&lt;</span>
      <span class="${id_prefix}-prev">&lt;</span>
      <span class="${id_prefix}-position"></span>
      <span class="${id_prefix}-next">&gt;</span>
      <span class="${id_prefix}-last">&gt;&gt;</span>
    </div>

    <div class="span-${width} prepend-top">
      <table>
        <tbody>
        </tbody>
      </table>
    </div>

    <div class="${classes} last centered">
      <span class="${id_prefix}-first">&lt;&lt;</span>
      <span class="${id_prefix}-prev">&lt;</span>
      <span class="${id_prefix}-position"></span>
      <span class="${id_prefix}-next">&gt;</span>
      <span class="${id_prefix}-last">&gt;&gt;</span>
    </div>
  </div>
</%def>
