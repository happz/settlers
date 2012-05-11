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

window.settlers.setup_page = () ->
  window.settlers.setup_forms()
