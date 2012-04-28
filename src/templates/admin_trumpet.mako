<%!
  import lib.trumpet

  import hruntime
%>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako" import="*" />
<%namespace file="lib.mako"          import="*" />

<%def name="page_script()">
  ${parent.page_script()}

window.settlers.setup_forms = () ->
  new window.hlib.Form
    fid:		'board'

  new window.hlib.Form
    fid:		'password_recovery_mail'

window.settlers.setup_page = () ->
  window.settlers.setup_forms()

</%def>

${page_content_start()}

  ${w_form_start('/admin/trumpet/change_board', 'Change board', 'board')}
    ${w_form_text('text', label = 'Text', default = lib.trumpet.Board().text)}
    ${w_submit_row('Set')}
  ${w_form_end()}

  ${w_form_start('/admin/trumpet/change_password_recovery_mail', 'Change "Password recovery" mail', 'password_recovery_mail')}
    ${w_form_input('subject', 'text', label = 'Subject', default = lib.trumpet.PasswordRecoveryMail().subject)}
    ${w_form_text('text', label = 'Text', default = lib.trumpet.PasswordRecoveryMail().text)}
    ${w_submit_row('Set')}
  ${w_form_end()}

${page_content_end()}
