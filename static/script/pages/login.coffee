$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:			'login'
    focus:			'username'
    clear_fields:		['username', 'password']
    handlers:
      s401:			(response, form) ->
        form.info.error window.hlib.format_error response.error

  new window.hlib.Form
    fid:			'check'
    clear_fields:		'username'
    handlers:
      s200:			(response, form) ->
        form.info.success window.hlib._g 'Yahoo! Your username has been transfered to betatest version, you may log in and have fun.'

      s403:			(response, form) ->
        form.info.error window.hlib._g 'We are sorry, your username has not been transfered to betatest version. Please register first.'
