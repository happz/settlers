<%!
  import hlib
%>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="lib.mako" import="*" />

${row_start()}
  ${w_form_start('/login/login', 'Game login', 'login')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('password', 'password', 'Password')}
    ${w_submit_row('Log in')}
 ${w_form_end()}
${row_end()}
