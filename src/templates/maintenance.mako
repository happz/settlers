<%!
  import hruntime

  import lib.trumpet
%>

<%inherit file="page.mako" />

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

${ui_page_header('Maintenance mode')}

<div class="row-fluid">
  <div class="span12">
    <div>
      <p>${_('Server is currently running in a maintenance mode - only selected users (admins) can log in. More info can be found in message bellow. If you are allowed to log in, please use form bellow.')}</p>
      <p>${_('This page will check periodicaly if maintenance mode is still enabled, and informs you when log in is available again.')}</p>
    </div>
    <div>
      <p>${lib.trumpet.Board().text}</p>
    </div>
  </div>
</div>

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/login/login', id = 'login', legend = 'Game login')}
    ${ui_input(type = 'text', label = 'Login name', form_name = 'username')}
    ${ui_input(type = 'password', label = 'Password', form_name = 'password')}
    ${ui_submit(value = 'Log in')}
  ${ui_form_end()}
${ui_row_end()}
