<%!
  import os
  import os.path
  import sys

  import hlib
  import hruntime

  import lib
  import lib.datalayer
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

  ${parent.page_favicon(path_prefix = '/static/images/favicon', tile_background = '#36932A')}

  <!-- Mobile viewport optimized: h5bp.com/viewport -->
  <meta name="viewport" content="width=device-width">
  <!-- Enable responsive design -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- remove or comment this line if you want to use the local fonts -->
  <!-- <link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800' rel='stylesheet' type='text/css' /> -->

  <!-- Stylesheets -->
  <!--[if lt IE 9]>${style('/static/metro/css/bootmetro-icons-ie7.css')}<![endif]-->
  ${style('/static/metro/css/bootmetro-icons.css')}
  ${style('/static/metro/css/bootmetro.css')}
  ${style('/static/metro/css/bootmetro-responsive.css')}
  ${style('/static/metro/css/metro-ui-light.css')}
  ${style('/static/metro/css/datepicker.css')}

  ${style('/static/css/settlers.css')}

  ${script('/static/metro/scripts/modernizr-2.6.2.min.js')}

  <!-- Scripts -->
  <script src="https://www.google.com/jsapi?key=ABQIAAAAnT7bvt5eCgJnKE_9xHtWrRQL0gKz-n891IYmna21nNIOzPZZixRfXXTxioGg6bd4WAedyIJq9y470A" type="text/javascript"></script>

  ${script('/static/script/jquery.js')}
  ${script('/static/script/jquery-ui.js')}

  ${script('/static/script/jquery.form.js')}
  ${script('/static/script/jquery.timers.js')}
  ${script('/static/script/jquery.sound.js')}
  ${script('/static/script/stacktrace.js')}
  ${script('/static/script/doT.js')}
  ${script('/static/script/strftime.js')}
  ${script('/static/script/parsley/parsley.min.js')}

  ${script('/static/metro/scripts/jquery.mousewheel.min.js')}
  ${script('/static/metro/scripts/jquery.scrollTo.min.js')}
  ${script('/static/metro/scripts/bootstrap.min.js')}
  ${script('/static/metro/scripts/bootmetro-panorama.min.js')}
  ${script('/static/metro/scripts/bootmetro-charms.js')}
  ${script('/static/metro/scripts/holder.min.js')}
  ${script('/static/metro/scripts/bootstrap-datepicker.js')}

  ${script('/static/script/hlib/ajax.min.js')}
  ${script('/static/script/hlib/pager.min.js')}
  ${script('/static/script/hlib/form.min.js')}
  ${script('/static/script/hlib/tabs.min.js')}
  ${script('/static/script/hlib/message.min.js')}
  ${script('/static/script/hlib/hlib.min.js')}
  ${script('/static/script/settlers.min.js')}
  ${script('/static/script/validators.min.js')}
  ${script('/static/script/marked.js')}

  <meta name="google-site-verification" content="wA0CBzot_CglwqnQRXErsh8JDRgkX9FhbhnmPyaxtOA" />

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
    window.settlers = window.settlers || {};
    window.settlers.title = "${hlib.unescape(_(hruntime.app.config['label']))}";

    % if hruntime.user != None:
      window.settlers.user = {
        name:                   "${hruntime.user.name}",
        sound:                  ${'true' if hruntime.user.sound == True else 'false'},
        name: "${hruntime.user.avatar_name}"
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

<%def name="menu_entry(icon, label, href = None, id = None, content = None)">
  <%
    href = href or '#'
    id = 'id="' + id + '"' if id else ''
    content = content or ''
  %>

  <a class="win-command" href="${href}" title="${_(label)}" rel="tooltip" data-placement="top" ${id} style="position: relative">
    <span class="win-commandimage win-commandring">${icon}</span>
    <span class="win-label">${_(label)}</span>
    % if len(id) > 0:
      <span class="badge badge-important menu-alert"></span>
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
          ${menu_entry('&#x0021;', 'Home', href = '/home/', id = 'menu_home', content = '<span class="badge badge-info menu-alert"></span>')}
          ${menu_entry('&#xe03e;', 'New ...', href = '/new/')}
          ${menu_entry('&#xe20d;', 'Board', href = '/chat/', id = 'menu_chat')}
          ${menu_entry('&#x0072;', 'Stats', href = '/stats/')}
          ${menu_entry('&#x0070;', 'Settings', href = '/settings/')}

          <hr class="win-command" />

          ${menu_entry('&#xe1a4;', 'Help', href = 'http://wiki.happz.cz/doku.php?id=settlers:start')}

          % if hruntime.user.is_admin:
            ${menu_entry('&#x006e;', 'Admin', href = '/admin/')}
            ${menu_entry('&#xe037;', 'Monitor', href = '/monitor/')}
            <hr class="win-command" />
          % endif
          ${menu_entry('&#xe040;', 'Log out', href = '/logout', id = 'menu_logout')}

          <hr class="win-command" />

          ${menu_entry('&#xe126;', 'Report issue', href = '/issues/')}
          ${menu_entry('&#xe12a;', 'About ...', href = '/about/')}
        </div>
      </div>
    </div>
  </footer>
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
