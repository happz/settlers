<%inherit file="page.mako" />

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

${ui_page_header('Settlers')}

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/loginas/loginas', id = 'loginas', legend = 'Admin login', validate = True)}
    ${ui_input(form_name = 'username', type = 'text', label = 'Login name', validators = 'required notblank rangelength="[2,30]"')}
    ${ui_input(form_name = 'password', type = 'password', label = 'Password', validators = 'required notblank rangelength="[2,256]"')}
    ${ui_input(form_name = 'loginas', type = 'text', label = 'Login as', validators = 'required notblank rangelength="[2,30]"')}
    ${ui_submit(value = 'Log in')}
  ${ui_form_end()}
${ui_row_end()}
