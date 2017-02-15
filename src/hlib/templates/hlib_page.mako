<%!
  import types
  import sys
  import hlib.i18n

  import hruntime
%>

<%def name="quote(s)">${'"' + s + '"'}</%def>

<%def name="script_file(file, type)">
  <script type="text/javascript" src="/static/script/${file}.js"></script>
</%def>

<%def name="stylesheet(file)">
  <link rel="stylesheet" type="text/css" href="/static/css/${path}" />
</%def>

##
## Inheritance methods
##
<%def name="page_title()">
</%def>

<%def name="page_favicon(path_prefix = '/static/images/favicon/', tile_background = '#2b5797')">
  <link rel="apple-touch-icon" sizes="57x57" href="${path_prefix}/apple-touch-icon-57x57.png" />
  <link rel="apple-touch-icon" sizes="72x72" href="${path_prefix}/apple-touch-icon-72x72.png" />
  <link rel="apple-touch-icon" sizes="60x60" href="${path_prefix}/apple-touch-icon-60x60.png" />
  <link rel="apple-touch-icon" sizes="76x76" href="${path_prefix}/apple-touch-icon-76x76.png" />
  <link rel="icon" type="image/png" href="${path_prefix}/favicon-16x16.png" sizes="16x16" />
  <link rel="icon" type="image/png" href="${path_prefix}/favicon-32x32.png" sizes="32x32" />
  <link rel="icon" type="image/png" href="${path_prefix}/favicon-96x96.png" sizes="96x96" />
  <meta name="msapplication-TileColor" content="${tile_background}" />
  <meta name="msapplication-square70x70logo" content="${path_prefix}/mstile-70x70.png" />
</%def>

<%def name="page_style()">
</%def>

<%def name="page_script()">
</%def>

<%def name="page_header()">
  <title>${self.page_title()}</title>

  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

</%def>

<%def name="page_pre_body()">
</%def>

<%def name="page_post_body()">
</%def>

<%def name="page_footer()">
</%def>


<!doctype html>
<!-- paulirish.com/2008/conditional-stylesheets-vs-css-hacks-answer-neither/ -->
<!--[if lt IE 7]><html class="no-js lt-ie9 lt-ie8 lt-ie7"><![endif]-->
<!--[if IE 7]><html class="no-js lt-ie9 lt-ie8"><![endif]-->
<!--[if IE 8]><html class="no-js lt-ie9"><![endif]-->
  <head>
    ${self.page_header()}
  </head>

  <body>
    ${self.page_pre_body()}

    ${next.body()}

    ${self.page_post_body()}

    <script type="text/javascript">
      $(document).ready(function() {
        $(window).trigger('hlib_prestartup');
        $(window).trigger('page_prestartup');
        $(window).trigger('hlib_startup');
        $(window).trigger('page_startup');
        $(window).trigger('hlib_poststartup');
        $(window).trigger('page_poststartup');
      });
    </script>
  </body>
</html>
