window.settlers.setup_menu = () ->
  #  pn = new window.settlers.PullNotify

  $('#menu_logout').click () ->
    new window.hlib.Ajax
      url:              '/logout/'

    return false

window.settlers.setup_settlers = () ->
  if window.settlers.setup_menu
    window.settlers.setup_menu()

#  window.settlers.PULL_NOTIFY.update()

  return true
