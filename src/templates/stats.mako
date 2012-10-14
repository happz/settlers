<%!
  import games.settlers.stats
%>

<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${row_start(width = 10)}
  <div id="stat_records">
    <div class="span-10 last centered">
      <span class="stats-first">&lt;&lt;</span>
      <span class="stats-prev">&lt;</span>
      <span class="stats-position"></span>
      <span class="stats-next">&gt;</span>
      <span class="stats-last">&gt;&gt;</span>
    </div>

    <div class="span-10 prepend-top">
      <table>
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
        <tbody>
        </tbody>
      </table>
    </div>

    <div class="span-10 last centered">
      <span class="stats-first">&lt;&lt;</span>
      <span class="stats-prev">&lt;</span>
      <span class="stats-position"></span>
      <span class="stats-next">&gt;</span>
      <span class="stats-last">&gt;&gt;</span>
    </div>
  </div>
${row_end()}
