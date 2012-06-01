window.settlers.check_status = () ->
  new window.hlib.Ajax
    url:			'/maintenance/state'
    handlers:
      h200:			(response, ajax) ->
        if response.enabled == false
          window.hlib.redirect '/login/'

        window.hlib.INFO._hide()

window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:                        'login'
    focus:                      'username'
    handlers:
      s200:			(response, form) ->
        window.hlib.redirect '/home/'
      s403:			(response, form) ->
        window.hlib.redirect '/vacation/'

  $('.container').everyTime '60s', window.settlers.check_status
