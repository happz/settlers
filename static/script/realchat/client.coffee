window.settlers.realchat ?= {}

class window.settlers.realchat.Chat
  message_badge_info: (msg) ->
    '' + msg.hours + ':' + msg.minutes + ' ' + msg.author

  constructor: (opts) ->
    window.WebSocket = window.WebSocket || window.MozWebSocket

    if not window.WebSocket
      $('#menu_realchat').hide()
      return

    _chat = @

    @content = $('#realchat_content')
    @input = $('#realchat_input')
    @status = $('#realchat_status')

    @color = window.settlers.user.color
    @nick = window.settlers.user.name

    @connection = new window.WebSocket 'ws://osadnici.happz.cz:1337/'

    @connection.onopen = () ->
      _chat.connection.send window.settlers.user.name
      return

    @connection.onerror = (error) ->
      return

    @connection.onmessage = (message) ->
      try
        message = JSON.parse message.data
      catch e
        return

      if message.type == 'ping'
        # ignore

      else if message.type == 'history'
        _chat.add_message m for m in message.data
        if message.data.length > 0
          window.settlers.show_menu_alert('menu_realchat', _chat.message_badge_info message.data.last())

      else if message.type == 'message'
        _chat.input.removeAttr 'disabled'
        _chat.add_message message.data
        window.settlers.show_menu_alert('menu_realchat', _chat.message_badge_info message.data)

    @input.keydown (e) ->
      if e.keyCode != 13
        return

      msg = $(@).val()
      if not msg
        return

      _chat.connection.send msg
      $(@).val ''
      _chat.input.attr 'disabled', 'disabled'

  add_message: (msg) ->
    if msg.author and msg.author == @nick
      msg.color = @color
    else
      msg.color = '#000000'

    stamp = new Date msg.time

    msg.hours = stamp.getHours()
    if msg.hours < 10
      msg.hours = '0' + msg.hours

    msg.minutes = stamp.getMinutes()
    if msg.minutes < 10
      msg.minutes = '0' + msg.minutes

    msg_template = doT.template '
      <p>
        {{= it.hours}}:{{= it.minutes}} <span style="color: {{= it.color}}">{{= it.author}}</span>: {{= it.text}}
      </p>'

    $('#realchat_dialog .modal-body ul').prepend msg_template msg

