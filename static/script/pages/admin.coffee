window.settlers.templates = window.settlers.templates or {}
window.settlers.templates.i18n_unused_tokens = '
  <ul>
    {{#tokens}}
      <li>{{name}}</li>
    {{/tokens}}
  </ul>
'
window.settlers.templates.i18n_missing_tokens = '
  <ul>
    {{#tokens}}
      <li>{{name}}</li>
    {{/tokens}}
  </ul>
'
window.settlers.templates.i18n_tokens = '
  <option value="Vybrat...">Vybrat...</option>
  {{#tokens}}
    <option value="{{name}}">{{name}}</option>
  {{/tokens}}
'
window.settlers.templates.maintenance_access_list = '
  <ul class="maintenance-access-list">
    <li class="header">Users with granted access</li>
    {{#users}}
      <li class="info info-with-menu">
        <span class="">{{name}}</span>
        <span class="user-menu right">
          <span id="user_maintenance_access_revoke_{{name}}" class="icon icon-medium icon-maintenance-access-revoke"></span>
        </span>
      </li>
    {{/users}}
  </ul>
'

window.settlers.refresh_token_list = (opts) ->
  new window.hlib.Ajax
    url:		opts.url
    data:
      lang:		$(opts.lang).val()
    handlers:
      h200:		opts.h200

window.settlers.refresh_unused_list = () ->
  window.settlers.refresh_token_list
    url:		'/admin/i18n/unused'
    lang:		'#i18n_edit_lang'
    h200:		(response, ajax) ->
      $('#i18n_unused_tokens_list').html window.hlib.render window.settlers.templates.i18n_unused_tokens, response
      $('#i18n_unused_tokens').show()

window.settlers.refresh_missed_list = () ->
  window.settlers.refresh_token_list
    url:		'/admin/i18n/missing'
    lang:		'#i18n_add_lang'
    h200:               (response, ajax) ->
      $('#i18n_missing_tokens_list').html window.hlib.render window.settlers.templates.i18n_missing_tokens, response
      $('#i18n_missing_tokens').show()

window.settlers.refresh_present_list = () ->
  window.settlers.refresh_token_list
    url:		'/admin/i18n/tokens'
    lang:		'#i18n_edit_lang'
    h200:		(response, ajax) ->
      $('#i18n_edit_token').html window.hlib.render window.settlers.templates.i18n_tokens, response
      $('#i18n_edit_token').val ''

window.settlers.refresh_maintenance_access_list = () ->
  new window.hlib.Ajax
    url:		'/maintenance/granted_full'
    handlers:
      h200:		(response, ajax) ->
        $('#maintenance_access_list').html window.hlib.render window.settlers.templates.maintenance_access_list, response

        __per_user = (u) ->
          $('#user_maintenance_access_revoke_' + u.name).click () ->
            new window.hlib.Ajax
              url:			'/maintenance/revoke'
              data:
                username:		u.name
              handlers:
                h200:			(response, ajax) ->
                  window.settlers.refresh_maintenance_access_list()
                  window.hlib.INFO._hide()

        __per_user u for u in response.users

        window.hlib.INFO._hide()

window.settlers.setup_forms = () ->
  new window.hlib.Form
    fid:                'board'

  new window.hlib.Form
    fid:                'password_recovery_mail'

  i18n_edit = new window.hlib.Form
    fid:		'i18n_edit'
    clear_fields:	['token', 'value']

  new window.hlib.Form
    fid:		'i18n_add'
    clear_fields:	['name', 'value']
    handlers:
      s200:	(response, form) ->
        form.info.success 'Added'

        window.settlers.refresh_missed_list()
        window.hlib.INFO._hide()

  new window.hlib.Form
    fid:		'maintenance_mode'

  new window.hlib.Form
    fid:		'maintenance_access'
    clear_fields:	['username']
    handlers:
      s200:		(response, form) ->
        window.settlers.refresh_maintenance_access_list()
        window.hlib.form_default_handlers.s200 response, form

  $('#i18n_add_lang').change () ->
    if $('#i18n_add_lang').val() == ''
      $('#i18n_missing_tokens').hide()
      return

    window.settlers.refresh_missed_list()
    window.hlib.INFO._hide()

  $('#i18n_edit_lang').change () ->
    if $('#i18n_edit_lang').val() == ''
      $('#i18n_unused_tokens').hide()
      return

    window.settlers.refresh_unused_list()
    window.settlers.refresh_present_list()

    window.hlib.INFO._hide()

  $('#i18n_remove').click () ->
    new window.hlib.Ajax
      url:		'/admin/i18n/remove'
      data:
        lang:		$('#i18n_edit_lang').val()
        name:		$('#i18n_edit_token').val()
      handlers:
        h200:		(response, ajax) ->
          i18n_edit.info.success 'Removed'

          $('#i18n_edit').hide()
          window.settlers.refresh_unused_list()
          window.settlers.refresh_present_list()
          window.hlib.INFO._hide()

  $('#i18n_edit_token').change () ->
    if $('#i18n_edit_token').val() == ''
      return

    $('#i18n_edit').hide()
    $('#i18n_edit textarea').val ''
    
    new window.hlib.Ajax
      url:              '/admin/i18n/token'
      data:
        lang:		$('#i18n_edit_lang').val()
        name:		$('#i18n_edit_token').val()
      handlers:
        h200:		(response, ajax) ->
          $('#i18n_edit textarea').val response.value
          $('#i18n_edit').show()

          window.hlib.INFO._hide()

    return false

  $('#maintenance_access_username').autocomplete
    source:			'/maintenance/granted'
    minLength:			2

window.settlers.setup_page = () ->
  window.settlers.setup_forms()

  window.settlers.refresh_maintenance_access_list()
