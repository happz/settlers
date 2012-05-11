window.settlers.setup_page = () ->
  new window.hlib.Form
    fid:			'login'
    focus:			'username'
    handlers:
      s200:	() ->
        window.hlib.redirect '/home/'

      s403:	() ->
        window.hlib.redirect '/vacation/'
