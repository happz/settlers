window.settlers.templates.chat_post = '
  <tr id="chat_post_{{id}}">
    <td>
      <h3>
        <span class="chat-post-unread label label-important hide">Unread</span>
        {{#user.is_online}}
          <span class="user-online">
        {{/user.is_online}}
        {{user.name}}
        {{#user.is_online}}
          </span>
        {{/user.is_online}} - {{time}}
      </h3>

      <div>

        <p>{{{message}}}</p>
      </div>
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
