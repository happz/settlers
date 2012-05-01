<%!
  import time
  import hlib.format
  import hlib
%>

<%namespace file="hlib_widgets.mako" import="*" />

<%def name="page_content_start()">
  <div class="prepend-top prepend-3 span-8 append-3 last">
</%def>

<%def name="page_content_end()">
  </div>
</%def>

<%def name="quote(s)">${'"' + s + '"'}</%def>

<%def name="username_taint(user)">
  ${user.name}
  % if hruntime.request.is_tainted():
    ${str(hruntime.session.tainted)}
  % endif
</%def>

<%def name="username_onlined(user)">
  % if user.is_online:
    <span style="font-weight: bold">${username_taint(user)}</span>

  % else:
    ${username_taint(user)}

  % endif
</%def>

<%def name="username_simple_onlined(user)">
  ${user.name}
</%def>

<%def name="stamp_to_days_hours(s)">
  ${int(s / 86400)} days, ${int((s % 86400) / 3600)} hours, ${int(((s % 86400) % 3600) / 60)} minutes
</%def>

<%!
  import types
  import hlib.i18n
%>

<%def name="motd()">
  <% import lib.trumpet %>

  % if lib.trumpet.MOTD().text != '':
    <span style="font-weight: bold">${_('Message of the day')}</span>
    <div style="text-align: justify; font-weight: bold">
      % for line in lib.trumpet.MOTD().text_splitted:
        ${line}
        <br />
      % endfor
    </div>
  % endif
</%def>

<%def name="trumpet_board()">
  <% import lib.trumpet %>

  % if lib.trumpet.Board().text != '':
    <div style="text-align: center; color: red">
      % for line in lib.trumpet.Board().text_splitted:
        ${line}
        <br />
      % endfor
    </div>
  % endif
</%def>

<%namespace file="hlib_widgets.mako"  import="*"/>

<%def name="chat_post_template()">
window.settlers.templates.chat_post = '
  <tr><td>
  <fieldset class="chat-post">
    <legend>
      {{#user.is_online}}
        <span class="user-online">
      {{/user.is_online}}
      {{user.name}}
      {{#user.is_online}}
        </span>
      {{/user.is_online}} - {{time}}
    </legend>
    <div>{{{message}}}</div>
  </fieldset>
  </td></tr>
'
</%def>

<%def name="chat_new_post(url_root, **kwargs)">
  <%
    params = '&'.join(['%s=%s' % (k, v) for k, v in kwargs.iteritems()])
    if len(params) > 0:
      params = '?' + params
  %>
  ${w_form_start(url_root + '/add' + params, 'New message', 'chat_post')}
    ${w_form_text('text')}

    ${w_submit_row('Add')}
  ${w_form_end()}
</%def>

<%def name="chat_table(width, prepend = None)">
  <%
    if prepend != None:
      classes = 'prepend-%i span-%i append-%i' % (prepend, width - 2 * prepend, prepend)
    else:
      classes = 'span-' + str(width)
  %>

  <div id="chat_posts">
    <div class="${classes} last centered">
      <span class="chat-first">&lt;&lt;</span>
      <span class="chat-prev">&lt;</span>
      <span class="chat-position"></span>
      <span class="chat-next">&gt;</span>
      <span class="chat-last">&gt;&gt;</span>
    </div>

    <div class="span-${width} prepend-top">
      <table>
        <tbody>
        </tbody>
      </table>
    </div>

    <div class="${classes} last centered">
      <span class="chat-first">&lt;&lt;</span>
      <span class="chat-prev">&lt;</span>
      <span class="chat-position"></span>
      <span class="chat-next">&gt;</span>
      <span class="chat-last">&gt;&gt;</span>
    </div>
  </div>
</%def>
