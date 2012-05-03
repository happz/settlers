<%!
  import games.settlers.stats
%>

<%inherit file="page.mako" />

<%def name="page_script()">
  ${parent.page_script()}

window.settlers.setup_datatable = () ->
  dt_options = window.settlers.dt_options 'stats_settlers'

  dt_options.sAjaxSource = '/stats/lister'
  dt_options.iDisplayLength = ${user.table_length}
  dt_options.fnDrawCallback = (oSettings) ->
    if $('#stats_settlers').find('td:.dataTables_empty').length != 1
      window.hlib.recalc_row_numbers (oSettings)

  dt_options.aoColumns = [
    {
      bSearchable:	false
      bVisible:		true
      bSortable:	false
    }
    null
    null
    null
    null
    null
  ]

  dt_options.oLanguage.sInfoEmpty	= "${_('There are no stats to display')}"
  dt_options.oLanguage.sZeroRecords	= "${_('No records to display')}"
  dt_options.oLanguage.sProcessing	= "${_('Processing...')}"
  dt_options.oLanguage.sEmptyTable	= "${_('There are no stats to display')}"

  dt = $('#stats_settlers').dataTable dt_options

  window.settlers.dt_migrate_controls()

window.settlers.setup_page = () ->
  window.settlers.setup_datatable()

</%def>

<div class="span-3" id="dt_info"></div>
<div class="span-8 append-3 last centered" id="dt_pagination_top"></div>

<div class="span-14 prepend-top">
  <table class="list" id="stats_settlers">
    <thead>
      <tr id="header_row">
        <th></th>
        <th>${_('Name')}</th>
        <th>${_('Total games')}</th>
        <th>${_('Won games')}</th>
        <th>${_('Total points')}</th>
        <th>${_('Points per game')}</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>

<div class="span-3" id="dt_filter">&nbsp;</div>
<div class="span-8 append-3 last centered" id="dt_pagination_bottom"></div>
