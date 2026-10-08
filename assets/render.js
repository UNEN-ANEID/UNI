(function (root, factory) {
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.Render = factory(); }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  var ICONS = {
    ig: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/></svg>',
    fb: '<svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-fb"/></svg>',
    tt: '<svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-tt"/></svg>',
    wa: '<svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-wa"/></svg>'
  };

  function iconSVG(net) { return ICONS[net] || ICONS.ig; }

  // Escapa & < > " y luego restaura unicamente <em> y </em>.
  function safeCaption(str) {
    var s = String(str == null ? '' : str);
    s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    s = s.replace(/&lt;(\/?em)&gt;/g, '<$1>');
    return s;
  }

  function linkButtonHTML(net, cfg) {
    var isPlaceholder = !cfg.url || cfg.url === '#';
    var attrs = isPlaceholder
      ? ' aria-disabled="true" tabindex="-1"'
      : ' href="' + cfg.url + '" target="_blank" rel="noopener"';
    return '<a class="lk2"' + attrs + '>' +
      '<div class="chipl ' + net + '">' + iconSVG(net) + '</div>' +
      '<div class="tx">' + cfg.label + '<small>' + cfg.handle + '</small></div>' +
      '<div class="led"></div>' +
      '</a>';
  }

  function thumbHTML(post) {
    if (!post || !post.img) return '';
    return '<img class="thumb" src="' + post.img + '" alt="" loading="lazy" decoding="async">';
  }

  function slideLinkHTML(post) {
    if (!post || !post.url) return '';
    var label = (post.cap ? String(post.cap) : 'Ver publicación').slice(0, 80).replace(/"/g, '&quot;');
    return '<a class="open" href="' + post.url + '" target="_blank" rel="noopener" ' +
      'aria-label="' + label + '"></a>';
  }

  return { iconSVG: iconSVG, linkButtonHTML: linkButtonHTML, safeCaption: safeCaption,
           thumbHTML: thumbHTML, slideLinkHTML: slideLinkHTML };
});
