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

<div class="row-fluid">
  <div class="offset2 span10">
    <div class="accordion" id="accordion">
      % for issue in repository.get_issues():
        <div class="accordion-group">
          <div class="accordion-heading">
            <a class="accordion-toggle" data-toggle="collapse" href="#ticket${issue.number}">${issue.title}</a>
          </div>
          <div id="ticket${issue.number}" class="accordion-body collapse in">
            <div class="accordion-inner">
              ${issue.body.replace('\n', '<br />')}

              % for comment in issue.comments:
                <div class="well well-large">
                  <b>${comment.user}:</b>
                  <p>${comment.body.replace('\n', '<br />')}</p>
                </div>
              % endfor
            </div>
          </div>
        </div>
      % endfor
    </div>
  </div>
</div>
