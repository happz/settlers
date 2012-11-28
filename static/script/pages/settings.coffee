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
    if $('#' + eid + '_kind').val()
      window.hlib.Ajax
        url:			'/settings/unused_colors'
        data:
          kind:			$('#' + eid + '_kind').val()
        handlers:
          h200:			(response, ajax) ->
            c.label = window.hlib._g c.label for c in response.colors
            response._g = window.hlib._g
            $('#' + eid + '_color').html window.hlib.render '<option value="">{{#_g}}Choose...{{/_g}}</option>{{#colors}}<option value="{{name}}" class="colors" style="background-image: url(/static/images/games/settlers/board/real/players/{{name}}/node/village.gif)">{{label}}</option>{{/colors}}', response

            window.hlib.MESSAGE.hide()
      $('#' + eid + '_color').removeAttr 'disabled'

    else
      data =
        _g:			window.hlib._g

      $('#' + eid + '_color').html window.hlib.render '<option value="" selected="selected">{{#_g}}Choose game kind first...{{/_g}}</option>', data
      $('#' + eid + '_color').attr 'disabled', 'disabled'

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
  $('#color_kind').change () ->
    refresh_colors('color')

  new window.hlib.Form
    fid:			'color'
    clear_fields:		['color']
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly changed'

        $('#color_kind').val ''
        refresh_colors('color')

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form

  refresh_colors('color')

  # Opponent color
  refresh_opponent_colors_list = () ->
    v = $('#opponent_colors_kind').val()

    if v
      tmpl = '
        <div class="listview-container grid-layout">
          {{user}}
            <div class="mediumListIconTextItem" title="Click to remove">
              <img src="holder.js/60x60" class="mediumListIconTextItem-Image" />
              <div class="mediumListIconTextItem-Detail">
                <h4>{{user.name}}</h4>
              </div>
            </div>
          {{/user}}
        </div>'

      new window.hlib.Ajax
        url:			'/settings/opponents/opponents'
        data:
          kind:			v
        handlers:
          h200:			(response, ajax) ->
            if response.users.length <= 0
              $('#opponent_colors_list').html ''
              window.hlib.MESSAGE.hide()
              return

            $('#opponent_colors_list').html window.hlib.render tmpl, response

            __per_user = (u) ->
              $('#opponent_colors_remove_' + u.user.name).click () ->
                new window.hlib.Ajax
                  url:		'/settings/opponents/remove'
                  data:
                    kind:	$('#opponent_colors_kind').val()
                    username:	u.user.name
                  handlers:
                    h200:	(response, ajax) ->
                      refresh_colors('opponent_colors')
                      refresh_opponent_colors_list()

                      window.hlib.MESSAGE.hide()

            __per_user u for u in response.users
            window.hlib.MESSAGE.hide()

      $('#opponent_colors_username').removeAttr 'disabled'

    else
      tmpl = ''

      $('#opponent_colors_list').html window.hlib.render tmpl, {}
      $('#opponent_colors_username').attr 'disabled', 'disabled'
      $('#opponent_colors_username').val ''

  $('#opponent_colors_kind').change () ->
    refresh_colors('opponent_colors')
    refresh_opponent_colors_list()

  $('#opponent_colors_username').typeahead window.settlers.autocomplete_options()

  form = new window.hlib.Form
    fid:			'opponent_colors'
    clear_fields:		['color', 'username']
    handlers:
      s200:			(response, form) ->
        form.info.success 'Successfuly changed'

        $('#opponent_colors_kind').val ''
        refresh_colors('opponent_colors')
        refresh_opponent_colors_list()

  refresh_colors('color')
  refresh_opponent_colors_list()

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
