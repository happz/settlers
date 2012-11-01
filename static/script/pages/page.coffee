window.settlers.setup_menu = () ->
  #  pn = new window.settlers.PullNotify

  $('#menu_talk').click () ->
    window.settlers.TALK.show()
    return false

  $('#menu_logout').click () ->
    new window.hlib.Ajax
      url:              '/logout/'

    return false

  new window.hlib.Form
    fid:		'talk_add'
    clear_fields:	['text']
    handlers:
      s200:		(response, form) ->
        window.settlers.TALK.update()

window.settlers.setup_settlers = () ->
  if window.settlers.setup_menu
    window.settlers.setup_menu()

#  window.settlers.PULL_NOTIFY.update()

  return true
