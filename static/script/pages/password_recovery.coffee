window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:                        'recovery'
    focus:                      'username'
    clear_fields:		['username', 'email']
    handlers:
      s200:			(response, form) ->
        form.info.success 'New password was sent to your e-mail', true

        redirect = () ->
          window.hlib.redirect '/login/'

        $('body').everyTime '15s', redirect
