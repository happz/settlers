<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*" />
<%namespace file="lib.mako" import="*" />

${row_start()}
  ${w_form_start('/registration/recovery/recover', 'Password recovery', 'recovery')}
    ${w_form_input('username', 'text', 'Login name')}
    ${w_form_input('email', 'text', 'E-mail address')}
    ${w_submit_row('Create new password')}
  ${w_form_end()}
${row_end()}
