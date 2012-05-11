<%!
  import games
%>

<%namespace file="lib.mako" import="*" />
<%namespace file="hlib_widgets.mako"  import="*"/>

<%inherit file="page.mako" />

<div id="views">

  <ul class="hide">
    <li><a href="#view_game">Games</a></li>
    <li><a href="#view_tournament">Tournament</a></li>
  </ul>

  <div class="row">
    <div class="prepend-3 span-6 last right">
      <input type="button" id="show_game" class="formee-button hide" value="Add game" />
      <input type="button" id="show_tournament" class="formee-button" value="Add tournament" />
    </div>
  </div>

  <div id="view_game">
    ${row_start()}

    ${w_form_start('/game/new', 'New game', 'new_game')}
      ${w_form_select('kind', label = 'Game kind', required = True)}
        % for kind in games.GAME_KINDS:
          ${w_option(kind, False, kind)}
        % endfor
      </select></div>

      ${w_form_input('name', 'text', label = 'Game name', required = True)}

      ${w_form_select('limit', label = 'Number of players', required = True)}
        % for i in range(3, 5):
          ${w_option(i, False, str(i))}
        % endfor
      </select></div>

      ${w_form_input('desc', 'text', label = 'Game description')}

      ${w_submit_row('Create')}
    </fieldset>

    <fieldset>
      <legend>Access control</legend>

      ${w_form_input('password', 'password', label = 'If you want to create game with secret password just for people who know password, fill in this field')}

      <div class="grid-12-12">
        ${w_form_label('Or, you can invite some people by typing their names here')}
      </div>

      ${w_form_input('opponent1', 'text', label = 'Opponent #1')}
      ${w_form_input('opponent2', 'text', label = 'Opponent #2')}
      ${w_form_input('opponent3', 'text', label = 'Opponent #3')}

    </fieldset>
    <fieldset>
      <legend>Additional game rules</legend>

      ${w_form_select('turn_limit', label = 'Turn limit', default = False)}
        ${w_option('43200', False, '12 hours')}
        ${w_option('86400', False, '1 day')}
        ${w_option('172800', False, '2 days')}
        ${w_option('259200', False, '3 days')}
        ${w_option('604800', True, '1 week')}
        ${w_option('1209600', False, '2 weeks')}
      </select></div>

      ${w_form_select('floating_desert', label = 'Floating desert', default = False)}
        ${w_option(1, True, 'Yes')}
        ${w_option(0, False, 'No')}
      </select></div>

    ${w_form_end()}

    ${row_end()}
  </div>

  <div id="view_tournament">
    ${row_start()}

    ${w_form_start('/tournament/new', 'New tournament', 'new_tournament')}
      ${w_form_select('kind', label = 'Game kind', required = True)}
        % for kind in games.GAME_KINDS:
          ${w_option(kind, False, _(kind))}
        % endfor
      </select></div>

      ${w_form_input('name', 'text', label = 'Tournament name', required = True)}

      ${w_form_select('tournament_players', label = 'Number of players in tournament', required = True)}
        % for i in range(8, 33):
          ${w_option(i, False, str(i))}
        % endfor
      </select></div>

      ${w_form_select('limit', label = 'Number of players per game', required = True)}
        % for i in range(3, 5):
          ${w_option(i, False, str(i))}
        % endfor
      </select></div>

      ${w_form_input('desc', 'text', label = 'Tournament description')}

      ${w_submit_row('Create')}

    </fieldset>
    <fieldset>
      <legend>Access control</legend>

      ${w_form_input('password', 'password', label = 'If you want to create game with secret password just for people who know password, fill in this field')}

    </fieldset>
    <fieldset>
      <legend>Additional game rules</legend>

      ${w_form_select('turn_limit', label = 'Turn limit', default = False)}
        ${w_option('43200', False, '12 hours')}
        ${w_option('86400', False, '1 day')}
        ${w_option('172800', False, '2 days')}
        ${w_option('259200', False, '3 days')}
        ${w_option('604800', True, '1 week')}
        ${w_option('1209600', False, '2 weeks')}
      </select></div>

      ${w_form_select('floating_desert', label = 'Floating desert', default = False)}
        ${w_option(1, True, 'Yes')}
        ${w_option(0, False, 'No')}
      </select></div>

    ${w_form_end()}
    ${row_end()}
  </div>

</div>
