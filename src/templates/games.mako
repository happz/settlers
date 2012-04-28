<%!
  PLUGINS = ['JQuery', 'Accordion', 'Autocomplete', 'DataTables', 'Sound']
  FUNCTIONS = ['opponents_set_autocomplete', 'tournament_init', 'datatables_init']

  import sys
  import hlib
%>

<%
  import time
  import types
  import games
  import hlib

  current_lister = listers[handler.view.name]
%>

<%namespace file="hlib_widgets.mako"  import="*"/>
<%namespace file="games_lib.mako" import="*"/>
<%namespace file="lib.mako" import="*" />

<%inherit file="page.mako" />

<%def name="page_script()">
  ${parent.page_script()}

  <%
    current_lister = listers[handler.view.name]
  %>

  % if handler.view.name == 'new':

  function opponents_set_autocomplete()
  {
    $("#opponent1").autocomplete('/admin/ajax_users_by_name', {
      multiple: false,
      matchContains: true
    });
    $("#opponent2").autocomplete('/admin/ajax_users_by_name', {
      multiple: false,
      matchContains: true
    });
    $("#opponent3").autocomplete('/admin/ajax_users_by_name', {
      multiple: false,
      matchContains: true
    });
  }

  function tournament_init()
  {
    $('#tournament_players').change(tournament_show_tree);
    $('#limit').change(tournament_show_tree);
  }

  function tournament_show_tree()
  {
    var players = parseInt($('#tournament_players').val());
    var ppg     = parseInt($('#limit').val());
    var round_num = 0;
    var games = 0;

    $('#tournament_tree').html('');

    for (i = 0; i < 10; i++) {
      round_num++;

      round           = new Object;
      round.num       = round_num;
      round.groups    = Math.floor(players / ppg);
      round.leftovers = players % ppg;
      round.bye       = 0;
      round.leveled   = 0;

      if (round.leftovers > 0) {
        if (round.num == 1) {
          round.bye = round.leftovers;
        } else {
          round.leveled = ppg - round.leftovers;
          round.groups++;
        }
      }

      $('#tournament_tree').html($('#tournament_tree').html() + '<br />' + 'Kolo #' + round.num + ': ' + round.groups + ' skupin o ' + ppg + ' hracich. Z minuleho kola vytazeno ' + round.leveled + ' nejlepsich druhych, ' + round.bye + ' hracu ma volno.');

      games += round.groups * ppg;

      players = round.groups + round.bye;
      if (players == 1)
        break;
    }
    $('#tournament_tree').html($('#tournament_tree').html() + '<br />' + 'Celkem ' + games + ' her');
  }

  % else:

  function opponents_set_autocomplete() {}
  function tournament_init() {}

  % endif

  % if handler.view.name in ['free', 'current', 'finished', 'canceled']:

    function datatables_init()
    {
      var tab_id = "${'game_table_' + current_lister.type}";

      var datatable = $('#' + tab_id).dataTable({
        'bProcessing':     false,
        'bServerSide':     true,
        'sAjaxSource':     '/games/lister',
        'sPaginationType': 'full_numbers',
        'bStateSave':      true,
        'bFilter':         false,
        'sDom':            '<"top"i>rpt<"bottom"flp><"clear">',
        'bLengthChange':   false,
        'bAutoWidth':      false,
        'iCookieDuration': 2419200, /* 4 weeks */
        'iDisplayLength':  ${user.table_length},

        'fnDrawCallback': function() {
          $('#working_dialog').dialog('close');
        },

        'fnServerData': function (sSource, aoData, fnCallback) {
          $('#working_dialog').dialog('open');
          $.ajax({
            'dataType': 'json',
            'type':     'POST',
            'url':      sSource,
            'data':     aoData,
            'success':  function (data) {
              fnCallback(data);
              $('#working_dialog').dialog('close');
            }
          });
        },

        'aoColumns':       [
          /* Hidden flags */ {'bSearchable': false, 'bVisible': false },

          % for token in current_lister.layout().split(','):
            % if game_list_headers_new[token]._order == None:
              /* ${token} - disabled sorting */ {'bSearchable': false, 'bSortable': false},

            % else:
              /* ${token} */ {'bSearchable': false},

            % endif
          % endfor
          /* Action */ {'bSearchable': false, 'bSortable': false}
        ],

        'fnRowCallback': function(nRow, aData, iDisplayIndex) {
          if (aData[0] == 'T')
            nRow.className += ' current_on_turn';
          return nRow; 
        },

        /* lokalizace */
        'oLanguage': {
          'oPaginate': {
            'sFirst': "${_('First')}",
            'sLast':  "${_('Last')}",
            'sPrevious': "${_('Previous')}",
            'sNext':     "${_('Next')}"
          },
          'sInfo': "${_('Got a total of _TOTAL_ entries to show (_START_ to _END_)')}",
          'sInfoEmpty':   "${_('There are no games to display')}",
          'sZeroRecords': "${_('No records to display')}",
          'sProcessing':  '',
//          'sProcessing':  "${_('Processing...')}",
          'sEmptyTable':  "${_('There are no games to display')}"
        }
      });

      $('#working_dialog').dialog('open');
    }

  % else:
    function datatables_init() { }

  % endif
</%def>



% if handler.view.name == 'new':
  <div id="accordion">
      <form action="/games/new" method="post">
        <fieldset>
          <legend>${_('New game')}</legend>
          <table>
            <tr class="required">
              <td><label>${_('Game kind:')}</label></td>
              <td>
                <select name="kind" class="selectbox">
                  % for kind in games.GAME_KINDS:
                    <option value="${kind}">${_(kind)}</option>
                  % endfor
                </select>
              </td>
            </tr>
            <tr class="required">
              <td><label>${_('Game name:')}</label></td>
              <td><input type="text" name="name" class="textbox" /></td>
            </tr>
            <tr class="required">
              <td><label>${_('Number of players:')}</label></td>
              <td>
                <select name="limit" id="limit" class="selectbox">
                  <option value="3" selected="selected">3</option>
                  <option value="4">4</option>
                </select>
              </td>
            </tr>
            <tr>
              <td><label>${_('Game description:')}</label></td>
              <td><input type="text" name="desc" class="textbox" /></td>
            </tr>
            <tr class="required">
              <td colspan="2"><label>${_('Red field are required')}</label></td>
            </tr>
            <tr>
              <td colspan="2" style="text-align: right"><input type="submit" value="${_('Create')}" class="button" /></td>
            </tr>
          </table>
        </fieldset>

        <fieldset>
          <legend class="accordion_toggle">${_('Access limitations')}</legend>
          <table class="accordion_content">
            <tr>
              <td colspan="3">${_('If you want to create game with secret password just for people who know password, fill in this field.')}</td>
            </tr>
            <tr>
              <td><label>${_('Password:')}</label></td>
              <td><input type="text" name="password" class="textbox" /></td>
            </tr>
            <tr />
            <tr>
              <td colspan="3">${_('Or, you can invite some people by typing their names here.')}</td>
            </tr>
            <tr>
              <td><label>${_('Opponent #1:')}</label></td>
              <td><input type="text" name="opponent1" class="textbox" id="opponent1" /></td>
            </tr>
            <tr>
              <td><label>${_('Opponent #2:')}</label></td>
              <td><input type="text" name="opponent2" class="textbox" id="opponent2" /></td>
            </tr>
            <tr>
              <td><label>${_('Opponent #3:')}</label></td>
              <td><input type="text" name="opponent3" class="textbox" id="opponent3" /></td>
              <td>${_('If you are creating game for 3 players, leave this field empty.')}</td>
            </tr>
          </table>
        </fieldset>

        <fieldset>
          <legend class="accordion_toggle">${_('Additional game rules')}</legend>
          <table class="accordion_content">
            <tr>
              <td><label>${_('Turn limit:')}</label></td>
              <td>
                <select name="turn_limit" class="selectbox">
                  <option value="43200">${_('12 hours')}</option>
                  <option value="86400">${_('1 day')}</option>
                  <option value="172800">${_('2 days')}</option>
                  <option value="259200">${_('3 days')}</option>
                  <option value="604800" selected="selected">${_('1 week')}</option>
                  <option value="1209600">${_('2 weeks')}</option>
                </select>
              </td>
              <td />
            </tr>
            <tr>
              <td><label>${_('Floating desert:')}</label></td>
              <td>
                <select name="floating_desert" class="selectbox">
                  <option value="1" selected="selected">${_('Yes')}</option>
                  <option value="0">${_('No')}</option>
                </select>
              </td>
            </tr>
          </table>
        </fieldset>

        <fieldset>
          <legend class="accordion_toggle">${_('Start as tournament')}</legend>
          <table class="accordion_content">
            <tr class="required">
              <td><label>${_('Number of players')}</label></td>
              <td>
                <select name="tournament_players" id="tournament_players">
                  <option value="0">${_('Choose')}</option>
                  % for i in range(8, 33):
                    <option value="${i}">${i}</option>
                  % endfor
                </select>
              </td>
            </tr>
            <tr>
              <td colspan="2" id="tournament_tree">
              </td>
            </tr>
          </table>
          <div>
            <ol>
              <li>Jeste to nefunguje</li>
              <li>Pro zalozeni turnaje se ignoruje seznam pozvanych hracu<li>
              <li>Rikal jsem, ze to jeste nefunguje? Aha, rikal. Tak fajn :)</li>
            </ol>
          </div>
        </fieldset>

      </form>
  </div>

% elif handler.view.name in ['free', 'current', 'finished', 'canceled']:

  <table class="list" id="${'game_table_' + current_lister.type}">
    <thead>
      <tr>
        <th>Flags</th>
        % for token in current_lister.layout().split(','):
          % if type(game_list_headers[token]) == types.TupleType:
            <th>${_(game_list_headers[token][0])}</th>

          % else:
            <th>${_(game_list_headers[token])}</th>

          % endif
        % endfor
        <th>${_('Action')}</th>
      </tr>
    </thead>

    <tbody></tbody>

  </table>

  ${working_dialog('/games/')}

% endif
