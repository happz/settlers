<%!
  import games.settlers.stats

  import hruntime
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('Stats')}

<div class="row-fluid">
  <div class="offset2 span10">

    ${ui_section_header('stats_settlers', 'Settlers stats')}
        <div id="stats_records">
          <div class="pagination pagination-right">
            <ul>
              <li><a href="#" class="stats-first">${_('First')}</a></li>
              <li><a href="#" class="stats-previous">${_('Previous')}</a></li>
              <li><a href="#" class="stats-position"></a></li>
              <li><a href="#" class="stats-next">${_('Next')}</a></li>
              <li><a href="#" class="stats-last">${_('Last')}</a></li>
            </ul>
          </div>

          <div>
            <table class="table table-bordered table-hover">
              <thead>
                <tr>
                  <th style="width: 25%;">${_('Name')}</th>
                  <th style="width: 15%;">${_('Total games')}</th>
                  <th style="width: 15%;">${_('Won games')}</th>
                  <th style="width: 15%;">${_('Finished games')}</th>
                  <th style="width: 15%;">${_('Points')}</th>
                  <th style="width: 15%;">${_('Points per game')}</th>
                </tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>

          <div class="pagination pagination-right">
            <ul>
              <li><a href="#" class="stats-first">${_('First')}</a></li>
              <li><a href="#" class="stats-previous">${_('Previous')}</a></li>
              <li><a href="#" class="stats-position"></a></li>
              <li><a href="#" class="stats-next">${_('Next')}</a></li>
              <li><a href="#" class="stats-last">${_('Last')}</a></li>
            </ul>
          </div>
        </div>
    </section>

    ${ui_section_header('server_stats', 'Server stats')}
      <div id="server_stats">
        <div>
          <table class="table table-bordered table-hover">
            <tbody>
              <tr>
                <td>${_('Active games')}</td>
                <td>${hruntime.dbroot.counters.games_active()}</td>
              </tr>
              <tr>
                <td>${_('Free games')}</td>
                <td>${hruntime.dbroot.counters.games_free()}</td>
              </tr>
              <tr>
                <td>${_('Inactive games')}</td>
                <td>${hruntime.dbroot.counters.games_inactive()}</td>
              </tr>
              <tr>
                <td>${_('Archived games')}</td>
                <td>${hruntime.dbroot.counters.games_archived()}</td>
              </tr>
              <tr>
                <td>${_('Total games')}</td>
                <td>${hruntime.dbroot.counters.games()}</td>
              </tr>
              <tr><td colspan="2"><hr /></td></tr>
              <tr>
                <td>${_('Active tournaments')}</td>
                <td>${hruntime.dbroot.counters.tournaments_active()}</td>
              </tr>
              <tr>
                <td>${_('Free tournaments')}</td>
                <td>${hruntime.dbroot.counters.tournaments_free()}</td>
              </tr>
              <tr>
                <td>${_('Inactive tournaments')}</td>
                <td>${hruntime.dbroot.counters.tournaments_inactive()}</td>
              </tr>
              <tr>
                <td>${_('Archived tournaments')}</td>
                <td>${hruntime.dbroot.counters.tournaments_archived()}</td>
              </tr>
              <tr>
                <td>${_('Total tournaments')}</td>
                <td>${hruntime.dbroot.counters.tournaments()}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

  </div>
</div>
