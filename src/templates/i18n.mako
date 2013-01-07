window.settlers = window.settlers || {};

window.settlers.i18n_table = {
  % for key in lang.tokens.keys():
    '${key}': '${lang.tokens[key]}',
  % endfor
};
