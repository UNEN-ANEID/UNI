(function (root, factory) {
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.Carrusel = factory(); }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  function nextIndex(cur, total) { return total ? (cur + 1) % total : 0; }
  function cyclePool(cur, len) { return len ? (cur + 1) % len : 0; }
  function orderSlides(present, order) {
    var pref = order.filter(function (n) { return present.indexOf(n) >= 0; });
    var rest = present.filter(function (n) { return pref.indexOf(n) < 0; });
    return pref.concat(rest);
  }
  function activeNets(present, pool) {
    pool = pool || {};
    return present.filter(function (n) { return Array.isArray(pool[n]) && pool[n].length > 0; });
  }
  function wrap(n, total) { return total ? ((n % total) + total) % total : 0; }
  return { nextIndex: nextIndex, cyclePool: cyclePool, orderSlides: orderSlides, activeNets: activeNets, wrap: wrap };
});
