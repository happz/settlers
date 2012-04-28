<%!
  import hlib
%>

<%def name="page_script()">
  ${parent.page_script()}

window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:                        'recovery'
    focus:			'username'
    handlers:
      s200:	(response, form) ->
        window.hlib.INFO.success 'New password was sent to your e-mail'
        window.hlib.redirect "${hlib.url(path = '/login/')}"
</%def>

<%inherit file="page.mako" />
<%namespace file="hlib_widgets.mako"  import="*" />

<div class="prepend-3 span-8 append-3 last">
  ${w_form_start('/registration/recovery/recover', 'Password recovery', 'recovery')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('email', 'text', 'E-mail address')}
    ${w_submit_row('Create new password')}
  ${w_form_end()}
</div>
