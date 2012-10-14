window.settlers.templates.opponent_colors = {}
window.settlers.templates.opponent_colors.enabled = '
{{#colors}}
  <option class="colors" style="background-image: url(/static/images/games/settlers/board/real/players/{{name}}/node/village.gif)" value="{{name}}">{{name}}</option>
{{/colors}}
'
window.settlers.templates.opponent_colors.disabled = '
<option value="">Choose kind first</option>
'
window.settlers.templates.opponent_colors.list = '
  <ul class="opponent-colors-list">
    <li class="header">Opponent colors</li>
    {{#users}}
      <li class="info info-with-menu">
        <span class="">{{user.name}}</span>
        <span class="user-menu right">
          <span id="opponent_colors_remove_{{user.name}}" class="icon icon-medium icon-opponent-color-remove"></span>
        </span>
      </li>
    {{/users}}
  </ul>
'

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
  $("#opponent").autocomplete
    source: '/admin/ajax_users_by_name'
    minLength: 2

window.settlers.setup_opponent_colors_form = () ->
  form = new window.hlib.Form
    fid:                'opponent_colors'
    clear_fields:	['username']
    disable_fields:	['color']
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly changed'

        refresh_opponent_colors_colors()        
        refresh_opponent_colors_list()
        window.hlib.INFO._hide()

  kind = form.field 'kind'
  color = form.field 'color'
  list = form.field 'list'

  refresh_opponent_colors_colors = () ->
    new window.hlib.Ajax
      url:			'/settings/opponents/colors'
      data:
        kind:			$(kind.fid).val()
      handlers:
        h200:			(response, ajax) ->
          $(color.fid).html window.hlib.render window.settlers.templates.opponent_colors.enabled, response
          color.enable()

  refresh_opponent_colors_list = () ->
    new window.hlib.Ajax
      url:			'/settings/opponents/opponents'
      data:
        kind:			$(kind.fid).val()
      handlers:
        h200:			(response, ajax) ->
          if response.users.length <= 0
            list.empty()
            return

          $(list.fid).html window.hlib.render window.settlers.templates.opponent_colors.list, response

          __per_user = (u) ->
            f = form.field 'remove_' + u.user.name

            $(f.fid).click () ->
              new window.hlib.Ajax
                url:			'/settings/opponents/remove'
                data:
                  kind:			$(kind.fid).val()
                  username:		u.user.name
                handlers:
                  h200:			(response, ajax) ->
                    refresh_opponent_colors_colors()
                    refresh_opponent_colors_list()

                    window.hlib.INFO._hide()

          __per_user u for u in response.users

  $(kind.fid).change () ->
    if $(kind.fid).val() == ''
      $(color.fid).html window.hlib.render window.settlers.templates.opponent_colors.disabled

      color.empty()
      color.disable()
      list.empty()

      return

    refresh_opponent_colors_colors()
    refresh_opponent_colors_list()

    window.hlib.INFO._hide()

window.settlers.setup_forms = () ->
  new window.hlib.Form
    fid:			'password'
    clear_fields:		['password1', 'password2']
    handlers:
      s200:			(response, form) ->
        form.info.success 'Password successfuly changed'

  new window.hlib.Form
    fid:			'after_pass_turn'

  new window.hlib.Form
    fid:                'color'
    clear_fields:	['color']
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly changed'

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form

  new window.hlib.Form
    fid:                'per_page'

  new window.hlib.Form
    fid:                'board_skin'

  new window.hlib.Form
    fid:                'sound'

  window.settlers.setup_opponent_colors_form()

window.settlers.setup_page = () ->
  window.settlers.setup_datepickers()
  window.settlers.setup_autocomplete()
  window.settlers.setup_forms()
