window.settlers.setup_forms = () ->
  autocomplete_options = window.settlers.autocomplete_options()

  __setup_autocomplete = (eid) ->
    options = window.settlers.autocomplete_options()
    options.appendTo = $(eid).parent()

    $(eid).autocomplete options

  __setup_autocomplete '#new_game_opponent1'
  __setup_autocomplete '#new_game_opponent2'
  __setup_autocomplete '#new_game_opponent3'

  new window.hlib.Form
    fid:                'new_game'
    clear_fields:	['kind', 'name', 'limit', 'desc', 'password', 'opponent1', 'opponent2', 'opponent3', 'turn_limit', 'floating_desert']
    refill:		true
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly created'

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form

  $('#new_game_submit').click () ->
    $('#new_game_form').attr 'action', '/game/' + $('#new_game_kind').val() + '/new'
    return true

  new window.hlib.Form
    fid:                'new_tournament'
    clear_fields:	['engine', 'kind', 'name', 'num_players', 'limit', 'desc', 'password', 'turn_limit', 'floating_desert']
    refill:             true
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly created'

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form

window.settlers.setup_views = () ->
  $('#show_game').click () ->
    $('#views').tabs 'select', 0
    $('#show_game').hide()
    $('#show_tournament').show()

  $('#show_tournament').click () ->
    $('#views').tabs 'select', 1
    $('#show_tournament').hide()
    $('#show_game').show()

  $('#views').tabs()

  $('#views').tabs 'select', 0
  $('#show_game').hide()
  $('#show_tournament').show()

window.settlers.setup_page = () ->
  window.settlers.setup_forms()
  window.settlers.setup_views()
