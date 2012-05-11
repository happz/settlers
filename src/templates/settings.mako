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

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

  ${row_start()}
  ${w_form_start('/settings/password', 'Change password', 'password')}
    ${w_form_input('password1', 'password', label = 'Password')}
    ${w_form_input('password2', 'password', label = 'Password verification')}

    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/after_pass_turn', 'After pass turn do what?', 'after_pass_turn')}
    ${w_form_select('action', default = False)}
      ${w_option(lib.datalayer.User.AFTER_PASS_TURN_STAY, hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_STAY, _('Stay on current game'))}
      ${w_option(lib.datalayer.User.AFTER_PASS_TURN_NEXT, hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_NEXT, _('Switch to next current game'))}
      ${w_option(lib.datalayer.User.AFTER_PASS_TURN_CURR, hruntime.user.after_pass_turn == lib.datalayer.User.AFTER_PASS_TURN_CURR, _('Switch to current games'))}
    </select></div>

    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/color', 'Favourite color', 'color')}
    ${w_form_select('color')}
      % for color_name in games.settlers.COLOR_SPACE.unused_colors(user):
        <%
          color = games.settlers.COLOR_SPACE.colors[color_name]
        %>
        ${w_option(color.name, False, _(color.label), classes = ['colors'], style = ['background-image: url(/static/images/games/settlers/board/real/players/' + color.name + '/node/village.gif)'])}
      % endfor
    </select></div>

    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/opponents/add', 'Colors for opponents', 'opponent_colors')}
    % if len(games.settlers.COLOR_SPACE.unused_colors(user)) > 3:
      <div class="grid-4-12">
        ${w_form_input('username', 'text', label = 'Player', struct = False)}
      </div>
      <div class="grid-4-12">
        ${w_form_select('kind', label = 'Game', struct = False)}
          % for kind in games.GAME_KINDS:
            ${w_option(kind, False, _(kind))}
          % endfor
        </select>
      </div>
      <div class="grid-4-12">
        ${w_form_select('color', label = 'Color', struct = False)}
          % for color_name in games.settlers.COLOR_SPACE.unused_colors(user):
            <%
              color = games.settlers.COLOR_SPACE.colors[color_name]
            %>
            ${w_option(color.name, False, _(color.label), classes = ['colors'], style = ['background-image: url(/static/images/games/settlers/board/real/players/' + color.name + '/node/village.gif);'])}
          % endfor
        </select>
      </div>
      ${w_submit_row('Set')}
    % endif

    <div id="opponent_colors_list">
    % if max([0] + [len(v) for v in hruntime.user.colors.values()]) > 1:
      <hr />
      <ul>
        % for k1, v1 in hruntime.user.colors:
          % for k2, v2 in v1:
            <li>${k1} - ${k2} - ${v2}</li>
          % endfor
        % endfor
      </ul>
    % endif
    </div>
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/table_length', 'Games per page of game table', 'table_length')}
    ${w_form_select('per_page', default = False)}
      % for cnt in handlers.settings.TABLE_ROW_COUNTS:
        ${w_option(cnt, user.table_length == cnt, cnt)}
      % endfor
    </select></div>

    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/board_skin', 'Game board skin', 'board_skin')}
    ${w_form_select('skin', default = False)}
      ${w_option('real', user.board_skin == 'real', _('Realistic'))}
      ${w_option('simple', user.board_skin == 'simple', _('Simple'))}
    </select></div>

    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/vacation/start', 'Vacation', 'vacation')}
    <div class="grid-12-12">
      <div class="form-msg-info">
        <h3>${_('Vacation left')}: ${stamp_to_days_hours(user.vacation)}</h3>
      </div>
    </div>

    <%def name="list_vacation(label, vacation)">
      <div class="grid-2-12">${_(label + ' from')}</div>
      <div class="grid-3-12">${time.strftime(user.date_format, time.localtime(vacation.start))}</div>
      <div class="grid-1-12">${_('to')}</div>
      <div class="grid-3-12">${time.strftime(user.date_format, time.localtime(vacation.start + vacation.length))}</div>
      <div class="grid-3-12">(${stamp_to_days_hours(vacation.length)})</div>
    </%def>

    % if user.has_vacation == True:
      <hr />

      % for v in lib.datalayer.VacationRecord.load_from_db_by_user(user.id, order = ('start', False)):
        ${list_vacation('Passed vacation', v)}
      % endfor
    % endif

    % if user.has_prepared_vacation == True:
      <hr />

      ${list_vacation('Vacation planned', user.last_vacation)}
      <div class="grid-1-12">
        <a href="/settings/vacation/revoke">${_('Revoke')}</a>
      </div>
    % endif

    <div class="grid-12-12">
      <label>${_('Start vacation from')}</label>
    </div>
    <div class="grid-6-12">
      <input type="text" class="dateRange" name="vacation_from_day" id="vacation_from_day" />
    </div>
    <div class="grid-6-12">
      <select name="vacation_from_hour">
        ${w_option('', True, '')}
        % for i in range(0, 9):
          ${w_option(i, False, '0' + str(i) + ':00')}
        % endfor
        % for i in range(10, 24):
          ${w_option(i, False, str(i) + ':00')}
        % endfor
      </select>
    </div>

    <div class="grid-12-12">
      <label>${_('to')}</label>
    </div>
    <div class="grid-6-12">
      <input type="text" class="dateRange" name="vacation_to_day" id="vacation_to_day" />
    </div>
    <div class="grid-6-12">
      <select name="vacation_to_hour">
        ${w_option('', True, '')}
        % for i in range(0, 9):
          ${w_option(i, False, '0' + str(i) + ':00')}
        % endfor
        % for i in range(10, 24):
          ${w_option(i, False, str(i) + ':00')}
        % endfor
      </select>
    </div>
    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}

  ${row_start()}
  ${w_form_start('/settings/sound', 'Sound notification', 'sound')} 
    ${w_form_select('sound', label = 'Play sound when player is on turn', default = False)}
      ${w_option('0', hruntime.user.sound == False, _('No'))}
      ${w_option('1', hruntime.user.sound == True, _('Yes'))}
    </select></div>

    ${w_submit_row('Set')}
  ${w_form_end()}
  ${row_end()}
