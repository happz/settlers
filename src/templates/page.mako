<%!
  import os.path
  import sys

  import hlib
  import hruntime
%>

<%namespace file="hlib_ui.mako" import="*" />
<%namespace file="lib.mako" import="*" />

<%inherit file="hlib_page.mako" />

<%def name="script(path)">
  <script src="/static/script/${path}.js"></script>
</%def>

<%def name="page_header()">
  <meta charset="utf-8" />

  <!-- Always force latest IE rendering engine (even in intranet) & Chrome Frame -->
  <!-- <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" /> -->
  <!-- Mobile viewport optimized: h5bp.com/viewport -->
  <meta name="viewport" content="width=device-width">
  <!-- Enable responsive design -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- remove or comment this line if you want to use the local fonts -->
  <!-- <link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800' rel='stylesheet' type='text/css' /> -->

  <!-- Stylesheets -->
  <link rel="stylesheet" type="text/css" href="/static/metro/css/bootstrap.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/bootstrap-responsive.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/bootmetro.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/bootmetro-tiles.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/bootmetro-charms.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/metro-ui-light.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/icomoon.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/datepicker.css">
  <link rel="stylesheet" type="text/css" href="/static/metro/css/daterangepicker.css">

  <script src="/static/metro/scripts/modernizr-2.6.1.min.js"></script>

  <link rel="stylesheet" href="/static/css/settlers.css" type="text/css" />

  <!-- Scripts -->
  <script src="https://www.google.com/jsapi?key=ABQIAAAAnT7bvt5eCgJnKE_9xHtWrRQL0gKz-n891IYmna21nNIOzPZZixRfXXTxioGg6bd4WAedyIJq9y470A" type="text/javascript"></script>

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.js" type="text/javascript"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.9.0/jquery-ui.min.js" type="text/javascript"></script>

  <script type="text/javascript" src="/static/script/jquery.form.js"></script>
  <script type="text/javascript" src="/static/script/jquery.timers.js"></script>
  <script type="text/javascript" src="/static/script/stacktrace.js"></script>

  <script type="text/javascript" src="/static/script/mustache.js"></script>
  <script type="text/javascript" src="/static/script/strftime.js"></script>

  <script type="text/javascript" src="/static/script/hlib.js"></script>
  <script type="text/javascript" src="/static/script/settlers.js"></script>
  <script type="text/javascript" src="/static/script/pages/page.js"></script>

  <meta name="google-site-verification" content="wA0CBzot_CglwqnQRXErsh8JDRgkX9FhbhnmPyaxtOA" />

  % if self.uri.startswith('games/'):
    <%
      kind = self.uri.split('/')[1].split('.')[0]
    %>

    <link rel="stylesheet" href="/static/css/pages/game.css" type="text/css" />
    <link rel="stylesheet" href="/static/css/games/${kind}/${kind}.css" type="text/css" />
    <link rel="stylesheet" href="/static/css/games/${kind}/${kind}-board.css" type="text/css" />

    <script type="text/javascript" src="/static/script/pages/game.js"></script>
    <script type="text/javascript" src="/static/script/games/${kind}/${kind}.js"></script>
    <script type="text/javascript" src="/static/script/games/${kind}/${kind}-board.js"></script>
  % endif

  <%
    current_page_name = next.name.split(':')[1].split('.')[0]

    page_script_file = os.path.join(hruntime.app.config['dir'], 'static', 'script', 'pages', current_page_name + '.js')
    page_style_file = os.path.join(hruntime.app.config['dir'], 'static', 'css', 'pages', current_page_name + '.css')
  %>

  % if os.path.exists(page_style_file):
    <link rel="stylesheet" href="/static/css/pages/${current_page_name}.css" type="text/css" />
  % endif

  % if os.path.exists(page_script_file):
    <script type="text/javascript" src="/static/script/pages/${current_page_name}.js"></script>
  % endif

  <script src="/i18n?lang=${hruntime.i18n.name}" type="text/javascript"></script>

  ${parent.page_header()}

  <script type="text/javascript">
    window.settlers = window.settlers || {};

    window.settlers.title = window.hlib._g("${hruntime.app.config['label']}");

    % if hruntime.user != None:
      window.settlers.user = {
        name:			"${hruntime.user.name}"
      };
    % endif
  </script>

<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-615278-7']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>

</%def>

<%def name="page_title()">
  ${_(hruntime.app.config['title'])}
</%def>

##
## Start rendering
##

<%def name="powered_by(link, img, label)">
  <a href="http://${link}/"><img src="/static/images/poweredby/${img}" alt="${label}" /></a>
</%def>

<%def name="page_header_public()">
  <div class="container-fluid">
</%def>

<%def name="menu_entry(icon, label, href = None, id = None)">
  <%
    href = href or '#'
    id = 'id="' + id + '"' if id else ''
  %>

  <a class="win-command" href="${href}" title="${_(label)}" rel="tooltip" data-placement="top" ${id} style="position: relative">
    <span class="win-commandimage win-commandring">${icon}</span>
    <span class="win-label">${_(label)}</span>
    % if len(id) > 0:
      <span class="badge badge-important menu-alert"></span>
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
          ${menu_entry('&#x0021;', 'Home', href = '/home/', id = 'menu_home')}
          ${menu_entry('&#xe03e;', 'New ...', href = '/new/')}
          ${menu_entry('&#xe20d;', 'Board', href = '/chat/', id = 'menu_chat')}
          ${menu_entry('&#x0072;', 'Stats', href = '/stats/')}
          ${menu_entry('&#x0070;', 'Settings', href = '/settings/')}

          <hr class="win-command" />

          ${menu_entry('&#xe1a4;', 'Help', href = '/help/')}

          % if hruntime.user.is_admin:
            ${menu_entry('&#x006e;', 'Admin', href = '/admin/')}
            ${menu_entry('&#xe037;', 'Monitor', href = '/monitor/')}
            <hr class="win-command" />
          % endif
          ${menu_entry('&#xe040;', 'Log out', href = '/logout', id = 'menu_logout')}
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

% if False:
  <div class="row-fluid">
    <div class="offset3 span6 poweredby-box">
      ${powered_by('www.python.org', 'python-powered-w-100x40.png', 'Python')}
      ${powered_by('www.lighttpd.net', 'light_logo.png', 'Lighttpd')}
      ${powered_by('www.makotemplates.org', 'makoLogo.png', 'Mako Templates')}
      ${powered_by('www.jquery.com', 'powered_by-jquery.png', 'JQuery')}
      ${powered_by('jashkenas.github.com/coffee-script/', 'coffeescript_logo.png', 'CoffeeScript')}
    </div>
  </div>
% endif
</%def>

<div class="modal warning hide trumpet-board" tabindex="-1" role="dialog" aria-hidden="true" id="trumpet_board_dialog">
  <div class="modal-body">
    <p></p>
  </div>
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

<script src="/static/metro/scripts/jquery.mousewheel.js"></script>
<script src="/static/metro/scripts/jquery.scrollTo.js"></script>
<script src="/static/metro/scripts/bootstrap.js"></script>
<script src="/static/metro/scripts/bootmetro.js"></script>
<script src="/static/metro/scripts/bootmetro-charms.js"></script>
<script src="/static/metro/scripts/holder.js"></script>
<script src="/static/metro/scripts/bootstrap-datepicker.js"></script>
