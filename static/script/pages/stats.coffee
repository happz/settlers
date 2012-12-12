window.settlers.templates.record = doT.template '
  <tr>
    <td>{{= it.user.name}}</td>
    <td>{{= it.games}}</td>
    <td>{{= it.wons}}</td>
    <td>{{= it.points}}</td>
    <td>{{= it.ppg}}</td>
    <td>{{= it.forhont}}</td>
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
