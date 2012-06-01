<%!
  import lib.trumpet

  import hlib
  import hruntime
%>

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${row_start()}
${w_form_start('/admin/trumpet/change_board', 'Change board', 'board')}
  ${w_form_text('text', label = 'Text', default = lib.trumpet.Board().text)}
  ${w_submit_row('Set')}
${w_form_end()}
${row_end()}

${row_start()}
${w_form_start('/admin/trumpet/change_password_recovery_mail', 'Change "Password recovery" mail', 'password_recovery_mail')}
  ${w_form_input('subject', 'text', label = 'Subject', default = lib.trumpet.PasswordRecoveryMail().subject)}
  ${w_form_text('text', label = 'Text', default = lib.trumpet.PasswordRecoveryMail().text)}
  ${w_submit_row('Set')}
${w_form_end()}
${row_end()}

${row_start()}
${w_form_start('/admin/i18n/add', 'Add token', 'i18n_add')}
  ${w_form_select('lang', label = 'Language')}
    % for key in hruntime.dbroot.localization.languages.iterkeys():
      ${w_option(key, False, key)}
    % endfor
  </select></div>

  <div class="grid-12-12 hide" id="i18n_missing_tokens">
    <label>${_('Missing tokens')}</label>
    <div id="i18n_missing_tokens_list" class="i18n-missing-tokens">
    </div>
  </div>

  ${w_form_input('name', 'text', label = 'Name')}
  ${w_form_input('value', 'text', label = 'Value')}
  ${w_submit_row('Add')}
${w_form_end()}
${row_end()}

${row_start()}
${w_form_start('/admin/i18n/token', 'Edit tokens', 'i18n_edit')}
  ${w_form_select('lang', label = 'Language')}
    % for key in hruntime.dbroot.localization.languages.iterkeys():
      ${w_option(key, False, key)}
    % endfor
  </select></div>

  <div class="grid-12-12 hide" id="i18n_unused_tokens">
    <label>${_('Unused tokens')}</label>
    <div id="i18n_unused_tokens_list" class="i18n-unused-tokens">
    </div>
  </div>

  ${w_form_select('token')}
    % for key in hruntime.i18n.tokens.iterkeys():
      ${w_option(key.replace('"', r'\"'), False, key)}
    % endfor
  </select></div>

  <div id="i18n_edit" class="hide">
    <div class="grid-11-12">
      ${w_form_text('value', struct = False)}
    </div>
    <div class="grid-1-12">
      <span class="icon icon-medium icon-i18n-remove-token" title="${_('Remove token')}" id="i18n_remove"></span>
    </div>
    ${w_submit_row('Change')}
  </div>
${w_form_end()}
${row_end()}

${row_start()}
  ${w_form_start('/maintenance/mode', 'Maintenance mode', 'maintenance_mode')}
    ${w_form_select('mode', label = 'Maintenance mode is', default = False)}
      ${w_option('1', hruntime.dbroot.server.maintenance_mode == True, 'Enabled')}
      ${w_option('0', hruntime.dbroot.server.maintenance_mode != True, 'Disabled')}
    </select></div>
    ${w_submit_row('Set')}
  ${w_form_end()}
${row_end()}

${row_start()}
  ${w_form_start('/maintenance/grant', 'Grant maintenance access', 'maintenance_access')}
    ${w_form_input('username', 'text', label = 'Username')}
    ${w_submit_row('Grant')}
  ${w_form_end()}
${row_end()}

${row_start()}
<div class="grid-12-12" id="maintenance_access_list">
</div>
${row_end()}
