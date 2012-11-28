<%!
  import time
  import hlib
  import lib.datalayer
  import handlers.settings

  import games
  import games.settlers

  import hruntime
%>

<%
  import handlers.settings
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('Settings')}

<div class="row-fluid">
  <!-- Leave space for affix -->
  <div class="offset2 span10">

<!-- "Account" section -->
${ui_section_header('account', 'Account')}

  <!-- Change password -->
  ${ui_form_start(action = '/settings/password', id = 'password', legend = 'Change password')}
    <!-- Password -->
    ${ui_input(type = 'password', label = 'Password', form_name = 'password1')}

    <!-- Password verification -->
    ${ui_input(type = 'password', label = 'Password verification', form_name = 'password2')}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

  <!-- After "Pass turn" -->
  ${ui_form_start(action = '/settings/after_pass_turn', id = 'after_pass_turn', legend = 'After pass turn do what?')}
    <!-- After "Pass turn" -->
    ${ui_select_start(form_name = 'action', default = False, size = 'xxlarge')}
      ${ui_select_option(value = lib.datalayer.User.AFTER_PASS_TURN_NEXT, selected = (hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_NEXT), label = 'Switch to next current game')}
      ${ui_select_option(value = lib.datalayer.User.AFTER_PASS_TURN_STAY, selected = (hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_STAY), label = 'Stay on current game')}
      ${ui_select_option(value = lib.datalayer.User.AFTER_PASS_TURN_CURR, selected = (hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_CURR), label = 'Switch to current games')}
    ${ui_select_end()}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

  <!-- Per page -->
  ${ui_form_start(action = '/settings/per_page', id = 'per_page', legend = 'Items per page of table')}
    ${ui_select_start(form_name = 'per_page', default = False)}
      % for cnt in handlers.settings.TABLE_ROW_COUNTS:
        ${ui_select_option(value = cnt, selected = (user.table_length == cnt), label = str(cnt))}
      % endfor
    ${ui_select_end()}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

  <!-- Sound -->
  ${ui_form_start(id = 'sound', action = '/settings/sound', legend = 'Sound notification')}
    ${ui_select_start(form_name = 'sound', label = 'Play sound when player is on turn', default = False)}
      ${ui_select_option(value = 0, selected = (hruntime.user.sound == False), label = 'No')}
      ${ui_select_option(value = 1, selected = (hruntime.user.sound == True), label = 'Yes')}
    ${ui_select_end()}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

</section>

<!-- "Colors" section -->
${ui_section_header('colors', 'Colors')}

  <!-- Color -->
  ${ui_form_start(action = '/settings/color', id = 'color', legend = 'Favourite color')}
    <!-- Game -->
    ${ui_select_start(form_name = 'kind', label = 'Game', default = 'Choose...')}
      % for kind in games.GAME_KINDS:
        ${ui_select_option(value = kind, selected = False, label = kind)}
      % endfor
    ${ui_select_end()}

    <!-- Color -->
    ${ui_select_start(form_name = 'color', label = 'Color', default = False, disabled = True)}
    ${ui_select_end()}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

  <!-- Opponent colors -->
  ${ui_form_start(action = '/settings/opponents/add', id = 'opponent_colors', legend = 'Colors for opponents')}
    <!-- Game -->
    ${ui_select_start(form_name = 'kind', label = 'Game', default = 'Choose...')}
      % for kind in games.GAME_KINDS:
        ${ui_select_option(value = kind, selected = False, label = kind)}
      % endfor
    ${ui_select_end()}

    <!-- Color -->
    ${ui_select_start(form_name = 'color', label = 'Color', default = False, disabled = True)}
    ${ui_select_end()}

    <!-- Player -->
    ${ui_input(type = 'text', form_name = 'username', label = 'Player')}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

  <div id="opponent_colors_list"></div>

  <!-- Board skin -->
  ${ui_form_start(action = '/settings/board_skin', legend = 'Game board skin', id = 'board_skin')}
    ${ui_select_start(form_name = 'skin', default = False)}
      ${ui_select_option(value = 'real', selected = (user.board_skin == 'real'), label = 'Realistic')}
      ${ui_select_option(value = 'simple', selected = (user.board_skin == 'simple'), label = 'Simple')}
    ${ui_select_end()}

    ${ui_submit(value = 'Set')}
  ${ui_form_end()}

</section>

<!-- "API" section -->
${ui_section_header('api', 'API')}

  <!-- API token -->
  ${ui_form_start(id = 'api_token', action = '/settings/api', legend = 'API token')}
    <div class="control-group">
      <div class="controls">
        <input type="button" id="api_token_new" value="${_('New token')}" class="btn" />
        <input type="button" id="api_token_download" value="${_('Download token')}" class="btn" />
      </div>
    </div>
  ${ui_form_end()}

  <h4>${_('Current API token')}</h4>
  <code id="api_token_token">
    % if len(hruntime.user.api_tokens) > 0:
      ${hruntime.user.api_tokens[0]}
    % endif
  </code>

  <hr />

  <header><h4>${_('Remote applications')}</h4></header>

  <div class="listview-container grid-layout">
    <div class="mediumListIconTextItem">
      <img src="holder.js/60x60" class="mediumListIconTextItem-Image" />
      <div class="mediumListIconTextItem-Detail">
        <h4>Osadnici - Hlidacek</h4>
        <a href="http://osadnici-test.happz.cz/static/settlers-notify.exe">Download</a>
      </div>
    </div>
  </div>

  <iframe id="api_token_downloader" src="" class="hide"></iframe>
</section>

  </div>
</div>
