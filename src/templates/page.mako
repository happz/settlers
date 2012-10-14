<%!
  import os.path
  import sys

  import hlib
  import hruntime
%>

<%namespace file="lib.mako" import="*" />
<%namespace file="hlib_widgets.mako" import="*" />

<%inherit file="hlib_page.mako" />

<%def name="page_header()">
  <!-- Stylesheets -->
  <link rel="stylesheet" href="/static/css/reset.css" type="text/css" media="screen, projection" />
  <link rel="stylesheet" href="/static/css/settlers.css" type="text/css" media="screen, projection" />
  <!--[if lt IE 8]>
    <link rel="stylesheet" href="/static/css/ie.css" type="text/css" media="screen, projection" />
  <![endif]-->

  <link rel="stylesheet" href="/static/css/formee-structure.css" type="text/css" />
  <link rel="stylesheet" href="/static/css/formee-style.css" type="text/css" />

  <link rel="stylesheet" href="/static/css/settlers-icons.css" type="text/css" />

  % if hruntime.user != None:
    <link rel="stylesheet" href="/static/css/private.css" type="text/css" />
  % else:
    <link rel="stylesheet" href="/static/css/public.css" type="text/css" />
  % endif

  <!-- Scripts -->
  <script src="https://www.google.com/jsapi?key=ABQIAAAAnT7bvt5eCgJnKE_9xHtWrRQL0gKz-n891IYmna21nNIOzPZZixRfXXTxioGg6bd4WAedyIJq9y470A" type="text/javascript"></script>

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.js" type="text/javascript"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js" type="text/javascript"></script>

  <script type="text/javascript" src="/static/script/jquery.form.js"></script>
  <script type="text/javascript" src="/static/script/jquery.timers.js"></script>
  <script type="text/javascript" src="/static/script/stacktrace.js"></script>

  <script type="text/javascript" src="/static/script/mustache.js"></script>
  <script type="text/javascript" src="/static/script/strftime-min.js"></script>

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
    <link rel="stylesheet" href="/static/css/games/${kind}/${kind}-icons.css" type="text/css" />

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
</%def>

<%def name="page_header_private()">
  <div class="framed menu-widget">
    <div class="menu-info"><span class="user-name">${hruntime.user.name}</span></div>
    <hr />
    <div id="menu_home"><a href="/home/" title="${_('Home')}"><span class="icon icon-large icon-menu-home"><span class="menu-alert"></span></span></a></div>
    <div><a href="/new/" title="${_('New ...')}"><span class="icon icon-large icon-menu-add"></span></a></div>
    <div id="menu_chat"><a href="/chat/" title="${_('Chat')}"><span class="icon icon-large icon-menu-chat"><span class="menu-alert"></span></span></a></div>
    <div><a href="/stats/" title="${_('Stats')}"><span class="icon icon-large icon-menu-stats"></span></a></div>
    <div><a href="/settings/" title="${_('Settings')}"><span class="icon icon-large icon-menu-settings"></span></a></div>
    <div><hr /></div>
    <div><a href="/help/" title="${_('Help')}"><span class="icon icon-large icon-menu-help"></span></a></div>
    <div><hr /></div>
    % if hruntime.user.is_admin:
      <div><a href="/admin/" title="${_('Admin')}"><span class="icon icon-large icon-menu-admin"></span></a></div>
      <div><a href="/monitor/" title="${_('Monitor')}"><span class="icon icon-large icon-menu-monitor"></span></a></div>
      <div><hr /></div>
    % endif
    <div><a href="/logout/" id="menu_logout" title="${_('Log out')}"><span class="icon icon-large icon-menu-logout"></span></a></div>
  </div>
</%def>

<%def name="page_footer_private()">
</%def>

<%def name="page_footer_public()">
  <%
    current_page_name = next.name.split(':')[1].split('.')[0]
    if current_page_name == 'maintenance':
      return ''
  %>

  <div class="row">
    <div class="prepend-3 span-6 last" style="text-align: center">
      <a href="/login/">${_('Log in')}</a> | <a href="/registration/">${_('Registration')}</a> | <a href="/registration/recovery/">${_('Forgot password?')}</a> | <a href="/loginas/">${_('Admin login')}</a>
    </div>
  </div>

% if True:
  <div class="row">
    <div class="prepend-top prepend-3 span-6 last poweredby-box">
      ${powered_by('www.python.org', 'python-powered-w-100x40.png', 'Python')}
      ${powered_by('www.lighttpd.net', 'light_logo.png', 'Lighttpd')}
      ${powered_by('www.makotemplates.org', 'makoLogo.png', 'Mako Templates')}
      ${powered_by('www.jquery.com', 'powered_by-jquery.png', 'JQuery')}
      ${powered_by('jashkenas.github.com/coffee-script/', 'coffeescript_logo.png', 'CoffeeScript')}
      ${powered_by('formee.org', 'formee.png', 'Formee')}
    </div>
  </div>
% endif
</%def>

<div class="container">
  % if hruntime.user != None:
    ${page_header_private()}
  % else:
    ${page_header_public()}
  % endif

  <div class="row">
    <div id="trumpet_board" class="prepend-top prepend-3 span-6 last hide">
      <div class="formee-msg-info"></div>
    </div>
  </div>

  <div class="prepend-top append-bottom">
    ${next.body()}
  </div>

% if hruntime.user != None:
  ${page_footer_private()}
% else:
  ${page_footer_public()}
% endif
</div>

<div class="info-dialog formee hide"></div>

<span style="display: none" id="pull-notify"></span>
