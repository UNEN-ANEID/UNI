#!/usr/bin/env python3
"""Genera site/data/feed.json y feed.js con publicaciones reales de TikTok, Instagram y Facebook.

Estrategia por red (cada una independiente; si falla se conserva la ultima tanda buena):
  - TikTok   : urlebird (ids + fechas) -> oEmbed oficial (titulo + miniatura) -> descarga miniatura.
  - Instagram: Playwright headless (perfil publico) -> enlaces + alt (fecha/caption) -> miniatura.
  - Facebook : Playwright headless (Page Plugin) -> posts + imagen -> miniatura.

Uso:
  python tools/build_feed.py                 # todas las redes
  python tools/build_feed.py --only tt,ig    # solo algunas
  python tools/build_feed.py --check         # no escribe nada, imprime el feed
"""
import argparse
import datetime
import json
import os
import re
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)                      # .../site
POSTS = os.path.join(SITE, 'assets', 'posts')
DATA = os.path.join(SITE, 'data')
FEED_JSON = os.path.join(DATA, 'feed.json')
FEED_JS = os.path.join(DATA, 'feed.js')

ORDER = ['tt', 'ig', 'fb']
ROTATION_MS = 6000

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
HEADERS = {'User-Agent': UA, 'Accept-Language': 'es-ES,es;q=0.9'}

TT_HANDLE = 'unen.industrial.uni'
TT_VIDEO = 'https://www.tiktok.com/@%s/video/%s'
TT_OEMBED = 'https://www.tiktok.com/oembed?url='
URELBIRD = 'https://urlebird.com/user/%s/'

IG_USER = 'unen.industrial'
IG_URL = 'https://www.instagram.com/%s/' % IG_USER

FB_PAGE = 'Unen-Industrial-61594093749350'
FB_PAGE_URL = 'https://www.facebook.com/' + FB_PAGE
FB_PLUGIN = ('https://www.facebook.com/plugins/page.php?href=' +
             requests.utils.quote(FB_PAGE_URL, safe='') +
             '&tabs=timeline&width=400&height=900&small_header=true&hide_cover=false')


# ---------------------------------------------------------------- utilidades
def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def relative(when, now=None):
    """Fecha en espanol relativa y breve: 'hace 2 d', 'ayer', '12/09/2026'."""
    if when is None:
        return ''
    now = now or now_utc()
    s = int((now - when).total_seconds())
    if s < 60:
        return 'ahora'
    if s < 3600:
        return 'hace %d min' % (s // 60)
    if s < 86400:
        return 'hace %d h' % (s // 3600)
    d = s // 86400
    if d == 1:
        return 'ayer'
    if d < 7:
        return 'hace %d d' % d
    return when.strftime('%d/%m/%Y')


def slug(net, ident):
    return '%s_%s' % (net, re.sub(r'[^A-Za-z0-9_-]', '', str(ident))[:40])


def normalize(net, cap, url, when=None, img=None, st=None):
    post = {
        'net': net,
        'cap': re.sub(r'\s+', ' ', (cap or '')).strip()[:200],
        'url': url or '',
        'tm': relative(when),
    }
    if img:
        post['img'] = img
    if st:
        post['st'] = [str(x) for x in st]
    return post


FALLBACK_CAP = {
    'tt': 'Ver las ultimas publicaciones en TikTok',
    'ig': 'Ver las ultimas publicaciones en Instagram',
    'fb': 'Ver las ultimas publicaciones en Facebook',
}


def strip_hashtags(text):
    """Quita hashtags y espacios sobrantes de una caption de TikTok."""
    return re.sub(r'\s+', ' ', re.sub(r'\s*#\S+', '', text or '')).strip()


def merge_keep_last_good(old_pool, new_pool):
    old_pool = old_pool or {}
    new_pool = new_pool or {}
    merged = {}
    for net in ORDER:
        new = new_pool.get(net) or []
        merged[net] = new if new else (old_pool.get(net) or [])
    return merged


def load_old_feed():
    try:
        with open(FEED_JSON, encoding='utf-8') as f:
            j = json.load(f)
        return j if isinstance(j, dict) else None
    except Exception:
        return None


def write_feed(feed):
    os.makedirs(DATA, exist_ok=True)
    with open(FEED_JSON, 'w', encoding='utf-8') as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
        f.write('\n')
    body = json.dumps(feed, ensure_ascii=False, indent=2)
    js = ("(function (root) {\n  root.UNEN_FEED = " + body +
          ";\n})(typeof globalThis !== 'undefined' ? globalThis : this);\n")
    with open(FEED_JS, 'w', encoding='utf-8') as f:
        f.write(js)


def purge_orphans(keep):
    if not os.path.isdir(POSTS):
        return []
    removed = []
    for name in sorted(os.listdir(POSTS)):
        p = os.path.join(POSTS, name)
        if os.path.isfile(p) and ('assets/posts/' + name) not in keep:
            os.remove(p)
            removed.append(name)
    return removed


def download(url, dest, timeout=30):
    """Descarga directa (TikTok). Devuelve la ruta relativa a SITE."""
    r = requests.get(url, headers={**HEADERS, 'Referer': 'https://www.tiktok.com/'}, timeout=timeout)
    r.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        f.write(r.content)
    return os.path.relpath(dest, SITE).replace('\\', '/')


def save_via_ctx(ctx, url, dest, timeout=30000):
    """Descarga usando el contexto de Playwright (arrastra cookies de IG/FB)."""
    r = ctx.request.get(url, timeout=timeout)
    if r.status != 200:
        raise RuntimeError('http %s' % r.status)
    body = r.body()
    if len(body) < 512:
        raise RuntimeError('imagen muy pequena (%d bytes)' % len(body))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        f.write(body)
    return os.path.relpath(dest, SITE).replace('\\', '/')


def launch(pw):
    """Usa el Chrome del sistema si existe; si no, el Chromium de Playwright."""
    try:
        return pw.chromium.launch(channel='chrome')
    except Exception:
        return pw.chromium.launch()


def parse_es_relative(text, now=None):
    """'hace aproximadamente un mes' -> datetime."""
    if not text:
        return None
    now = now or now_utc()
    units = {'minuto': 60, 'min': 60, 'hora': 3600,
             'dia': 86400, 'día': 86400, 'dias': 86400, 'días': 86400,
             'semana': 604800, 'sem': 604800,
             'mes': 2592000, 'meses': 2592000,
             'ano': 31536000, 'año': 31536000, 'anos': 31536000, 'años': 31536000}
    m = re.search(r'hace\s+(?:aproximadamente\s+|m[áa]s de\s+|menos de\s+|casi\s+)?'
                  r'(un|una|uno|\d+)\s+([a-záéíóúñ]+)', text.lower())
    if not m:
        return None
    q = m.group(1)
    n = 1 if q in ('un', 'una', 'uno') else int(q)
    secs = units.get(m.group(2))
    return now - datetime.timedelta(seconds=n * secs) if secs else None


# ------------------------------------------------------------------- TikTok
def parse_urlebird(html):
    """Devuelve [(video_id, n, unidad)] unicos en orden, emparejados con las fechas."""
    vids, seen = [], set()
    for m in re.finditer(r'href="https://urlebird\.com/video/[^"]*?-(\d{15,})/"', html):
        v = m.group(1)
        if v not in seen:
            seen.add(v)
            vids.append(v)
    dates = re.findall(r'\b(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago\b', html)
    out = []
    for i, v in enumerate(vids):
        if i < len(dates):
            out.append((v, int(dates[i][0]), dates[i][1]))
        else:
            out.append((v, None, None))
    return out


def rel_to_dt(n, unit, now=None):
    now = now or now_utc()
    secs = {'second': 1, 'minute': 60, 'hour': 3600, 'day': 86400,
            'week': 604800, 'month': 2592000, 'year': 31536000}[unit]
    return now - datetime.timedelta(seconds=n * secs)


def fetch_tiktok(limit=4):
    r = requests.get(URELBIRD % TT_HANDLE, headers=HEADERS, timeout=40)
    r.raise_for_status()
    rows = parse_urlebird(r.text)[:limit]
    posts = []
    for vid, n, unit in rows:
        url = TT_VIDEO % (TT_HANDLE, vid)
        when = rel_to_dt(n, unit) if n else None
        cap, thumb = '', ''
        try:
            o = requests.get(TT_OEMBED + requests.utils.quote(url, safe=''),
                             headers=HEADERS, timeout=30)
            o.raise_for_status()
            j = o.json()
            cap = strip_hashtags(j.get('title') or '')
            thumb = j.get('thumbnail_url') or ''
        except Exception as e:
            print('[warn] tiktok oembed %s: %s' % (vid, e))
        img = None
        if thumb:
            try:
                img = download(thumb, os.path.join(POSTS, slug('tt', vid) + '.jpg'))
            except Exception as e:
                print('[warn] tiktok miniatura %s: %s' % (vid, e))
        posts.append(normalize('tt', cap, url, when=when, img=img))
    return posts


# ---------------------------------------------------------------- Instagram
_MONTHS_EN = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
              'august', 'september', 'october', 'november', 'december']
_MONTHS_ES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
              'agosto', 'septiembre', 'setiembre', 'octubre', 'noviembre', 'diciembre']
# Descripciones automaticas de accesibilidad de Instagram (no son captions reales).
_IG_AUTO = re.compile(r'^(Puede ser|Es posible que|Puede que|May be|No hay|'
                      r'Photo by|Video by|Imagen de|Foto de)', re.I)


def ig_alt_parse(alt):
    """'Video by X on October 05, 2026. <caption>' -> (datetime|None, caption)."""
    if not alt:
        return None, ''
    when, end = None, 0
    m = re.search(r'on\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', alt)
    if m and m.group(1).lower() in _MONTHS_EN:
        try:
            when = datetime.datetime(int(m.group(3)), _MONTHS_EN.index(m.group(1).lower()) + 1,
                                     int(m.group(2)), tzinfo=datetime.timezone.utc)
            end = m.end()
        except Exception:
            when = None
    if when is None:
        m = re.search(r'el\s+(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})', alt, re.I)
        if m and m.group(2).lower() in _MONTHS_ES:
            try:
                idx = _MONTHS_ES.index(m.group(2).lower())
                idx = 9 if idx == 10 else (10 if idx == 9 else idx)  # septiembre/setiembre
                when = datetime.datetime(int(m.group(3)), idx + 1, int(m.group(1)),
                                         tzinfo=datetime.timezone.utc)
                end = m.end()
            except Exception:
                when = None
    cap = alt[end:].lstrip(' .,:;').strip()
    # Instagram genera una descripcion automatica cuando el post no tiene caption real.
    if _IG_AUTO.match(cap):
        cap = ''
    return when, cap


def fetch_instagram(limit=4):
    from playwright.sync_api import sync_playwright
    posts = []
    with sync_playwright() as pw:
        b = launch(pw)
        ctx = b.new_context(locale='es-ES')
        pg = ctx.new_page()
        pg.goto(IG_URL, wait_until='domcontentloaded', timeout=60000)
        pg.wait_for_timeout(3500)
        for _ in range(3):
            pg.mouse.wheel(0, 1200)
            pg.wait_for_timeout(1200)
        rows = pg.evaluate("""() => {
          const out = [], seen = new Set();
          document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]').forEach(a => {
            const img = a.querySelector('img');
            if (!img) return;
            const href = a.href.split('?')[0];
            if (seen.has(href)) return;
            seen.add(href);
            out.push({ url: href, alt: img.alt || '', src: img.src || '' });
          });
          return out;
        }""")
        for row in rows[:limit]:
            when, cap = ig_alt_parse(row['alt'])
            img = None
            if row['src']:
                ident = row['url'].rstrip('/').split('/')[-1] or 'p'
                try:
                    img = save_via_ctx(ctx, row['src'], os.path.join(POSTS, slug('ig', ident) + '.jpg'))
                except Exception as e:
                    print('[warn] instagram miniatura %s: %s' % (ident, e))
            posts.append(normalize('ig', cap, row['url'], when=when, img=img))
        b.close()
    return posts


# ----------------------------------------------------------------- Facebook
_FB_NOISE = re.compile(r'^(\d[\d.,]*\s*(seguidores|me gusta|comentarios|personas)|'
                       r'hace\s|Se un[ií][oó]|Ver m[áa]s|Me gusta|Comentar|Compartir|'
                       r'Todas las reacciones|UNEN Industrial UNI|Unen-Industrial|Facebook)$', re.I)
# Cabecera del post: "Unen-Industrial hace aproximadamente un mes".
_FB_HEAD = re.compile(r'^.*?hace\s+(?:aproximadamente\s+|m[áa]s de\s+|menos de\s+|casi\s+)?'
                      r'(?:un|una|uno|\d+)\s+[a-záéíóúñ]+\s*', re.I)


def fb_clean_text(text):
    lines = [l.strip() for l in (text or '').splitlines()]
    keep = [l for l in lines if l and not _FB_NOISE.match(l)]
    cap = _FB_HEAD.sub('', ' '.join(keep)).strip()
    return re.sub(r'\s+', ' ', cap)


def fetch_facebook(limit=3):
    from playwright.sync_api import sync_playwright
    posts = []
    with sync_playwright() as pw:
        b = launch(pw)
        ctx = b.new_context(locale='es-ES', viewport={'width': 420, 'height': 1000})
        pg = ctx.new_page()
        pg.goto(FB_PLUGIN, wait_until='domcontentloaded', timeout=60000)
        pg.wait_for_timeout(4500)
        for _ in range(4):
            pg.mouse.wheel(0, 1500)
            pg.wait_for_timeout(1200)
        rows = pg.evaluate("""() => {
          const out = [], seen = new Set();
          document.querySelectorAll('.userContentWrapper').forEach(w => {
            const txt = (w.innerText || '').trim();
            if (!txt) return;
            const link = w.querySelector('a[href*="/posts/"], a[href*="story_fbid"], a[href*="/photos/"]');
            const url = link ? link.href.split('&__cft__')[0] : '';
            if (url && seen.has(url)) return;
            if (url) seen.add(url);
            let best = '', area = 0;
            w.querySelectorAll('img').forEach(im => {
              const a = (im.naturalWidth || 0) * (im.naturalHeight || 0);
              if (a > area) { area = a; best = im.src; }
            });
            out.push({ text: txt, url: url, src: best });
          });
          return out;
        }""")
        for row in rows[:limit]:
            when = parse_es_relative(row['text'])
            cap = fb_clean_text(row['text'])
            if len(cap) < 12:
                continue
            url = re.sub(r'[&?]ref=embed_page.*$', '', row['url'])
            img = None
            if row['src'] and 'emoji' not in row['src']:
                ident = re.sub(r'\D', '', url)[:20] or 'fb'
                try:
                    img = save_via_ctx(ctx, row['src'], os.path.join(POSTS, slug('fb', ident) + '.jpg'))
                except Exception as e:
                    print('[warn] facebook miniatura: %s' % e)
            posts.append(normalize('fb', cap, url, when=when, img=img))
        b.close()
    return posts


# -------------------------------------------------------------------- build
FETCHERS = {'tt': fetch_tiktok, 'ig': fetch_instagram, 'fb': fetch_facebook}


def build(only=None, check=False):
    old = load_old_feed() or {}
    old_pool = old.get('pool') or {}
    new_pool = {}
    for net in ORDER:
        if (only and net not in only) or net not in FETCHERS:
            new_pool[net] = old_pool.get(net) or []
            continue
        try:
            got = FETCHERS[net]() or []
            print('[%s] %d publicaciones' % (net, len(got)))
            new_pool[net] = got
        except Exception as e:
            print('[warn] %s fallo: %s' % (net, e))
            new_pool[net] = []

    pool = merge_keep_last_good(old_pool, new_pool)
    for net in ORDER:
        for p in pool.get(net) or []:
            if not p.get('cap'):
                p['cap'] = FALLBACK_CAP.get(net, '')
    feed = {
        'generatedAt': now_utc().replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'rotationMs': ROTATION_MS,
        'order': ORDER,
        'pool': pool,
    }

    if check:
        print(json.dumps(feed, ensure_ascii=False, indent=2)[:1200])
        return 0

    write_feed(feed)
    keep = set()
    for net in ORDER:
        for p in pool.get(net) or []:
            if p.get('img'):
                keep.add(p['img'])
    removed = purge_orphans(keep)
    print('feed: %s | purgadas: %s' % ({n: len(pool.get(n) or []) for n in ORDER}, removed))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Genera el feed real de la pagina E.')
    ap.add_argument('--check', action='store_true', help='no escribe, solo imprime')
    ap.add_argument('--only', default='', help='lista separada por comas: tt,ig,fb')
    args = ap.parse_args(argv)
    only = [x.strip() for x in args.only.split(',') if x.strip()] or None
    return build(only=only, check=args.check)


if __name__ == '__main__':
    sys.exit(main())
