<%namespace file="lib.mako"          import="*"/>
<%namespace file="hlib_widgets.mako" import="*"/>

<%inherit file="page.mako" />

${page_content_start()}

${chat_new_post('/chat')}

</div>
<div class="span-14">

${chat_table(14)}

${page_content_end()}
