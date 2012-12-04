window.settlers.setup_datepickers = () ->
  options =
    dateFormat: 'dd.mm.yy'
    buttonImage:        '/static/images/calendar.gif'
    buttonText:         window.hlib._g 'Choose'
    changeMonth:		true
    closeText:			window.hlib._g 'Set'
    nextText:			window.hlib._g 'Next'
    prevText:			window.hlib._g 'Previous'
    showButtonPanel:    true
    showOn:             'both'
    showOtherMonths:    true
    changeYear: true
    yearRange:  '-0:+1'

  $('#vacation_from_day').datepicker options
  $('#vacation_to_day').datepicker options

window.settlers.setup_autocomplete = () ->
  $("#opponent").autocomplete window.settlers.autocomplete_options()

window.settlers.setup_opponent_colors_form = () ->

window.settlers.setup_forms = () ->
  refresh_colors = (eid) ->

  # Password
  new window.hlib.Form
    fid:			'password'
    clear_fields:		['password1', 'password2']
    handlers:
      s200:			(response, form) ->
        form.info.success 'Password successfuly changed'

  # After "Pass turn"
  new window.hlib.Form
    fid:			'after_pass_turn'

  # Color
  form_color = new window.hlib.Form
    fid:			'color'
    clear_fields:		['kind', 'color']
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly changed'

        (form.field 'color').disable()

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form

  (form_color.field 'color').enable (f) ->
    window.hlib.Ajax
      url:			'/settings/unused_colors'
      data:
        kind:			(form_color.field 'kind').value()
      handlers:
        h200:			(response, ajax) ->
          c.label = window.hlib._g c.label for c in response.colors
          response._g = window.hlib._g

          f.content(window.hlib.render '<option value="">{{#_g}}Choose...{{/_g}}</option>{{#colors}}<option value="{{name}}" class="colors" style="background-image: url(/static/images/games/settlers/board/real/players/{{name}}/node/village.gif)">{{label}}</option>{{/colors}}', response)

          window.hlib.MESSAGE.hide()

  (form_color.field 'color').disable (f) ->
    f.placeholder 'Choose game kind first...'
    (form_color.field 'submit').disable()

  $((form_color.field 'kind').fid).change () ->
    if (form_color.field 'kind').value()
      (form_color.field 'color').enable()
    else
      (form_color.field 'color').disable()

  $((form_color.field 'color').fid).change () ->
    if (form_color.field 'color').value()
      (form_color.field 'submit').enable()
    else
      (form_color.field 'submit').disable()

  # Opponent color
  form_opponent_color = new window.hlib.Form
    fid:			'opponent_colors'
    clear_fields:		['color', 'username']
    handlers:
      s200:			(response, form) ->
        form.info.success 'Successfuly changed'

        (form.field 'color').on_enable(form_opponent_color.field 'color')
        (form.field 'list').on_enable(form_opponent_color.field 'list')

  # color
  (form_opponent_color.field 'color').enable (f) ->
    window.hlib.Ajax
      url:			'/settings/unused_colors'
      data:
        kind:			(form_opponent_color.field 'kind').value()
      handlers:
        h200:			(response, ajax) ->
          c.label = window.hlib._g c.label for c in response.colors
          response._g = window.hlib._g

          f.content(window.hlib.render '<option value="">{{#_g}}Choose...{{/_g}}</option>{{#colors}}<option value="{{name}}" class="colors" style="background-image: url(/static/images/games/settlers/board/real/players/{{name}}/node/village.gif)">{{label}}</option>{{/colors}}', response)

          window.hlib.MESSAGE.hide()

  (form_opponent_color.field 'color').disable (f) ->
    f.placeholder 'Choose game kind first...'

  # list
  (form_opponent_color.field 'list').enable (f) ->
    tmpl = '
      <div class="listview-container grid-layout">
        {{#users}}
          <div class="mediumListIconTextItem" title="Click to remove" id="opponent_{{user.name}}">
            <img class="mediumListIconTextItem-Image" style="background-color: {{color.color}}"/>
            <div class="mediumListIconTextItem-Detail">
              <h4>{{user.name}}</h4>
            </div>
          </div>
        {{/users}}
      </div>'

    new window.hlib.Ajax
      url:			'/settings/opponents/opponents'
      data:
        kind:			(form_opponent_color.field 'kind').value()
      handlers:
        h200:			(response, ajax) ->
          if response.users.length <= 0
            (form_opponent_color.field 'list').disable()
            window.hlib.MESSAGE.hide()
            return

          (form_opponent_color.field 'list').content(window.hlib.render tmpl, response).show()

          __per_user = (u) ->
            $('#opponent_' + u.user.name).click () ->
              new window.hlib.Ajax
                url:		'/settings/opponents/remove'
                data:
                  kind:		(form_opponent_color.field 'kind').value()
                  username:	u.user.name
                handlers:
                  h200:	(response, ajax) ->
                    (form_opponent_color.field 'color').on_enable(form_opponent_color.field 'color')
                    (form_opponent_color.field 'list').on_enable(form_opponent_color.field 'list')

                    window.hlib.MESSAGE.hide()

          __per_user u for u in response.users
          window.hlib.MESSAGE.hide()

  (form_opponent_color.field 'list').disable (f) ->
    (form_opponent_color.field 'list').empty().hide()

  $((form_opponent_color.field 'kind').fid).change () ->
    if (form_opponent_color.field 'kind').value()
      (form_opponent_color.field 'color').enable()
      (form_opponent_color.field 'username').enable()
      (form_opponent_color.field 'list').enable()
      (form_opponent_color.field 'submit').enable()

    else
      (form_opponent_color.field 'color').disable()
      (form_opponent_color.field 'username').disable()
      (form_opponent_color.field 'list').disable()
      (form_opponent_color.field 'submit').disable()

  $((form_opponent_color.field 'username').fid).typeahead window.settlers.autocomplete_options()

  # Email
  new window.hlib.Form
    fid:		'email'

  # Per page
  new window.hlib.Form
    fid:                'per_page'

  # Board skin
  new window.hlib.Form
    fid:                'board_skin'

  # Sound
  new window.hlib.Form
    fid:                'sound'

  # API Token
  new window.hlib.Form
    fid:		'api_token'

  $('#api_token_new').click () ->
    new window.hlib.Ajax
      url:			'/settings/api_token/new'
      handlers:
        h200:			(response, ajax) ->
          if response.hasOwnProperty 'token'
            $('#api_token_token').html response.token

          window.hlib.MESSAGE.hide()
    return false

  $('#api_token_download').click () ->
    $('#api_token_downloader').attr 'src', '/settings/api_token/download'
    return false

  window.settlers.setup_opponent_colors_form()

window.settlers.setup_page = () ->
  window.settlers.setup_datepickers()
  window.settlers.setup_autocomplete()
  window.settlers.setup_forms()
