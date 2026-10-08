#!/usr/bin/env python3
"""Genera site/data/feed.json y feed.js con publicaciones reales de TikTok, Instagram y Facebook.

Estrategia por red (cada una independiente; si falla se conserva la ultima tanda buena):
  - TikTok   : urlebird (ids + fechas) -> oEmbed oficial (titulo + miniatura) -> descarga miniatura.
  - Instagram: RSS-Bridge publico (varias instancias, con failover) -> Atom con fecha + miniatura.
  - Facebook : RSS-Bridge publico (suele fallar: Facebook exige sesion) -> si falla, se conserva lo previo.

Todo corre en la nube (GitHub Actions) sin tokens y sin depender de ninguna PC.

Uso:
  python tools/build_feed.py                 # TikTok + Instagram
  python tools/build_feed.py --with-fb       # intenta tambien Facebook
  python tools/build_feed.py --only tt,ig    # solo algunas
  python tools/build_feed.py --check         # no escribe nada, imprime el feed
"""
import argparse
import datetime
import html as _html
import json
import os
import re
import sys
import urllib.parse

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

# Instancias publicas de RSS-Bridge con failover (gratis, server-side, sin token).
RSS_BRIDGES = [
    'https://rss-bridge.org/bridge01',
    'https://rss-bridge.sans-nuage.fr',
    'https://rss-bridge.ggc-project.de',
    'https://rss.bloat.cat',
    'https://rss-bridge.lewd.tech',
]

FB_PAGE = 'Unen-Industrial-61594093749350'
FB_PAGE_URL = 'https://www.facebook.com/' + FB_PAGE

# Fuente externa de Facebook (hoja de calculo publicada como CSV o un feed
# Atom/RSS). Si esta vacia, el comportamiento es el de siempre: se conserva
# la ultima tanda buena. Se configura con la variable de repositorio FB_FEED_URL.
FB_FEED_URL = os.environ.get('FB_FEED_URL', '').strip()


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


def fetch_image(url, dest, timeout=40):
    """Descarga una imagen; si el origen la bloquea, reintenta por el proxy wsrv.nl."""
    candidates = [url]
    if 'wsrv.nl' not in url and 'weserv.nl' not in url:
        candidates.append('https://wsrv.nl/?url=' + requests.utils.quote(url, safe=''))
    for attempt in candidates:
        try:
            r = requests.get(attempt, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            ctype = (r.headers.get('content-type') or '')
            if len(r.content) < 512 or (ctype and 'image' not in ctype):
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(r.content)
            return os.path.relpath(dest, SITE).replace('\\', '/')
        except Exception as e:
            print('[warn] imagen %s: %s' % (attempt[:48], e))
    return None


def html_to_text(html):
    """Convierte el <content> de un Atom (con <img>/<br>/entidades) a texto plano."""
    txt = re.sub(r'<br\s*/?>', '\n', html or '', flags=re.I)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = _html.unescape(txt)
    return re.sub(r'\s+', ' ', txt).strip()


def parse_atom(xml_text):
    """Atom de RSS-Bridge -> [{cap, url, when, thumb}], ignorando entradas de error."""
    import xml.etree.ElementTree as ET
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_text)
    out = []
    for e in root.findall('a:entry', ns):
        title = (e.findtext('a:title', '', ns) or '').strip()
        content = e.findtext('a:content', '', ns) or ''
        if 'Bridge returned error' in title or 'Unable to find anything useful' in content:
            continue
        link, thumb = '', ''
        for l in e.findall('a:link', ns):
            rel = l.get('rel')
            if rel in (None, 'alternate') and not link:
                link = l.get('href') or ''
            if rel == 'enclosure' and not thumb:
                thumb = l.get('href') or ''
        if not link:
            link = (e.findtext('a:id', '', ns) or '').strip()
        if not thumb:
            m = re.search(r'(?:src|poster)="([^"]+)"', content)
            if m:
                thumb = m.group(1)
        when = None
        for tag in ('a:published', 'a:updated'):
            s = e.findtext(tag, '', ns)
            if s:
                try:
                    when = datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
                    break
                except Exception:
                    pass
        cap = html_to_text(content) or title
        cap = strip_hashtags(cap.lstrip('▶ ').strip())
        out.append({'cap': cap, 'url': link, 'when': when, 'thumb': thumb})
    return out


def bridge_atom(bridge, params):
    """Pide un Atom a una instancia de RSS-Bridge y devuelve sus entradas."""
    url = bridge + '/?action=display&' + urllib.parse.urlencode(params) + '&format=Atom'
    r = requests.get(url, headers=HEADERS, timeout=40)
    r.raise_for_status()
    return parse_atom(r.text)


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
def fetch_instagram(limit=4):
    """Instagram por RSS-Bridge publico (varias instancias con failover)."""
    for bridge in RSS_BRIDGES:
        try:
            rows = bridge_atom(bridge, {
                'bridge': 'InstagramBridge',
                'context': 'Username',
                'u': IG_USER,
            })
        except Exception as e:
            print('[warn] ig %s: %s' % (bridge, e))
            continue
        posts = []
        for row in rows[:limit]:
            if not row['url'] or '/p/' not in row['url'] and '/reel/' not in row['url']:
                continue
            img = None
            if row['thumb']:
                ident = re.sub(r'[^A-Za-z0-9_-]', '', row['url'].rstrip('/').split('/')[-1]) or 'p'
                img = fetch_image(row['thumb'], os.path.join(POSTS, slug('ig', ident) + '.jpg'))
            posts.append(normalize('ig', row['cap'], row['url'], when=row['when'], img=img))
        if posts:
            print('[ig] fuente: %s' % bridge)
            return posts
    return []


# ----------------------------------------------------------------- Facebook
def fetch_facebook(limit=3):
    """Facebook por RSS-Bridge publico. Suele fallar (Facebook exige sesion):
    en ese caso se conserva la ultima tanda buena (ver merge_keep_last_good)."""
    for bridge in RSS_BRIDGES:
        for user in (FB_PAGE, IG_USER):
            try:
                rows = bridge_atom(bridge, {
                    'bridge': 'FacebookBridge',
                    'context': 'User',
                    'u': user,
                })
            except Exception as e:
                print('[warn] fb %s: %s' % (bridge, e))
                continue
            posts = []
            for row in rows[:limit]:
                if len(row['cap']) < 12:
                    continue
                img = None
                if row['thumb']:
                    ident = re.sub(r'\D', '', row['url'])[:20] or 'fb'
                    img = fetch_image(row['thumb'], os.path.join(POSTS, slug('fb', ident) + '.jpg'))
                posts.append(normalize('fb', row['cap'], row['url'], when=row['when'], img=img))
            if posts:
                print('[fb] fuente: %s (%s)' % (bridge, user))
                return posts
    return []


# ------------------------------------------------- Facebook desde una hoja
_FB_COL_ALIASES = {
    'cap': ('caption', 'cap', 'texto', 'text', 'descripcion', 'titulo'),
    'url': ('url', 'enlace', 'link', 'permalink'),
    'fecha': ('fecha', 'date', 'tm', 'cuando'),
    'img': ('imagen', 'img', 'image', 'thumb', 'miniatura', 'foto'),
}


def _norm_key(s):
    return re.sub(r'[^a-z]', '', (s or '').strip().lower())


def parse_fb_date(s):
    """Acepta ISO, 'dd/mm/aaaa' o 'dd-mm-aaaa'. Devuelve datetime UTC o None."""
    s = (s or '').strip()
    if not s:
        return None
    try:
        dt = datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
        return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)
    except Exception:
        pass
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y'):
        try:
            return datetime.datetime.strptime(s, fmt).replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue
    return None


def parse_fb_table(text):
    """Lee una tabla CSV/TSV con encabezados, o un Atom/RSS. Devuelve filas
    {cap, url, when, img_url}. Tolera encabezados con acentos o mayusculas."""
    stripped = (text or '').lstrip('\ufeff \t\r\n')
    if not stripped:
        return []
    if stripped.startswith('<'):
        return [{'cap': r['cap'], 'url': r['url'], 'when': r['when'], 'img_url': r['thumb']}
                for r in parse_atom(text)]
    import csv as _csv
    import io as _io
    sample = stripped[:4000]
    delim = '\t' if sample.count('\t') > sample.count(',') else ','
    table = [r for r in _csv.reader(_io.StringIO(stripped), delimiter=delim)
             if any((c or '').strip() for c in r)]
    if not table:
        return []
    header = [_norm_key(c) for c in table[0]]
    idx = {}
    for key, aliases in _FB_COL_ALIASES.items():
        wanted = [_norm_key(a) for a in aliases]
        for i, h in enumerate(header):
            if h in wanted:
                idx[key] = i
                break
    if 'cap' in idx or 'url' in idx:
        body = table[1:]
    else:
        idx = {'cap': 0, 'url': 1, 'fecha': 2, 'img': 3}
        body = table
    out = []
    for r in body:
        def cell(k):
            i = idx.get(k)
            return r[i].strip() if i is not None and i < len(r) else ''
        cap, url = cell('cap'), cell('url')
        if not cap and not url:
            continue
        out.append({'cap': cap, 'url': url,
                    'when': parse_fb_date(cell('fecha')),
                    'img_url': cell('img')})
    return out


def fetch_facebook_sheet(url, limit=3):
    """Facebook desde una hoja publicada (CSV) o un feed Atom/RSS externo."""
    r = requests.get(url, timeout=40, headers=HEADERS)
    r.raise_for_status()
    posts = []
    for i, row in enumerate(parse_fb_table(r.text)):
        cap = row['cap']
        if len(cap) < 12:
            continue
        img = None
        if row.get('img_url'):
            ident = re.sub(r'\D', '', row.get('url') or '')[:20] or str(i)
            img = fetch_image(row['img_url'], os.path.join(POSTS, slug('fb', ident) + '.jpg'))
        posts.append(normalize('fb', cap, row['url'], when=row.get('when'), img=img))
        if len(posts) >= limit:
            break
    return posts


# -------------------------------------------------------------------- build
FETCHERS = {'tt': fetch_tiktok, 'ig': fetch_instagram, 'fb': fetch_facebook}


def build(only=None, check=False, with_fb=False):
    old = load_old_feed() or {}
    old_pool = old.get('pool') or {}
    new_pool = {}
    for net in ORDER:
        wanted = (not only or net in only) and net in FETCHERS
        # Facebook: 1) hoja externa si esta configurada; 2) RSS-Bridge solo si lo piden.
        if net == 'fb':
            if FB_FEED_URL and (not only or 'fb' in only):
                try:
                    got = fetch_facebook_sheet(FB_FEED_URL) or []
                    print('[fb] fuente: hoja externa (%d publicaciones)' % len(got))
                    new_pool[net] = got
                except Exception as e:
                    print('[warn] fb hoja fallo: %s' % e)
                    new_pool[net] = []
                continue
            # Facebook casi siempre falla desde la nube: solo se intenta si lo piden.
            if not (with_fb or (only and 'fb' in only)):
                wanted = False
        if not wanted:
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
    ap.add_argument('--with-fb', action='store_true', help='intenta tambien Facebook')
    args = ap.parse_args(argv)
    only = [x.strip() for x in args.only.split(',') if x.strip()] or None
    return build(only=only, check=args.check, with_fb=args.with_fb)


if __name__ == '__main__':
    sys.exit(main())
