(function () {
  'use strict';

  // ---------- Enlaces ----------
  function renderLinks() {
    var list = document.querySelector('#p4phone .lklist');
    if (!list || !window.UNEN_LINKS || !window.Render) return;
    var order = ['whatsappDirecto', 'instagram', 'facebook', 'tiktok', 'whatsapp'];
    var html = '';
    order.forEach(function (key) {
      var cfg = window.UNEN_LINKS[key];
      if (!cfg) return;
      html += window.Render.linkButtonHTML(cfg.net, cfg);
    });
    list.innerHTML = html;
  }

  // ---------- Carrusel ----------
  function netOf(el) { return el.getAttribute('data-net'); }

  function fillSlide(slide, post) {
    var cap = slide.querySelector('.cap');
    var tm = slide.querySelector('.tm');
    var dur = slide.querySelector('.dur');
    var st = slide.querySelector('.st');
    var m = slide.querySelector('.m');
    if (cap) cap.innerHTML = window.Render.safeCaption(post.cap);
    if (tm) { tm.textContent = post.tm || ''; tm.style.display = post.tm ? '' : 'none'; }
    if (dur) { dur.textContent = post.dur || ''; dur.style.display = post.dur ? '' : 'none'; }
    if (st) {
      st.innerHTML = (post.st || []).map(function (v) { return '<span><b>' + v + '</b></span>'; }).join('');
      st.style.display = (post.st && post.st.length) ? '' : 'none';
    }
    if (m) {
      var img = m.querySelector('img.thumb');
      if (post.img) {
        if (img) { img.src = post.img; }
        else { m.insertAdjacentHTML('afterbegin', window.Render.thumbHTML(post)); }
      } else if (img) { img.parentNode.removeChild(img); }
    }
    var old = slide.querySelector('.open');
    if (old) old.parentNode.removeChild(old);
    if (post.url) slide.insertAdjacentHTML('beforeend', window.Render.slideLinkHTML(post));
  }

  function startCarousel(feed) {
    var phone = document.getElementById('p4phone');
    if (!phone || !feed || !feed.pool) return;
    var track = phone.querySelector('.car .track');
    if (!track) return;

    var allSlides = [].slice.call(track.querySelectorAll('.sl'));
    var present = window.Carrusel.activeNets(allSlides.map(netOf), feed.pool);
    if (!present.length) present = allSlides.map(netOf); // respaldo: no dejar el carrusel en blanco
    var order = window.Carrusel.orderSlides(present, feed.order || present);

    // Reordenar el DOM segun 'order' y ocultar slides sin publicaciones.
    allSlides.forEach(function (s) { s.style.display = 'none'; });
    var slides = order.map(function (net) {
      var s = allSlides.filter(function (x) { return netOf(x) === net; })[0];
      if (s) { s.style.display = ''; track.appendChild(s); }
      return s;
    }).filter(Boolean);

    if (!slides.length) return;

    // Puntos: uno por slide activo.
    var dotsWrap = phone.querySelector('.car .dots');
    if (dotsWrap) {
      dotsWrap.innerHTML = slides.map(function (_, i) {
        return '<i' + (i === 0 ? ' class="on"' : '') + '></i>';
      }).join('');
    }
    var dots = [].slice.call(phone.querySelectorAll('.car .dots i'));

    // Rotulo con la fecha real de la ultima actualizacion del feed.
    var liveTxt = phone.querySelector('.car .live-txt');
    if (liveTxt && feed.generatedAt) {
      var gd = new Date(feed.generatedAt);
      if (!isNaN(gd.getTime())) {
        var txt = gd.toLocaleDateString('es', { day: '2-digit', month: 'long', year: 'numeric' });
        liveTxt.textContent = 'Actividad de las redes · actualizado ' + txt;
      }
    }

    var poolIdx = { tt: 0, ig: 0, fb: 0 };
    var cur = 0;
    var lap = 0;
    var reduce = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

    function paint(slide) {
      var net = netOf(slide);
      var pool = feed.pool[net] || [];
      if (pool.length) fillSlide(slide, pool[poolIdx[net] % pool.length]);
    }

    // Prellenar cada slide con la publicacion mas reciente de su red.
    slides.forEach(paint);

    function go(n) {
      cur = window.Carrusel.wrap(n, slides.length);
      track.style.transform = 'translateX(' + (-cur * 100) + '%)';
      dots.forEach(function (d, i) { d.className = (i === cur) ? 'on' : ''; });
      var cap = slides[cur].querySelector('.cap');
      if (cap && !reduce) { cap.classList.remove('fresh'); void cap.offsetWidth; cap.classList.add('fresh'); }
      // Cada vuelta completa rota a la siguiente publicacion de cada red.
      if (cur === 0 && lap > 0) {
        slides.forEach(function (sl) {
          var net = netOf(sl);
          poolIdx[net] = (poolIdx[net] || 0) + 1;
          paint(sl);
        });
      }
      lap++;
    }

    go(0);
    var ms = feed.rotationMs || 6000;
    if (!reduce) setInterval(function () { go(cur + 1); }, ms);
  }

  // ---------- Datos con fallback ----------
  // Solo se usa un feed si tiene al menos una red con publicaciones.
  function isValidFeed(f) {
    if (!f || typeof f !== 'object' || !f.pool || typeof f.pool !== 'object') return false;
    for (var k in f.pool) {
      if (Object.prototype.hasOwnProperty.call(f.pool, k) && Array.isArray(f.pool[k]) && f.pool[k].length > 0) return true;
    }
    return false;
  }

  function initShareButton() {
    var btn = document.getElementById('btnShare');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var shareData = {
        title: 'UNEN Industrial | Enlaces Oficiales',
        text: 'Canales oficiales y publicaciones de UNEN Industrial - UNI',
        url: window.location.href
      };
      if (typeof navigator !== 'undefined' && navigator.share) {
        navigator.share(shareData).catch(function () {});
      } else if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(window.location.href).then(function () {
          var span = btn.querySelector('span');
          if (span) {
            var old = span.textContent;
            span.textContent = '¡Enlace copiado!';
            setTimeout(function () { span.textContent = old; }, 2200);
          }
        }).catch(function () {});
      }
    });
  }

  function load() {
    initShareButton();
    renderLinks();
    var fallback = isValidFeed(window.UNEN_FEED) ? window.UNEN_FEED : null;

    function use(feed) { startCarousel(isValidFeed(feed) ? feed : fallback); }

    if (typeof fetch === 'function') {
      fetch('data/feed.json', { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error('no feed.json')); })
        .then(function (j) { use(j); })
        .catch(function () { use(fallback); });
    } else {
      use(fallback);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
