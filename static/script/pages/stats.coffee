window.settlers.templates.record = doT.template '
  {{? it.user.name == window.settlers.user.name}}
    <tr class="info">
  {{??}}
    <tr>
  {{?}}
    <td>{{= it.user.name}}</td>
    <td>{{= it.games}}</td>
    <td>{{= it.wons}}</td>
    <td>{{= it.finished}}</td>
    <td>{{= it.points}}</td>
    <td>{{= it.ppg}}</td>
  </tr>
'

$(window).bind 'page_startup', () ->
  pager = new window.hlib.Pager
    id_prefix:          'stats'
    url:                '/stats/page'
    template:           window.settlers.templates.record
    eid:                '#stats_records'
    start:              0
    length:             20

  pager.refresh()
