<%!
  import hlib
  import hruntime
%>

<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('Home')}

<div class="row-fluid">
  <div class="span12">

    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th>${_('Active')}</th>
          <th colspan="3">${_('Players')}</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="active"></tbody>

      <thead>
        <tr>
          <th>${_('Free')}</th>
          <th colspan="3">${_('Players')}</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="free"></tbody>

      <thead>
        <tr>
          <th>${_('Finished')}</th>
          <th colspan="3">${_('Players')}</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="finished"></tbody>
    </table>

  </div>
</div>
