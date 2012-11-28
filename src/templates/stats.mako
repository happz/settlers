<%!
  import games.settlers.stats
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
                  <th>${_('Name')}</th>
                  <th>${_('Total games')}</th>
                  <th>${_('Won games')}</th>
                  <th>${_('Total points')}</th>
                  <th>${_('Points per game')}</th>
                  <th>${_('On turn')}</th>
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

  </div>
</div>
