window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:                        'recovery'
    focus:                      'username'
    clear_fields:		['username', 'email']
    handlers:
      s200:     (response, form) ->
        window.hlib.INFO.show 'Password recovery', 'New password was sent to your e-mail'
        window.hlib.redirect '/login/'
