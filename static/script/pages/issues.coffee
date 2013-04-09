$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:			'create'
    clear_fields:		['title', 'body']
    timeout:			30000
    handlers:
      h200:			(response, form) ->
        form.info.success window.hlib._g 'Issue successfully reported, thank you.'

      h503:			(response, form) ->
        form.info.error window.hlib._g 'Bohuzel, nelze pridat novou chybu. Zkuste to prosim pozdeji.'

      h401:			(response, form) ->
        form.info.error window.hlib.format_error response.error

  $('.accordion-body').collapse 'hide'
