window.settlers.check_status = () ->
  new window.hlib.Ajax
    url:			'/maintenance/state'
    handlers:
      h200:			(response, ajax) ->
        if response.enabled == false
          window.hlib.redirect '/login/'

        window.hlib.MESSAGE.hide()

$(window).bind 'page_startup', () ->
  new window.hlib.Form
    fid:                        'login'
    focus:                      'username'
    handlers:
      s200:			(response, form) ->
        window.hlib.redirect '/home/'
      s403:			(response, form) ->
        window.hlib.redirect '/vacation/'

  $('.container').everyTime '60s', window.settlers.check_status
