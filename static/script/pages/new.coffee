window.settlers.setup_forms = () ->
  __setup_autocomplete = (eid) ->
    options = window.settlers.autocomplete_options()

    $(eid).typeahead options

  __setup_autocomplete '#new_game_opponent1'
  __setup_autocomplete '#new_game_opponent2'
  __setup_autocomplete '#new_game_opponent3'

  new window.hlib.Form
    fid:                'new_game'
    clear_fields:	['kind', 'name', 'limit', 'desc', 'password', 'opponent1', 'opponent2', 'opponent3', 'floating_desert']
    refill:		true
    handlers:
      h200:     (response, form) ->
        form.info.success 'Successfuly created'

  $('#new_game_submit').click () ->
    $('#new_game_form').attr 'action', '/game/' + $('#new_game_kind').val() + '/new'
    return true

  new window.hlib.Form
    fid:                'new_tournament'
    clear_fields:	['engine', 'kind', 'name', 'num_players', 'limit', 'desc', 'password', 'turn_limit', 'floating_desert']
    refill:             true
    handlers:
      h200:     (response, form) ->
        form.info.success 'Successfuly created'

$(window).bind 'page_startup', () ->
  window.settlers.setup_forms()
