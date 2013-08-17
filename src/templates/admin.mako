<%!
  import lib.trumpet

  import hlib
  import hruntime
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('Administration')}

<div class="row-fluid">
  <div class="offset2 span10">

<!-- "Trumpet" section -->
${ui_section_header('trumpet', 'Trumpet')}

  <!-- Change board -->
  ${ui_form_start(action = '/admin/trumpet/change_board', legend = 'Change board', id = 'board')}
    ${ui_textarea(form_name = 'text', label = 'Text', value = lib.trumpet.Board().text, size = 'xxlarge')}

    <div class="control-group">
      <div class="hide board-preview offset1 span7" id="preview">
      </div>
    </div>

    <div class="control-group">
      <div class="controls">
        <input class="btn" type="submit" value="${_('Set')}">
        <input class="btn btn-info btn-preview" type="button" value="${_('Preview')}">
      </div>
    </div>
  ${ui_form_end()}

  <!-- Change password recovery mail -->
  ${ui_form_start(action = '/admin/trumpet/change_password_recovery_mail', legend = 'Change "Password recovery" mail', id = 'password_recovery_mail')}
    ${ui_input(form_name = 'subject', type = 'text', label = 'Subject', value = lib.trumpet.PasswordRecoveryMail().subject, size = 'xxlarge')}
    ${ui_textarea(form_name = 'text', label = 'Text', value = lib.trumpet.PasswordRecoveryMail().text, size = 'xxlarge')}
    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

</section>

<!-- "Language" section -->
${ui_section_header('language', 'Language')}

  <!-- Add token -->
  ${ui_form_start(action = '/admin/i18n/add', legend = 'Add token', id = 'i18n_add')}

    <!-- Language -->
    ${ui_select_start(form_name = 'lang', label = 'Language', default = 'Choose...')}
      % for key in hruntime.dbroot.localization.languages.keys():
        ${ui_select_option(value = key, selected = False, label = str(key))}
      % endfor
    ${ui_select_end()}

    <div class="hide" id="i18n_add_missing"></div>

    ${ui_input(form_name = 'name', type = 'text', label = 'Name', disabled = True, placeholder = _('Choose language first...'))}
    ${ui_input(form_name = 'value', type = 'text', label = 'Value', disabled = True, placeholder = _('Choose language first...'))}

    ${ui_submit(value = 'Add', id = 'i18n_add_submit', disabled = True)}
  ${ui_form_end()}

  <!-- Edit token -->
  ${ui_form_start(action = '/admin/i18n/edit', legend = 'Edit tokens', id = 'i18n_edit')}
    ${ui_select_start(form_name = 'lang', label = 'Language', default = 'Choose...')}
      % for key in hruntime.dbroot.localization.languages.keys():
        ${ui_select_option(value = key, selected = False, label = key)}
      % endfor
    ${ui_select_end()}

    <div id="i18n_edit_unused"></div>

    ${ui_select_start(form_name = 'name', label = 'Token', disabled = True, placeholder = _('Choose language first...'))}
      <option value="" disabled="disabled">Choose language first...</option>
    ${ui_select_end()}

    ${ui_textarea(form_name = 'value', size = 'xxlarge', disabled = True, placeholder = _('Choose language first...'))}

    <div class="control-group">
      <div class="controls">
        <input id="i18n_edit_submit" class="btn" type="submit" value="Upravit">
        <button id="i18n_edit_remove" class="btn btn-danger hide" disabled="disabled">${_('Remove token')}</button>
      </div>
    </div>
  ${ui_form_end()}

</section>

<!-- "Donations" section -->
${ui_section_header('donations', 'Donations')}
  <!-- Add donor -->
  ${ui_form_start(action = '/admin/donations/add', legend = 'Add donation', id = 'donations_add')}
    ${ui_input(form_name = 'username', type = 'text', label = 'Username')}
    ${ui_input(form_name = 'amount', type = 'text', label = 'Amount')}

    ${ui_submit(value = 'Add')}
  ${ui_form_end()}

  <div id="donations_list" class="listview grid-layout"></div>
</section>

<!-- "Maintenance" section -->
${ui_section_header('maintenance', 'Maintenance')}

  <!-- Change mode -->
  ${ui_form_start(action = '/maintenance/mode', legend = 'Maintenance mode', id = 'maintenance_mode')}
    ${ui_select_start(form_name = 'mode', label = 'Maintenance mode is', default = False)}
      ${ui_select_option(value = 1, selected = (hruntime.dbroot.server.maintenance_mode == True), label = 'Enabled')}
      ${ui_select_option(value = 0, selected = (hruntime.dbroot.server.maintenance_mode != True), label = 'Disabled')}
    ${ui_select_end()}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

  <!-- Grant access -->
  ${ui_form_start(action = '/maintenance/grant', legend = 'Grant maintenance access', id = 'maintenance_access')}
    ${ui_input(form_name = 'username', type = 'text', label = 'Username')}
    ${ui_submit(value = 'Grant')}
  ${ui_form_end()}

  <div id="maintenance_access_list" class="listview grid-layout"></div>

</section>

  </div>
</div>
