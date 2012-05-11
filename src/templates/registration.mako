<%inherit file="page.mako" />

<%namespace file="lib.mako" import="*" />
<%namespace file="hlib_widgets.mako" import="*" />

  ${row_start()}
  ${w_form_start('checkin', 'New account', 'checkin')}
    ${w_form_input('username', 'text', 'Login name', required = True)}
    ${w_form_input('password1', 'password', 'Password', required = True)}
    ${w_form_input('password2', 'password', 'Password verification', required = True)}
    ${w_form_input('email', 'text', 'E-mail address')}
    ${w_submit_row('Check in')}
  ${w_form_end()}
  ${row_end()}
