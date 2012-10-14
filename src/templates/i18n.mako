<%!
  import hruntime
%>

window.settlers = window.settlers || {};
window.settlers.i18n = window.settlers.i18n || {};

window.settlers.i18n.${lang.name} = {
  % for key in lang.tokens.keys():
    '${key}': '${lang.tokens[key]}',
  % endfor
};

window.settlers.i18n.tokens = window.settlers.i18n.${lang.name};
