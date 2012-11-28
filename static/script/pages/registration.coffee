window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:                        'checkin'
    focus:                      'username'
    refill:                     true
    clear_fields:		['username', 'password1', 'password2', 'email']
    handlers:
      s200:     (response, form) ->
        window.hlib.INFO.show 'Registration', 'New account created, you may log in'
        window.hlib.redirect '/login/'
