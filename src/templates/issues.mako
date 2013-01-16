<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('New issue')}

<div class="row-fluid">
  <div class="offset2 span10">
    ${ui_form_start(action = '/issues/create', id = 'create', legend = 'Report new issue')}
      <!-- Title -->
      ${ui_input(type = 'text', label = 'Title', form_name = 'title')}

      <!-- Body -->
      ${ui_textarea(form_name = 'body', size = 'xxlarge', label = 'Description')}

      ${ui_submit(value = 'Report')}
    ${ui_form_end()}
  </div>
</div>
