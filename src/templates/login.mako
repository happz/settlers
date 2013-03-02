<%!
  import hlib
%>

<%inherit file="page.mako" />

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

${ui_page_header('Settlers')}

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/login/login', id = 'login', legend = 'Game login', validate = True)}
    ${ui_input(type = 'text', label = 'Login name', form_name = 'username', placeholder = 'Pozor na velka/mala pismena', validators = 'required notblank rangelength="[2,30]"')}
    ${ui_input(type = 'password', label = 'Password', form_name = 'password', validators = 'required notblank rangelength="[2,256]"')}
    ${ui_submit(value = 'Log in')}
  ${ui_form_end()}
${ui_row_end()}

${ui_row_start(span = 6)}
  ${ui_form_start(action = '/login/check', id = 'check', legend = 'Username check', validate = True)}
    ${ui_input(type = 'text', label = 'Check if your accout exists', form_name = 'username',  validators = 'required notblank rangelength="[2,30]"')}
    ${ui_submit(value = 'Check')}
  ${ui_form_end()}
${ui_row_end()}
