window.settlers.templates.colors = {}
window.settlers.templates.colors.list = ''

window.settlers.setup_datepickers = () ->
  options =
    dateFormat: 'dd.mm.yy'
    buttonImage:        '/static/images/calendar.gif'
    buttonText:         window.hlib._g 'Choose'
    changeMonth:		true
    closeText:			window.hlib._g 'Set'
    nextText:			window.hlib._g 'Next'
    prevText:			window.hlib._g 'Prev'
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

window.settlers.setup_forms = () ->
  new window.hlib.Form
    fid:        'password'
    handlers:
      s200:     (response, form) ->
        form.info.success 'Password successfuly changed'

  new window.hlib.Form
    fid:        'after_pass_turn'
    dont_clean: true

  new window.hlib.Form
    fid:                'color'
    dont_clean:         true
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly changed'
        $(form.field_id 'color').val ''

      s400:     (response, form) ->
        window.hlib.form_default_handlers.s400 response, form
        $(form.field_id 'color').val ''

  new window.hlib.Form
    fid:                'opponent_colors'
    handlers:
      s200:     (response, form) ->
        form.info.success 'Successfuly changed'
        

  new window.hlib.Form
    fid:                'table_length'
    dont_clean:         true

  new window.hlib.Form
    fid:                'board_skin'
    dont_clean:         true

  new window.hlib.Form
    fid:                'sound'
    dont_clean:         true

window.settlers.setup_page = () ->
  window.settlers.setup_datepickers()
  window.settlers.setup_autocomplete()
  window.settlers.setup_forms()
