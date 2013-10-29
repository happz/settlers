<%!
  import games
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('New ...')}

<div class="row-fluid">
  <div class="offset2 span10">

<!-- "Game" section -->
${ui_section_header('game', 'Game')}
      ${ui_form_start(legend = 'New game', id = 'new_game', validate = True)}

        <!-- Game -->
        ${ui_select_start(form_name = 'kind', label = 'Game kind', required = True, validators = 'required notblank inlist="' + ', '.join(games.GAME_KINDS) + '"')}
        <!-- ${ui_select_start(form_name = 'kind', label = 'Game kind', default = 'Choose...', required = True)} -->
          % for kind in games.GAME_KINDS:
            ${ui_select_option(value = kind, selected = (True if kind == 'settlers' else False), label = kind)}
          % endfor
        ${ui_select_end()}

        <!-- Name -->
        ${ui_input(form_name = 'name', type = 'text', label = 'Game name', required = True, validators = 'required notblank minlength="2" maxlength="64"')}

        <!-- Number of players -->
        ${ui_select_start(form_name = 'limit', label = 'Number of players', required = True, validators = 'required notblank inlist="' + ', '.join(['3', '4']) + '" type="number"')}
          % for i in range(3, 5):
            ${ui_select_option(value = i, selected = False, label = str(i))}
          % endfor
        ${ui_select_end()}

        <!-- Description -->
        ${ui_input(form_name = 'desc', type = 'text', label = 'Game description', validators = 'maxlength="64"')}

        ${ui_submit(value = 'Create', id = 'new_game_submit')}
      </fieldset>

      <fieldset>
        <legend>${_('Access control')}</legend>

        ${ui_input(form_name = 'opponent1', type = 'text', label = 'Opponent #1')}
        ${ui_input(form_name = 'opponent2', type = 'text', label = 'Opponent #2')}
        ${ui_input(form_name = 'opponent3', type = 'text', label = 'Opponent #3', help = 'You can invite some people by typing their names here')}

        ${ui_input(type = 'password', form_name = 'password', label = 'Password', help = 'If you want to create game with secret password just for people who know password, fill in this field')}
      </fieldset>

      <fieldset>
        <legend>${_('Additional game rules')}</legend>

        <!-- Turn limit -->
        ${ui_select_start(form_name = 'turn_limit', label = 'Turn limit', default = False)}
          ${ui_select_option(value = '43200', selected = False, label = '12 hours')}
          ${ui_select_option(value = '86400', selected = False, label = '1 day')}
          ${ui_select_option(value = '172800', selected = False, label = '2 days')}
          ${ui_select_option(value = '259200', selected = False, label = '3 days')}
          ${ui_select_option(value = '604800', selected = True, label = '1 week')}
          ${ui_select_option(value = '1209600', selected = False, label = '2 weeks')}
        ${ui_select_end()}

        <!-- Floating desert -->
        ${ui_select_start(form_name = 'floating_desert', label = 'Floating desert', default = False)}
          ${ui_select_option(value = 1, selected = True, label = 'Yes')}
          ${ui_select_option(value = 0, selected = False, label = 'No')}
        ${ui_select_end()}

        <!-- Spread fields -->
        ${ui_select_start(form_name = 'spread_fields', label = 'Spread 6/8 fields', default = False)}
          ${ui_select_option(value = 1, selected = True, label = 'Yes')}
          ${ui_select_option(value = 0, selected = False, label = 'No')}
        ${ui_select_end()}
      ${ui_form_end()}
</section>

<%
  unused = """
<!-- "Tournament" section -->
${ui_section_header('tournament', 'Tournament')}
      ${ui_form_start(action = '/tournament/new', legend = 'New tournament', id = 'new_tournament')}

        <!-- Engine -->
        ${ui_select_start(form_name = 'engine', label = 'Engine', required = True)}
          ${ui_select_option(value = 'swiss', selected = False, label = 'swiss')}
        ${ui_select_end()}

        <!-- Game -->
        ${ui_select_start(form_name = 'kind', label = 'Game kind', default = 'Choose...', required = True)}
          % for kind in games.GAME_KINDS:
            ${ui_select_option(value = kind, selected = False, label = kind)}
          % endfor
        ${ui_select_end()}

        <!-- Name -->
        ${ui_input(form_name = 'name', type = 'text', label = 'Game name', required = True)}

        <!-- Number of players -->
        ${ui_select_start(form_name = 'num_players', label = 'Number of players in tournament', required = True)}
          ${ui_select_option(value = 12, selected = False, label = '12')}
          ${ui_select_option(value = 24, selected = False, label = '24')}
        ${ui_select_end()}

        <!-- Number of players per game -->
        ${ui_select_start(form_name = 'limit', label = 'Number of players per game', required = True)}
          % for i in range(3, 5):
            ${ui_select_option(value = i, selected = False, label = str(i))}
          % endfor
        ${ui_select_end()}

        <!-- Description -->
        ${ui_input(form_name = 'desc', type = 'text', label = 'Tournament description')}

        ${ui_submit(value = 'Create', id = 'new_tournament_submit')}
      </fieldset>

      <fieldset>
        <legend>${_('Access control')}</legend>

        ${ui_input(type = 'password', form_name = 'password', label = 'Password', help = 'If you want to create game with secret password just for people who know password, fill in this field')}
      </fieldset>

      <fieldset>
        <legend>${_('Additional game rules')}</legend>

        <!-- Turn limit -->
        ${ui_select_start(form_name = 'turn_limit', label = 'Turn limit', default = False)}
          ${ui_select_option(value = '43200', selected = False, label = '12 hours')}
          ${ui_select_option(value = '86400', selected = False, label = '1 day')}
          ${ui_select_option(value = '172800', selected = False, label = '2 days')}
          ${ui_select_option(value = '259200', selected = False, label = '3 days')}
          ${ui_select_option(value = '604800', selected = True, label = '1 week')}
          ${ui_select_option(value = '1209600', selected = False, label = '2 weeks')}
        ${ui_select_end()}

        <!-- Floating desert -->
        ${ui_select_start(form_name = 'floating_desert', label = 'Floating desert', default = False)}
          ${ui_select_option(value = 1, selected = True, label = 'Yes')}
          ${ui_select_option(value = 0, selected = False, label = 'No')}
        ${ui_select_end()}
      ${ui_form_end()}
</section>
"""
%>

  </div>
</div>
