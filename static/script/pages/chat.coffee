window.settlers.templates.chat_post = '
  <tr>
    <td>
      <fieldset class="chat-post">
        <legend>
          {{#user.is_online}}
            <span class="user-online">
          {{/user.is_online}}
          {{user.name}}
          {{#user.is_online}}
            </span>
          {{/user.is_online}} - {{time}}
        </legend>
        <div>{{{message}}}</div>
      </fieldset>
    </td>
  </tr>
'

window.settlers.setup_page = () ->
  window.settlers.setup_chat_form
    eid:			'#chat_post'

  window.settlers.setup_chat
    eid:			'#chat_posts'
    url:			'/chat/page'
    data:
      gid:			window.settlers.game.gid
