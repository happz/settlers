window.settlers ?= {}

$(window).bind 'hlib_startup', () ->
  window.settlers.info = null

  if not window.settlers.user
    return

  if window.settlers.user.name != 'happz'
    return

  window.settlers.intro = introJs()

  window.settlers.intro.onchange () ->
    $('html').animate({scrollTop: 0}, 'slow')
    $('body').animate({scrollTop: 0}, 'slow')

  window.settlers.intro.setOptions
    skipLabel: window.hlib._g 'Skip'
    nextLabel: window.hlib._g('Next') + ' &rarr;'
    prevLabel: '&larr; ' + window.hlib._g('Prev')

