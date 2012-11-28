<%inherit file="page.mako" />

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

${ui_page_header('Settlers')}

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/loginas/loginas', id = 'loginas', legend = 'Admin login')}
    ${ui_input(form_name = 'username', type = 'text', label = 'Login name')}
    ${ui_input(form_name = 'password', type = 'password', label = 'Password')}
    ${ui_input(form_name = 'loginas', type = 'text', label = 'Login as')}
    ${ui_submit(value = 'Log in')}
  ${ui_form_end()}
${ui_row_end()}
