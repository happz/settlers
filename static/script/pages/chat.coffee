window.settlers.templates.chat_post = doT.template '
  <tr id="chat_post_{{= it.id}}">
    <td>
      <h3>
        <span class="chat-post-unread label label-important hide">{{= window.hlib._g("Unread")}}</span>
        {{= window.settlers.fmt_player(it) }} - {{= it.time}}
        <a href="#" rel="tooltip" data-placement="right" title="{{= window.hlib._g(\'Quote\')}}" data-chat-post="{{= it.id}}">
          <span class="icon-comment-alt2-stroke"></span>
        </a>
      </h3>

      <div>
        <p>{{= it.message}}</p>
      </div>
    </td>
  </tr>
'

$(window).bind 'page_startup', () ->
  chat_preview = null

  chat_preview = window.settlers.setup_chat_form
    eid:      '#chat_post'
    handlers:
      h200:   () ->
        chat_pager.refresh()
        chat_preview.preview.hide()

  chat_pager = window.settlers.setup_chat
    id_prefix:			'chat'
    eid:			'#chat_posts'
    url:			'/chat/'
    editor_eid: '#chat_post_text'
    preview: chat_preview
