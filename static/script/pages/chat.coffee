window.settlers.templates.chat_post = doT.template '
  <tr id="chat_post_{{= it.id}}">
    <td>
      <h3>
        <span class="chat-post-unread label label-important hide">Unread</span>
        {{? it.user.is_online}}
          <span class="user-online">
        {{?}}
        {{= it.user.name}}
        {{? it.user.is_online}}
          </span>
        {{?}} - {{= it.time}}
      </h3>

      <div>

        <p>{{= it.message}}</p>
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
