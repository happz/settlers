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
      h200:			(response, form) ->
        form.info.success 'Password successfuly changed'

  # After "Pass turn"
  new window.hlib.Form
    fid:			'after_pass_turn'

  # Color
  form_color = new window.hlib.Form
    fid:			'color'
    clear_fields:		['kind', 'color']
    handlers:
      h200:     (response, form) ->
        form.info.success 'Successfuly changed'

        (form.field 'color').disable()

  (form_color.field 'color').enable (f) ->
    new window.hlib.Ajax
      url:			'/settings/unused_colors'
      data:
        kind:			(form_color.field 'kind').value()
      handlers:
        h200:			(response, ajax) ->
          c.label = window.hlib._g c.label for c in response.colors
          response._g = window.hlib._g

          tmpl = doT.template '
            <option value="">{{= window.hlib._g("Choose...")}}</option>
            {{~ it.colors :color:index}}
              <option value="{{= color.name}}" class="colors" style="background-image: url(/static/images/games/settlers/board/real/players/{{= color.name}}/node/village.gif)">{{= color.label}}</option>
            {{~}}'

          f.content tmpl response

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
  free_colors_count = null
  form_opponent_color = new window.hlib.Form
    fid:			'opponent_colors'
    clear_fields:		['color', 'username']
    handlers:
      h200:			(response, form) ->
        form.info.success 'Successfuly changed'

        (form.field 'color').on_enable(form_opponent_color.field 'color')
        (form.field 'list').on_enable(form_opponent_color.field 'list')

  # color
  (form_opponent_color.field 'color').enable (f) ->
    new window.hlib.Ajax
      url:			'/settings/unused_colors'
      data:
        kind:			(form_opponent_color.field 'kind').value()
      handlers:
        h200:			(response, ajax) ->
          free_colors_count = response.colors.length
          if free_colors_count <= 3
            (form_opponent_color.field 'color').disable()
            (form_opponent_color.field 'username').disable()
            (form_opponent_color.field 'submit').disable()

          else
            (form_opponent_color.field 'username').enable()
            (form_opponent_color.field 'submit').enable()

            c.label = window.hlib._g c.label for c in response.colors
            response._g = window.hlib._g

            tmpl = doT.template '
              <option value="">{{= window.hlib._g("Choose...")}}</option>
              {{~ it.colors :color:index}}
                <option value="{{= color.name}}" class="colors" style="background-image: url(/static/images/games/settlers/board/real/players/{{= color.name}}/node/village.gif)">{{= color.label}}</option>
              {{~}}'
            f.content tmpl response

          window.hlib.MESSAGE.hide()

  (form_opponent_color.field 'color').disable (f) ->
    if free_colors_count <= 3
      f.placeholder 'You have no free colors to use'
    else
      f.placeholder 'Choose game kind first...'

  # list
  (form_opponent_color.field 'list').enable (f) ->
    tmpl = doT.template '
      <div class="listview-container grid-layout">
        {{~ it.users :pair:index}}
          <div class="mediumListIconTextItem" title="Click to remove" id="opponent_{{= pair.user.name}}">
            <img class="mediumListIconTextItem-Image" style="background-color: {{= pair.color.color}}"/>
            <div class="mediumListIconTextItem-Detail">
              <h4>{{= pair.user.name}}</h4>
            </div>
          </div>
        {{~}}
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

          (form_opponent_color.field 'list').content(tmpl response).show()

          __per_user = (u) ->
            $('#opponent_' + u.user.name).click () ->
              new window.hlib.Ajax
                url:		'/settings/opponents/remove'
                data:
                  kind:		(form_opponent_color.field 'kind').value()
                  username:	u.user.name
                handlers:
                  h200:	(response, ajax) ->
                    (form_opponent_color.field 'color').enable()
                    #(form_opponent_color.field 'color').on_enable(form_opponent_color.field 'color')
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

  # Avatar
  avatar_form = new window.hlib.Form
    fid: 'avatar'
    clear_fields: ['filename']
    handlers:
      h200: (response, form) ->
        form.info.success 'Successfully changed'
        $('#avatar_preview').hide()
        $('#avatar_image').attr 'src', ('/static/images/avatars/' + window.settlers.user.avatar_name + '.jpg?_client_version_stamp=' + new Date().getTime())

  $('#avatar_filename').change () ->
    if avatar_form.last_invalid_field
      avatar_form.last_invalid_field.unmark_error()
      avatar_form.info._hide()

    file = window.settlers.parsley_validators.file = $('#avatar_filename')[0].files[0]
    if not file
      return

    reader = new FileReader()
    if not reader
      return

    reader.onload = (e) ->
      $('#avatar_preview img').remove()
      $('#avatar_preview div.controls').prepend '<img class="img-polaroid avatar-image" name="avatar_preview" src="" />'

      $('#avatar_preview img').load () ->
        $('#avatar_preview_valid').hide()
        $('#avatar_preview_invalid').hide()

        dummy_field =
          $element: $('#avatar_filename')

        if    not window.ParsleyConfig.validators.filedimensionsmax(null, '#avatar_preview img,160,160') \
           or not window.ParsleyConfig.validators.filedimensionsmin(null, '#avatar_preview img,160,160') \
           or not window.ParsleyConfig.validators.filesize(null, '1024000', dummy_field) \
           or not window.ParsleyConfig.validators.filetype(null, 'image/jpeg,image/png', dummy_field)
          $('#avatar_preview_invalid').show()
        else
          $('#avatar_preview_valid').show()

      $('#avatar_preview').show()
      $('#avatar_preview img').attr 'src', e.target.result

    reader.readAsDataURL file

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

$(window).bind 'page_startup', () ->
  window.settlers.setup_datepickers()
  window.settlers.setup_autocomplete()
  window.settlers.setup_forms()
