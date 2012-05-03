<%!
  import hruntime
%>

window.settlers = window.settlers || {};
window.settlers.i18n = window.settlers.i18n || {};

window.settlers.i18n.${lang.name} = {
  % for key in lang.tokens.iterkeys():
    '${key}': '${lang.tokens[key]}',
  % endfor
};
