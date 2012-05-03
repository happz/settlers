window.settlers.setup_menu = () ->
  #  pn = new window.settlers.PullNotify

  $('#menu_logout').click () ->
    new window.hlib.Ajax
      url:              '/logout/'
      handlers:
        h200:           (response, ajax) ->
          window.hlib.redirect '/login/'
          return false

window.settlers.setup_settlers = () ->
  if window.settlers.setup_menu
    window.settlers.setup_menu()

#  window.settlers.PULL_NOTIFY.update()

  return true
