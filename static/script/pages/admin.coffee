window.settlers.templates = window.settlers.templates or {}
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

window.settlers.setup_i18n_add_form = () ->

window.settlers.setup_forms = () ->
  # Board
  new window.hlib.Form
    fid:                'board'

  # Password recovery mail
  new window.hlib.Form
    fid:                'password_recovery_mail'

  # I18N - add token
  refresh_missing_list = () ->
    window.settlers.refresh_token_list
      url:			'/admin/i18n/missing'
      lang:			(form_i18n_add.field 'lang').value()
      h200:			(response, ajax) ->
        tmpl = '<h4>{{section_label}}</h4><ul class="i18n-missing-tokens">{{#tokens}}<li>{{name}}</li>{{/tokens}}</ul>'
        response.section_label = window.hlib._g 'Missing tokens'

        (form_i18n_add.field 'missing').content(window.hlib.render tmpl, response).show()

        window.hlib.MESSAGE.hide()

  form_i18n_add = new window.hlib.Form
    fid:		'i18n_add'
    clear_fields:	['name', 'value']
    handlers:
      s200:	(response, form) ->
        form.info.success 'Added'

        refresh_missing_list()
        window.hlib.MESSAGE.hide()

  (form_i18n_add.field 'name').disable (f) ->
    f.placeholder 'Choose language first...'

  (form_i18n_add.field 'value').disable (f) ->
    f.placeholder 'Choose language first...'

  $((form_i18n_add.field 'lang').fid).change () ->
    if (form_i18n_add.field 'lang').value()
      (form_i18n_add.field 'name').enable()
      (form_i18n_add.field 'value').enable()
      (form_i18n_add.field 'submit').enable()

      refresh_missing_list()

    else
      (form_i18n_add.field 'name').disable()
      (form_i18n_add.field 'value').disable()
      (form_i18n_add.field 'submit').disable()
      (form_i18n_add.field 'missing').empty().hide()

    return false

  # I18N - edit tokens
  form_i18n_edit = new window.hlib.Form
    fid:			'i18n_edit'
    clear_fields:		['name', 'value']
    handlers:
      s200:			(response, form) ->
        window.hlib.form_default_handlers.s200 response, form
        (form_i18n_edit.field 'value').disable()

  # unused
  (form_i18n_edit.field 'unused').enable (f) ->
    window.settlers.refresh_token_list
      url:			'/admin/i18n/unused'
      lang:			(form_i18n_edit.field 'lang').value()
      h200:			(response, ajax) ->
        tmpl = '<h4>{{section_label}}</h4><ul class="i18n-unused-tokens">{{#tokens}}<li>{{name}}</li>{{/tokens}}</ul>'
        response.section_label = window.hlib._g 'Unused tokens'

        f.content(window.hlib.render tmpl, response).show()

  (form_i18n_edit.field 'unused').disable (f) ->
    f.empty().hide()

  # name
  (form_i18n_edit.field 'name').enable (f) ->
    window.settlers.refresh_token_list
      url:			'/admin/i18n/tokens'
      lang:			(form_i18n_edit.field 'lang').value()
      h200:			(response, ajax) ->
        tmpl = '<option value="">{{#_g}}Choose...{{/_g}}</option>{{#tokens}}<option value="{{name}}">{{name}}</option>{{/tokens}}'
        response._g = window.hlib._g

        (form_i18n_edit.field 'name').content(window.hlib.render tmpl, response)
        window.hlib.MESSAGE.hide()

  (form_i18n_edit.field 'name').disable (f) ->
    f.placeholder 'Choose language first...'

    (form_i18n_edit.field 'value').disable()

  # value
  (form_i18n_edit.field 'value').enable (f) ->
    new window.hlib.Ajax
      url:			'/admin/i18n/token'
      data:
        lang:			(form_i18n_edit.field 'lang').value()
        name:			(form_i18n_edit.field 'name').value()
      handlers:
        h200:			(response, ajax) ->
          f.value response.value
          (form_i18n_edit.field 'remove').show()
          (form_i18n_edit.field 'submit').enable()

          window.hlib.MESSAGE.hide()

  (form_i18n_edit.field 'value').disable (f) ->
    f.empty().placeholder('Choose token first...')
    (form_i18n_edit.field 'remove').hide()
    (form_i18n_edit.field 'submit').disable()

  # lang.change
  $((form_i18n_edit.field 'lang').fid).change () ->
    if (form_i18n_edit.field 'lang').value()
      (form_i18n_edit.field 'unused').enable()
      (form_i18n_edit.field 'name').enable()

    else
      (form_i18n_edit.field 'unused').disable()
      (form_i18n_edit.field 'name').disable()

    return false

  # token.change
  $((form_i18n_edit.field 'name').fid).change () ->
    if (form_i18n_edit.field 'name').value()
      (form_i18n_edit.field 'value').enable()

    else
      (form_i18n_edit.field 'value').disable()

    return false

  $((form_i18n_edit.field 'remove').fid).click () ->
    new window.hlib.Ajax
      url:			'/admin/i18n/remove'
      data:
        lang:		(form_i18n_edit.field 'lang').value()
        name:		(form_i18n_edit.field 'name').value()
      handlers:
        h200:		(response, ajax) ->
          form_i18n_edit.info.success 'Removed'

          (form_i18n_edit.field 'unused').on_enable (form_i18n_edit.field 'unused')
          (form_i18n_edit.field 'name').on_enable (form_i18n_edit.field 'name')
          (form_i18n_edit.field 'value').disable()

          window.hlib.MESSAGE.hide()

    return false

  # Maintenance mode
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
