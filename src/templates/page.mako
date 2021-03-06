<%!
  import os
  import os.path
  import sys

  import hlib
  import hruntime

  import lib
  import lib.datalayer

  import games.settlers
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="hlib_page.mako" />

<%def name="script(path)">
  <script type="text/javascript" src="${path}${lib.version_stamp(path)}"></script>
</%def>

<%def name="style(path)">
  <link rel="stylesheet" href="${path}${lib.version_stamp(path)}" type="text/css" />
</%def>

<%def name="page_header()">
  <meta charset="utf-8" />
  <!-- Always force latest IE rendering engine (even in intranet) & Chrome Frame -->
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />

  ${parent.page_favicon(path_prefix = '/static/images/favicon')}

  <!-- Mobile viewport optimized: h5bp.com/viewport -->
  <meta name="viewport" content="width=device-width">
  <!-- Enable responsive design -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- remove or comment this line if you want to use the local fonts -->
  <!-- <link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800' rel='stylesheet' type='text/css' /> -->

  <!-- Stylesheets -->
  ${style('/static/metro/css/bootmetro.css')}
  ${style('/static/metro/css/bootmetro-responsive.css')}
  % if True:
    <link rel="stylesheet" href="http://osadnici.happz.cz/static/metro/css/bootmetro-icons.css" type="text/css" />
  % else:
    ${style('/static/metro/css/bootmetro-icons2.css')}
  % endif
  ${style('/static/metro/css/bootmetro-ui-light.css')}
  ${style('/static/metro/css/datepicker.css')}

  ${style('/static/css/offline-theme-default.css')}
  ${style('/static/css/offline-language-czech.css')}

  ${style('/static/css/settlers.css')}

  <meta name="google-site-verification" content="wA0CBzot_CglwqnQRXErsh8JDRgkX9FhbhnmPyaxtOA" />

  ${script('/static/metro/js/modernizr-2.6.2.min.js')}

  <!-- Scripts -->
  <script src="https://www.google.com/jsapi?key=ABQIAAAAnT7bvt5eCgJnKE_9xHtWrRQL0gKz-n891IYmna21nNIOzPZZixRfXXTxioGg6bd4WAedyIJq9y470A" type="text/javascript"></script>

  ${script('/static/metro/js/jquery-1.10.0.min.js')}
  ${script('/static/script/jquery-ui.js')}

  ${script('/static/script/jquery.form.js')}
  ${script('/static/script/jquery.timers.js')}
  ${script('/static/script/jquery.sound.js')}

  ${script('/static/script/doT.js')}
  ${script('/static/script/holder.js')}
  ${script('/static/script/marked.js')}
  ${script('/static/script/parsley/parsley.min.js')}
  ${script('/static/script/stacktrace.js')}
  ${script('/static/script/strftime.js')}
  ${script('/static/script/offline.js')}

  ${script('/static/metro/js/jquery.mousewheel.min.js')}
  ${script('/static/metro/js/jquery.touchSwipe.min.js')}

  <!--[if IE 7]>
    ${script('/static/metro/js/min/bootmetro-icons-ie7.min.js')}
  <![endif]-->
  ${script('/static/metro/js/min/bootstrap.min.js')}
  ${script('/static/metro/js/min/bootmetro-panorama.min.js')}
  ${script('/static/metro/js/min/bootmetro-pivot.min.js')}
  ${script('/static/metro/js/min/bootmetro-charms.min.js')}

  ${script('/static/script/hlib/ajax.min.js')}
  ${script('/static/script/hlib/pager.min.js')}
  ${script('/static/script/hlib/form.min.js')}
  ${script('/static/script/hlib/tabs.min.js')}
  ${script('/static/script/hlib/message.min.js')}
  ${script('/static/script/hlib/hlib.min.js')}
  ${script('/static/script/settlers.min.js')}
  ${script('/static/script/validators.min.js')}

  ${script('/static/script/realchat/client.min.js')}

  % if self.uri.startswith('games/'):
    <%
      kind = self.uri.split('/')[1].split('.')[0]
    %>

    ${style('/static/css/pages/game.css')}
    ${style('/static/css/games/' + kind + '/' + kind + '.css')}
    ${style('/static/css/games/' + kind + '/' + kind + '-board.css')}

    ${script('/static/script/pages/game.js')}
    ${script('/static/script/games/' + kind + '/' + kind + '.min.js')}
    ${script('/static/script/games/' + kind + '/' + kind + '-board.min.js')}
  % endif

  <%
    current_page_name = next.name.split(':')[1].split('.')[0]

    page_script_file = os.path.join(hruntime.app.config['dir'], 'static', 'script', 'pages', current_page_name + '.min.js')
    page_style_file = os.path.join(hruntime.app.config['dir'], 'static', 'css', 'pages', current_page_name + '.css')
  %>

  % if os.path.exists(page_style_file):
    ${style('/static/css/pages/' + current_page_name + '.css')}
  % endif

  % if os.path.exists(page_script_file):
    ${script('/static/script/pages/' + current_page_name + '.min.js')}
  % endif

  <script src="/i18n?lang=${hruntime.i18n.name}" type="text/javascript"></script>

  <script type="text/javascript">
    Offline.options = {
      checkOnLoad: false,
      interceptRequests: true,
      reconnect: {
        initialDelay: 60
      },
      requests: false,
      game: false,
      checks: {
        active: 'xhr',
        xhr: {
          url: '/pull_notify'
        }
      }
    };

    window.settlers = window.settlers || {};
    window.settlers.title = "${hlib.unescape(_(hruntime.app.config['label']))}";

    % if hruntime.user != None:
      window.settlers.user = {
        name:                   "${hruntime.user.name}",
        sound:                  ${'true' if hruntime.user.sound == True else 'false'},
        name: "${hruntime.user.avatar_name}",
        color: "${hruntime.user.color(games.settlers.COLOR_SPACE).color}"
      };
    % endif
  </script>

  <script type="text/javascript">
    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', 'UA-615278-4']);
    _gaq.push(['_trackPageview']);

    (function() {
      var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
      ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
      var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
    })();
  </script>

  ${parent.page_header()}
</%def>

<%def name="page_title()">
  ${_(hruntime.app.config['title'])}
</%def>

##
## Start rendering
##

<%def name="page_header_public()">
  <div class="container-fluid">
</%def>

<%def name="menu_entry(icon, label, href = None, id = None, content = None, toggle = None, badge = 'important')">
  <%
    href = href or '#'
    id = 'id="' + id + '"' if id else ''
    content = content or ''
    toggle = 'data-toggle="%s"' % toggle if toggle else ''
  %>

  <a class="win-command" href="${href}" title="${_(label)}" rel="tooltip" data-placement="top" ${id} style="position: relative" ${toggle}>
    <span class="win-commandicon win-commandring icon-${icon}"></span>
    <span class="win-label">${_(label)}</span>
    % if len(id) > 0:
    <span class="badge badge-${badge} menu-alert"></span>
      ${content}
    % endif
  </a>
</%def>

<%def name="page_header_private()">
  <div class="container-fluid">
</%def>

<%def name="page_footer_private()">
  <%
    current_page_name = next.name.split(':')[1].split('.')[0]
  %>

  </div>

  <footer class="win-commandlayout navbar-fixed-bottom navbar-inverse win-ui-dark">
    <div class="container-fluid">
      <div class="row-fluid">
        <div class="span12" style="text-align: center">
          ${menu_entry('home', 'Home', href = '/home/', id = 'menu_home', content = '<span class="badge badge-info menu-alert"></span>')}
          ${menu_entry('archive', 'Archive', href = '/archive/')}
          ${menu_entry('plus-5', 'New ...', href = '/new/')}
          ${menu_entry('comment-3', 'Board', href = '/chat/', id = 'menu_chat')}
          ${menu_entry('bars-3', 'Stats', href = '/stats/')}
          ${menu_entry('cog-6', 'Settings', href = '/settings/')}

          <hr class="win-command" />

          ${menu_entry('question-mark', 'Help', href = 'http://wiki.happz.cz/doku.php?id=settlers:start')}

          % if hruntime.user.is_admin:
            ${menu_entry('tools', 'Admin', href = '/admin/')}
            ${menu_entry('info-5', 'Monitor', href = '/monitor/')}
            <hr class="win-command" />
          % endif
          ${menu_entry('logout', 'Log out', href = '/logout', id = 'menu_logout')}

          <hr class="win-command" />

          ${menu_entry('bug', 'Report issue', href = '/issues/')}
          <!-- ${menu_entry('info', 'About ...', href = '/about/')} -->

          <hr class="win-command" />

          ${menu_entry('chat', 'Chat', href = '#realchat_dialog', toggle = 'modal', id = 'menu_realchat', badge = 'info')}
        </div>
      </div>
    </div>
  </footer>

  <div class="modal hide fade" tabindex="-1" role="dialog" aria-hidden="true" id="realchat_dialog">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true"></button>
      <h3>Chat</h3>
    </div>
    <div class="modal-body">
      <p>${_('Last 100 messages only. Type in your message and press Enter. Press Escape or click Close to close this window.')}</p>
      <p><input type="text" class="input-large" id="realchat_input" /></p>
      <ul>
      </ul>
    </div>
    <div class="modal-footer">
      <a href="#" data-dismiss="modal" class="btn">Close</a>
    </div>
  </div>
</%def>

<%def name="page_footer_public()">
  </div>

  <%
    current_page_name = next.name.split(':')[1].split('.')[0]
    if current_page_name == 'maintenance':
      return ''
  %>

  <div class="row-fluid">
    <div class="offset3 span6" style="text-align: center">
      <a href="/login/">${_('Log in')}</a> | <a href="/registration/">${_('Registration')}</a> | <a href="/registration/recovery/">${_('Forgot password?')}</a> | <a href="/loginas/">${_('Admin login')}</a>
    </div>
  </div>
</%def>

<div class="modal warning hide trumpet-board" tabindex="-1" role="dialog" aria-hidden="true" id="trumpet_board_dialog">
  <div class="modal-body">
    <p></p>
  </div>
  % if hruntime.user != None:
    <div class="modal-footer">
      <a href="#" class="btn">${_('Hide')}</a>
    </div>
  % endif
</div>

% if hruntime.user != None:
  ${page_header_private()}
% else:
  ${page_header_public()}
% endif

${next.body()}

% if hruntime.user != None:
  ${page_footer_private()}
% else:
  ${page_footer_public()}
% endif

<span id="pull-notify" class="hide"></span>

<!-- Message dialog -->
<div class="modal message hide fade" tabindex="-1" role="dialog" aria-hidden="true" id="message_dialog">
  <div class="modal-header">
    <h3></h3>
  </div>
  <div class="modal-body">
    <p></p>
  </div>
  <div class="modal-footer">
    <button class="btn btn-large" data-dismiss="modal">${_('Close')}</button>
  </div>
</div>

<div id="visibility_check_mobile" class="hidden-phone hidden-tablet"></div>
