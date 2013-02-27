window.settlers.refresh_donations_list = () ->
  new window.hlib.Ajax
    url:			'/admin/donations/list_full'
    handlers:
      h200:			(response, ajax) ->
        tmpl = doT.template '
          {{~ it.donations :donation:index}}
            <div class="mediumListIconTextItem">
              <div class="mediumListIconTextItem-Image icon-user"></div>
              <div class="mediumListIconTextItem-Detail">
                <h4>{{= donation.user.name}} - {{= donation.amount}} {{= window.hlib._g("_currency_")}}</h4>
                <div class="btn-toolbar">
                  <a class="btn" href="#" title="{{= window.hlib._g("Remove")}}" rel="tooltip" data-placement="right" id="donation_remove_{{= donation.user.name}}"><i class="icon-remove"></i></a>
                </div>
              </div>
            </div>
          {{~}}'

        $('#donations_list').html tmpl response

        __per_donation = (d) ->
          $('#donation_remove_' + d.user.name).click () ->
            new window.hlib.Ajax
              url:			'/admin/donations/remove'
              data:
                username:		d.user.name
              handlers:
                h200:			(response, ajax) ->
                  window.settlers.refresh_donations_list()
                  window.hlib.MESSAGE.hide()
            return false

        __per_donation d for d in response.donations

        window.hlib.MESSAGE.hide()

window.settlers.refresh_maintenance_access_list = () ->
  new window.hlib.Ajax
    url:		'/maintenance/granted'
    handlers:
      h200:		(response, ajax) ->
        tmpl = doT.template '
          {{~ it.users :user:index}}
            <div class="mediumListIconTextItem">
              <div class="mediumListIconTextItem-Image icon-user"></div>
              <div class="mediumListIconTextItem-Detail">
                <h4>{{= user.name}}</h4>
                <div class="btn-toolbar">
                  <a class="btn" href="#" title="{{= window.hlib._g("Remove")}}" rel="tooltip" data-placement="right" id="user_maintenance_access_revoke_{{= name}}"><i class="icon-remove"></i></a>
                </div>
              </div>
            </div>
          {{~}}'

        $('#maintenance_access_list').html tmpl response

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
        tmpl = doT.template '
          <h4>{{= window.hlib._g("Missing tokens")}}</h4>
          <ul class="i18n-missing-tokens">
            {{~ it.tokens :token:index}}
              <li>{{= token.name}}</li>
            {{~}}
          </ul>'

        (form_i18n_add.field 'missing').content(tmpl response).show()

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
    f.placeholder window.hlib._g 'Choose language first...'

  (form_i18n_add.field 'value').disable (f) ->
    f.placeholder window.hlib._g 'Choose language first...'

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
        tmpl = doT.template '
          <h4>{{= window.hlib._g("Unused tokens")}}</h4>
          <ul class="i18n-unused-tokens">
            {{~ it.tokens :token:index}}
              <li>{{= token.name}}</li>
            {{~}}
          </ul>'

        f.content(tmpl response).show()

  (form_i18n_edit.field 'unused').disable (f) ->
    f.empty().hide()

  # name
  (form_i18n_edit.field 'name').enable (f) ->
    window.settlers.refresh_token_list
      url:			'/admin/i18n/tokens'
      lang:			(form_i18n_edit.field 'lang').value()
      h200:			(response, ajax) ->
        tmpl = doT.template '
          <option value="">{{= window.hlib._g("Choose...")}}</option>
          {{~ it.tokens :token:index}}
            <option value="{{= token.name}}">{{= token.name}}</option>
          {{~}}'

        (form_i18n_edit.field 'name').content(tmpl response)
        window.hlib.MESSAGE.hide()

  (form_i18n_edit.field 'name').disable (f) ->
    f.placeholder window.hlib._g 'Choose language first...'

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
    f.empty().placeholder window.hlib._g 'Choose token first...'
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

  # Donations
  new window.hlib.Form
    fid:			'donations_add'
    clear_fields:		['username', 'amount']
    handlers:
      s200:			(response, form) ->
        window.settlers.refresh_donations_list()
        window.hlib.form_default_handlers.s200 response, form

  $('#donations_add_username').typeahead window.settlers.autocomplete_options()

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

$(window).bind 'page_startup', () ->
  window.settlers.setup_forms()
  window.settlers.refresh_donations_list()
  window.settlers.refresh_maintenance_access_list()
