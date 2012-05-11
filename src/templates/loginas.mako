<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="lib.mako" import="*" />

${row_start()}
  ${w_form_start('/loginas/loginas', 'Admin login', 'loginas')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('password', 'password', 'Password')}
    ${w_form_input('loginas', 'text', 'Login as')}
    ${w_submit_row('Log in')}
  ${w_form_end()}
${row_end()}
