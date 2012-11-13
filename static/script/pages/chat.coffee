window.settlers.templates.chat_post = '
  <tr>
    <td>
      <fieldset id="chat_post_{{id}}" class="chat-post">
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
  chat_pager = window.settlers.setup_chat
    id_prefix:			'chat'
    eid:			'#chat_posts'
    url:			'/chat/page'

  window.settlers.setup_chat_form
    eid:			'#chat_post'
    handlers:
      h200:		() ->
        chat_pager.refresh()
