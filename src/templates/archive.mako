<%!
  import sys

  import hlib
  import hruntime

  import games
%>

<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

${ui_page_header('Archive')}

<div class="row-fluid">
  <div class="span12">

    <table class="table table-hover table-condensed">
      <thead>
        <tr>
          <th>${_('Finished')}</th>
          <th colspan="3">${_('Players')}</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="finished">
        % for playable in games.f_archived(hruntime.user):
          <tr id="${playable.id}">
            <td>
              % if playable.get_type():
                ${_('Game')}
              % else:
                ${_('Tournament')}
              % endif
              &nbsp;#${playable.id} - ${playable.name}
            </td>
            <td>${playable.limit} ${_('players')}</td>
            <td>${', '.join([p.user.name for p in playable.players.values()])}</td>
            <td>${_('Winner is')} ${playable.forhont_player.user.name}</td>
            <td>
              <div class="btn-toolbar">
                <div>
                  % if playable.get_type():
                    <a class="btn" href="/game/?gid=${playable.id}#board" title="${_('Show board')}" rel="tooltip" data-placement="top" id="${playable.id}_board" style="position: relative"><i class="icon-info-7"></i><span class="badge badge-important menu-alert"></span></a>
                  % else:
                    <a class="btn" href="/tournament/?tid=${playable.id}#board" title="${_('Show board')}" rel="tooltip" data-placement="top" id="${playable.id}_board" style="position: relative"><i class="icon-info-7"></i><span class="badge badge-important menu-alert"></span></a>
                  % endif
                </div>
              </div>
            </td>
          </tr>
        % endfor
      </tbody>
    </table>

  </div>
</div>
