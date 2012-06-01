<%!
  import hruntime

  import lib.trumpet
%>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="lib.mako" import="*" />

${row_start()}
  <div class="formee">
    <fieldset class="maintenance-info">
      <legend>${_('Maintenance mode')}</legend>
      <div class="grid-12-12">
        <p>${_('Server is currently running in a maintenance mode - only selected users (admins) can log in. More info can be found in message bellow. If you are allowed to log in, please use form bellow.')}</p>
        <p>${_('This page will check periodicaly if maintenance mode is still enabled, and informs you when log in is available again.')}</p>
      </div>
      <div class="grid-12-12">
        <p>${lib.trumpet.Board().text}</p>
      </div>
    </fieldset>
  </div>
${row_end()}

${row_start()}
  ${w_form_start('/login/login', 'Game login', 'login')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('password', 'password', 'Password')}
    ${w_submit_row('Log in')}
  ${w_form_end()}
${row_end()}
