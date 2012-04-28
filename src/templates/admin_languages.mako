<%!
  PLUGINS = ['Accordion', 'Sound']

  import hlib
%>

<%namespace file="hlib_widgets.mako"  import="*"/>

<%inherit file="page.mako" />

<div id="accordion">
  <form action="/admin/languages/change_edited" method="post">
    <fieldset>
      <legend class="accordion_toggle">${_('Change edited language')}</legend>
      <table class="accordion_content">
        <tr>
          <td><label>${_('Language:')}</label></td>
          <td>
            <select name="language" class="selectbox">
              <option value="">${_('Choose...')}</option>
              % for name in hlib.localization().languages.keys():
                <option value="${name}">${_(name)}</option>
              % endfor
            </select>
          </td>
        </tr>
        ${w_submit_row(2, 'Set')}
      </table>
    </fieldset>
  </form>

  <form action="/admin/languages/add" method="post">
    <fieldset>
      <legend class="accordion_toggle">${_('Add token')}</legend>
      <table class="accordion_content">
        <tr>
          <td><label>${_('Name:')}</label></td>
          <td><input type="text" name="name" class="textbox" size="50" /></td>
        </tr>
        <tr>
          <td><label>${_('Value:')}</label></td>
          <td><input type="text" name="value" class="textbox" size="50" /></td>
        </tr>
        ${w_submit_row(2, 'Add')}
      </table>
    </fieldset>
  </form>

  <form action="/admin/languages/remove" method="post">
    <fieldset>
      <legend class="accordion_toggle">${_('Remove token')}</legend>
      <table class="accordion_content">
        <tr>
          <td><label>${_('Name:')}</label></td>
          <td>
            <select name="name" class="selectbox">
              <option value="">${_('Choose...')}</option>
              % for key in languages.edited.keys(sort = True):
                <option value="${key}">${key}</option>
              % endfor
            </select>
          </td>
        </tr>
        ${w_submit_row(2, 'Remove')}
      </table>
    </fieldset>
  </form>

  <form action="/admin/languages/edit" method="post">
    <fieldset>
      <legend class="accordion_toggle">${_('Edit tokens - language: %(language)s', language = languages.edited.name)}</legend>
      <table class="accordion_content">
        <tr>
          <th>${_('Name')}</th>
          <th>${_('Value')}</th>
        </tr>
        % for key in languages.edited.keys(sort = True):
          <tr>
            <td><label>${key}</label></td>
            <td><input type="text" name="${key}" value="${languages.edited.data[key]}" class="textbox" /></td>
          </tr>
        % endfor
        ${w_submit_row(2, 'Set')}
      </table>
    </fieldset>
  </form>

</div>
