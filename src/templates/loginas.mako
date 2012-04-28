<%!
  import hlib
%>

<%def name="page_script()">
  ${parent.page_script()}

window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:			'loginas'
    focus:			'username'
    dont_clean:			true
    handlers:
      s200:	() ->
        window.hlib.redirect "${hlib.url(path = '/home/')}"

      s403:	() ->
        window.hlib.redirect "${hlib.url(path = '/vacation/')}"
</%def>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>

<div class="prepend-top prepend-3 span-8 append-3 last">
  ${w_form_start('/loginas/loginas', 'Admin login', 'loginas')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('password', 'password', 'Password')}
    ${w_form_input('loginas', 'text', 'Login as')}
    ${w_submit_row('Log in')}
  ${w_form_end()}
</div>
