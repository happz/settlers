window.settlers.templates = window.settlers.templates or {}
window.settlers.templates.i18n_unused_tokens = '
  <label>{{section_label}}</label>
  <ul class="i18n-unused-tokens">
    {{#tokens}}
      <label>{{name}}</label>
    {{/tokens}}
  </ul>
'
window.settlers.templates.i18n_missing_tokens = '
  <label>{{section_label}}</label>
  <ul class="i18n-missing-tokens">
    {{#tokens}}
      <label>{{name}}</label>
    {{/tokens}}
  </ul>
'
window.settlers.templates.i18n_tokens = '
  <option value="">Vybrat...</option>
  {{#tokens}}
    <option value="{{name}}">{{name}}</option>
  {{/tokens}}
'
window.settlers.templates.maintenance_access_list = '
  {{#users}}
    <div class="mediumListIconTextItem">
      <img src="holder.js/60x60" class="mediumListIconTextItem-Image" />
      <div class="mediumListIconTextItem-Detail">
        <h4>{{name}}</h4>
        <div class="btn-toolbar">
          <a class="btn" href="#" title="{{#_g}}Remove{{/_g}}" rel="tooltip" data-placement="right" id="user_maintenance_access_revoke_{{name}}"><i class="icon-remove"></i></a>
        </div>
      </div>
    </div>
  {{/users}}
'

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
                  window.hlib.MESSAGE.hide()
            return false

        __per_user u for u in response.users

        window.hlib.MESSAGE.hide()

window.settlers.refresh_token_list = (opts) ->
  new window.hlib.Ajax
    url:		opts.url
    data:
      lang:		opts.lang
    handlers:
      h200:		opts.h200

window.settlers.setup_i18n_edit_form = () ->
  form = new window.hlib.Form
    fid:		'i18n_edit'
    clear_fields:	['token', 'value']
    disable_fields:	['token']

  lang = form.field 'lang'
  unused = form.field 'unused'
  edit = form.field 'edit'
  token = form.field 'token'
  value = form.field 'value'
  remove = form.field 'remove'

  refresh_unused_list = () ->
    window.settlers.refresh_token_list
      url:		'/admin/i18n/unused'
      lang:		$(lang.fid).val()
      h200:		(response, ajax) ->
        response.section_label = window.hlib._g 'Unused tokens'
        $(unused.fid).html window.hlib.render window.settlers.templates.i18n_unused_tokens, response
        $(unused.fid).show()

  refresh_present_list = () ->
    window.settlers.refresh_token_list
      url:		'/admin/i18n/tokens'
      lang:		$(lang.fid).val()
      h200:		(response, ajax) ->
        $(token.fid).html window.hlib.render window.settlers.templates.i18n_tokens, response

  $(lang.fid).change () ->
    if $(lang.fid).val() == ''
      unused.empty()
      $(unused.fid).hide()

      value.empty()
      $(edit.fid).hide()

      tmpl_data =
        tokens:		[]

      $(token.fid).html window.hlib.render window.settlers.templates.i18n_tokens, tmpl_data
      token.disable()
      return

    token.enable()

    refresh_unused_list()
    refresh_present_list()

    window.hlib.MESSAGE.hide()

    return false

  $(token.fid).change () ->
    if $(token.fid).val() == ''
      value.empty()
      $(edit.fid).hide()
      return

    value.empty()
    $(edit.fid).hide()
    
    new window.hlib.Ajax
      url:              '/admin/i18n/token'
      data:
        lang:		$(lang.fid).val()
        name:		$(token.fid).val()
      handlers:
        h200:		(response, ajax) ->
          $(value.fid).val response.value
          $(edit.fid).show()

          window.hlib.MESSAGE.hide()

    return false

  $(remove.fid).click () ->
    new window.hlib.Ajax
      url:		'/admin/i18n/remove'
      data:
        lang:		$(lang.fid).val()
        name:		$(token.fid).val()
      handlers:
        h200:		(response, ajax) ->
          form.info.success 'Removed'

          value.empty()
          $(edit.fid).hide()

          refresh_unused_list()
          refresh_present_list()

          window.hlib.MESSAGE.hide()

    return false

window.settlers.setup_i18n_add_form = () ->
  form = new window.hlib.Form
    fid:		'i18n_add'
    clear_fields:	['name', 'value']
    handlers:
      s200:	(response, form) ->
        form.info.success 'Added'

        refresh_missed_list()
        window.hlib.MESSAGE.hide()

  lang = form.field 'lang'
  missing = form.field 'missing'

  refresh_missed_list = () ->
    window.settlers.refresh_token_list
      url:		'/admin/i18n/missing'
      lang:		$(lang.fid).val()
      h200:               (response, ajax) ->
        response.section_label = window.hlib._g 'Missing tokens'
        $(missing.fid).html window.hlib.render window.settlers.templates.i18n_missing_tokens, response
        $(missing.fid).show()

  $(lang.fid).change () ->
    if $(lang.fid).val() == ''
      missing.empty()
      $(missing.fid).hide()
      return

    refresh_missed_list()

    window.hlib.MESSAGE.hide()

    return false

window.settlers.setup_forms = () ->

  new window.hlib.Form
    fid:                'board'

  new window.hlib.Form
    fid:                'password_recovery_mail'

  new window.hlib.Form
    fid:		'maintenance_mode'

  $('#maintenance_access_username').typeahead window.settlers.autocomplete_options()

  new window.hlib.Form
    fid:		'maintenance_access'
    clear_fields:	['username']
    handlers:
      s200:		(response, form) ->
        window.settlers.refresh_maintenance_access_list()
        window.hlib.form_default_handlers.s200 response, form

  window.settlers.setup_i18n_add_form()
  window.settlers.setup_i18n_edit_form()

window.settlers.setup_page = () ->
  window.settlers.setup_forms()

  window.settlers.refresh_maintenance_access_list()

  $('#test_error').click () ->
    window.hlib.WORKING.show()
    false
