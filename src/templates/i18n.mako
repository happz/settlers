<%!
  import hruntime
%>

window.settlers = window.settlers || {};
window.settlers.i18n = window.settlers.i18n || {};

window.settlers.i18n.${hruntime.i18n.name} = {
  % for key in hruntime.i18n.tokens.iterkeys():
    '${key}': '${hruntime.i18n.tokens[key]}',
  % endfor
};
