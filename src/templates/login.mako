<%!
  import hlib
%>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>

<div class="prepend-top prepend-3 span-8 append-3 last">
  ${w_form_start('/login/login', 'Game login', 'login')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('password', 'password', 'Password')}
    ${w_submit_row('Log in')}
  ${w_form_end()}
</div>
