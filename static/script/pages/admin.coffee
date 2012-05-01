window.settlers.templates = window.settlers.templates or {}
window.settlers.templates.i18n_tokens = '
  <option value="Vybrat...">Vybrat...</option>
  {{#tokens}}
    <option value="{{name}}">{{name}}</option>
  {{/tokens}}
'

window.settlers.refresh_token_list = () ->
  new window.hlib.Ajax
    url:		'/admin/i18n/tokens'
    data:
      lang:		$('#i18n_edit_lang').val()
    handlers:
      h200:		(response, ajax) ->
        $('#i18n_edit_token').html window.hlib.render window.settlers.templates.i18n_tokens, response
        $('#i18n_edit_token').val ''

window.settlers.setup_forms = () ->
  new window.hlib.Form
    fid:                'board'
    dont_clean:		true

  new window.hlib.Form
    fid:                'password_recovery_mail'
    dont_clean:		true

  i18n_edit = new window.hlib.Form
    fid:		'i18n_edit'
    dont_clean:		true

  new window.hlib.Form
    fid:		'i18n_add'
    dont_clean:		true
    handlers:
      s200:	(response, form) ->
        form.info.success 'Added'
        window.settlers.refresh_token_list()
        window.hlib.INFO._hide()

  $('#i18n_edit_lang').change () ->
    if $('#i18n_edit_lang').val() == ''
      return

    window.settlers.refresh_token_list()
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
          window.settlers.refresh_token_list()
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
