window.settlers.setup_forms = () ->
  autocomplete_options =
    source:             '/users_by_name'
    minLength:          2

  $('#new_game_opponent1').autocomplete autocomplete_options
  $('#new_game_opponent2').autocomplete autocomplete_options
  $('#new_game_opponent3').autocomplete autocomplete_options

  new window.hlib.Form
    fid:                'new_game'
    clear_fields:	['kind', 'name', 'limit', 'desc', 'password', 'opponent1', 'opponent2', 'opponent3', 'turn_limit', 'floating_desert']
    refill:		true
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly created'

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form

  new window.hlib.Form
    fid:                'new_tournament'
    dont_clean:         true
    refill:             true
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly created'
      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form
        $(form.field_id 'limit').val ''

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

