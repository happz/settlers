<%!
  import hruntime
%>

<%inherit file="page.mako" />

<%namespace file="hlib_ui.mako" import="*" />

${ui_page_header('About')}

<div class="row-fluid">
  <div class="offset2 span10">
    ${ui_section_header('about', 'About')}
    </section>
  </div>
</div>

<div class="row-fluid">
  <div class="offset2 span10">
    ${ui_section_header('donations', 'Donations')}
      <h4>${_('People who supported this web by donation')}</h4>
      <div>
        <table class="table table-striped" style="width: 30%">
          % for donor, amount in hruntime.dbroot.donors:
            <tr>
              <td>${donor.name}</td>
              <td>${amount} ${_('_currency_')}</td>
            </tr>
          % endfor
        </table>
      </div>
    </section>
  </div>
</div>
