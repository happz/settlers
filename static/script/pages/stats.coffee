window.settlers.templates.record = doT.template '
  {{? it.user.name == window.settlers.user.name}}
    <tr class="info">
  {{??}}
    <tr>
  {{?}}
    <td>{{= window.settlers.fmt_player(it)}}</td>
    <td>{{= it.games}}</td>
    <td>{{= it.wons}}</td>
    <td>{{= it.finished}}</td>
    <td>{{= it.points}}</td>
    <td>{{= it.ppg.toFixed(3)}}</td>
  </tr>
'

$(window).bind 'page_startup', () ->
  pager = new window.hlib.Pager
    id_prefix:          'stats'
    url:                '/stats/'
    template:           window.settlers.templates.record
    eid:                '#stats_records'
    start:              0
    length:             20

  pager.refresh()
