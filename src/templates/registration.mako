<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

<%namespace file="lib.mako" import="*" />

${ui_page_header('Settlers')}

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/registration/checkin', legend = 'New account', id = 'checkin')}
    ${ui_input(form_name = 'username', type = 'text', label = 'Login name', required = True)}
    ${ui_input(form_name = 'password1', type = 'password', label = 'Password', required = True)}
    ${ui_input(form_name = 'password2', type = 'password', label = 'Password verification', required = True)}
    ${ui_input(form_name = 'email', type = 'text', label = 'E-mail address')}
    ${ui_submit(value = 'Check in')}
  ${ui_form_end()}
${ui_row_end()}
