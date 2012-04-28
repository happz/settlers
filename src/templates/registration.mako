<%!
  import hlib
%>

<%def name="page_script()">
  ${parent.page_script()}

window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:			'checkin'
    focus:			'username'
    refill:			true
    handlers:
      s200:	(response, form) ->
        window.hlib.INFO.success 'New account created, you may log in', () ->
          window.hlib.redirect "${hlib.url(path = '/login/')}"

</%def>

<%inherit file="page.mako" />
<%namespace file="hlib_widgets.mako" import="*" />

<div class="prepend-3 span-8 append-3 last">
  ${w_form_start('checkin', 'New account', 'checkin')}
    ${w_form_input('username', 'text', 'Login name', required = True)}
    ${w_form_input('password1', 'password', 'Password', required = True)}
    ${w_form_input('password2', 'password', 'Password verification', required = True)}
    ${w_form_input('email', 'text', 'E-mail address')}
    ${w_submit_row('Check in')}
  ${w_form_end()}
</div>
