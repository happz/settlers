$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:                        'checkin'
    focus:                      'username'
    refill:                     true
    clear_fields:		['username', 'password1', 'password2', 'email']
    handlers:
      h200:     (response, form) ->
        form.info.success 'New account created, you may log in', true

        redirect = () ->
          window.hlib.redirect '/login/'

        $('body').everyTime '15s', redirect
