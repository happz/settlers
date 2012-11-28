<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

<%namespace file="lib.mako" import="*" />

${ui_page_header('Settlers')}

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/registration/recovery/recover', legend = 'Password recovery', id = 'recovery')}
    ${ui_input(form_name = 'username', type = 'text', label = 'Login name')}
    ${ui_input(form_name = 'email', type = 'text', label = 'E-mail address')}
    ${ui_submit(value = 'Create new password')}
  ${ui_form_end()}
${ui_row_end()}
