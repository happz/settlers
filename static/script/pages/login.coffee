$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:			'login'
    focus:			'username'
    clear_fields:		['username', 'password']
    handlers:
      s401:			(response, form) ->
        form.info.error window.hlib.format_error response.error
