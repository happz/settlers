window.settlers.templates.chat_post = '
  <tr>
    <td></td>
    <td>{{user.name}}</td>
    <td>{{games}}</td>
    <td>{{wons}}</td>
    <td>{{points}}</td>
    <td>{{ppg}}</td>
  </tr>
'

window.settlers.setup_page = () ->
  pager = new window.hlib.Pager
    id_prefix:          'stats'
    url:                '/stats/page'
    template:           window.settlers.templates.chat_post
    eid:                '#stat_records'
    start:              0
    length:             20

  pager.refresh()
