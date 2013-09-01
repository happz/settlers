window.settlers.events['game.GameCreated']              = (e) ->
  window.hlib._g 'Game has been created'

window.settlers.events['game.GameFinished']             = (e) ->
  window.hlib._g 'Game has been finished'

window.settlers.events['game.GameArchived']             = (e) ->
  window.hlib._g 'Game has been archived'

window.settlers.events['game.GameCanceled']             = (e) ->
  if e.reason == 1
    return window.hlib._g 'Game has been canceled due to massive timeouts'

  if e.reason == 2
    return (window.hlib._g 'Game has been canceled due to missing {0}').format e.user.name

  if e.reason == 3
    return window.hlib._g 'Game has been canceled due to lack of interest'

  return 'game.GameCanceled'

window.settlers.events['game.GameStarted']              = (e) ->
  return window.hlib._g 'Game has started'

window.settlers.events['game.PlayerJoined']             = (e) ->
  return (window.hlib._g '{0} joined game').format e.user.name

window.settlers.events['game.ChatPost']                 = (e) ->
  return (window.hlib._g '{0} post new message on chat').format e.user.name

window.settlers.events['game.PlayerMissed']             = (e) ->
  return (window.hlib._g '{0} missed his turn').format e.user.name

window.settlers.events['game.Pass']                     = (e) ->
  return (window.hlib._g '{0} passed turn, next is {1}').format e.prev.name, e.next.name

window.settlers.events['game.PlayerInvited']            = (e) ->
  return (window.hlib._g '{0} has been invited to game').format e.user.name

window.settlers.events['game.CardUsed']                 = (e) ->
  return (window.hlib._g '{0} used card {1} from round {2}').format e.user.name, card = window.hlib._g(e.card.type), e.card.bought

window.settlers.events['game.CardBought']               = (e) ->
  return (window.hlib._g '{0} bought new card').format e.user.name

window.settlers.render_board_piece = (attrs) ->
  return '<span ' + ((attr_name + '="' + attr_value + '"' for own attr_name, attr_value of attrs).join ' ') + '></span>'
