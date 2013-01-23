$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:			'create'
    clear_fields:		['title', 'body']
    timeout:			30000
    handlers:
      s200:			(response, form) ->
        form.info.success 'Issue successfully reported, thank you.'

      s503:			(response, form) ->
        form.info.error 'Bohuzel, nelze pridat novou chybu. Zkuste to prosim pozdeji.'

      s401:			(response, form) ->
        form.info.error window.hlib.format_error response.error

  $('.accordion-body').collapse 'hide'
