$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:                        'recovery'
    focus:                      'username'
    clear_fields:		['username', 'email']
    handlers:
      h200:			(response, form) ->
        form.info.success 'New password was sent to your e-mail', true

        redirect = () ->
          window.hlib.redirect '/login/'

        $('body').everyTime '15s', redirect
