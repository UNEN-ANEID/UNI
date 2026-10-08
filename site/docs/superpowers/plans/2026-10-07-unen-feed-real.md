# Feed Real Automatizado (UNEN Industrial, página E) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar los datos de demostración del carrusel por publicaciones reales de TikTok, Instagram y Facebook, actualizadas a diario por GitHub Actions y publicadas en GitHub Pages, sin costo y sin romper la página si una red falla.

**Architecture:** La página E (estática, cero build) se mueve dentro del repo `UNI` en `site/`. Un script Python (`tools/build_feed.py`) corre en un GitHub Action diario, consulta cada red por separado (TikTok oEmbed, Instagram vía RSS-Bridge, Facebook vía Playwright), descarga las miniaturas al repo y escribe `site/data/feed.json` y `feed.js` con los mismos datos reales, conservando la última tanda buena de cada red si falla. La página lee `feed.json` (o `feed.js` en `file://`) y renderiza miniatura real, enlace real y métricas solo si son reales.

**Tech Stack:** HTML/CSS/JS sin dependencias (navegador + Node `node:test`); Python 3.13 (`requests`, `playwright`) con `unittest`; GitHub Actions + GitHub Pages.

**Spec:** `site/docs/superpowers/specs/2026-10-07-unen-feed-real-design.md`

## Global Constraints

- CSS E **verbatim**: no cambiar reglas existentes de `assets/estilo.css`; solo **añadir** reglas nuevas al final.
- **Cero build** para la página; **cero dependencias runtime** en el navegador; debe funcionar en `file://`.
- UI en **español**; mensajes de commit en **español**.
- **No tocar** `mockups/` ni el presentador A–F (`entregable/index.html`, `entregable/mockup.html`, `entregable/logo.png`).
- Orden de slides: `['tt','ig','fb']`. WhatsApp **fuera** del carrusel (su botón de enlace se conserva).
- Esquema de feed v2: `{ generatedAt, rotationMs, order, pool }`; cada post `{ net, cap, url, tm, img?, st? }` (`img` y `st` opcionales).
- Cada red es independiente: si falla, **conserva la última tanda buena**; nunca se escribe un feed vacío.
- Repo destino: `C:\Users\--X\Desktop\PILAR\entregable` (clone de `github.com/WalterSolorzano/UNI`, rama `main`). Comandos git vía `& 'C:\Program Files\Git\cmd\git.exe'` (el shim del shell rompe con `;`).
- Costo **cero**; sin backend, sin login, sin tokens.

## Review Focus

1. **`file://` sin red**: al abrir `site/index.html` con doble clic, `fetch('data/feed.json')` falla → debe caer a `feed.js` (datos reales del último build) sin errores visibles ni carrusel vacío.
2. **Red sin publicaciones ese día**: si `pool.tt` (o ig/fb) queda vacío y no hay tanda previa, el carrusel debe **omitir** esa red y los dots deben coincidir con los slides visibles.
3. **Post sin métricas o sin fecha**: TikTok/IG no dan likes/fecha → la fila `.st` y el `.tm`/`.dur` deben **ocultarse** (no mostrar cajas vacías ni "0").
4. **Miniatura rota/ausente**: si `img` no existe o no carga, el slide debe mostrar el **degradado** actual, no un hueco.
5. **Datos sucios de origen** (caption con `<`, `&`, saltos, muy largo): deben verse como **texto literal** (saneados) y no romper el layout a 320 px.

---

### Task 1: Migrar `site/` al repo UNI, hacerlo público y activar Pages

**Files:**
- Create: `site/**` (copia de `C:\Users\--X\Desktop\PILAR\site`, sin su `.git`)
- Modify: (ninguno del presentador)

**Interfaces:**
- Consumes: nada.
- Produces: repo UNI con `site/` versionado en `main`, público, con Pages sirviendo `/UNI/site/`. Todas las tareas siguientes trabajan en `C:\Users\--X\Desktop\PILAR\entregable`.

- [ ] **Step 1: Verificar el clon destino**

Run (workdir `C:\Users\--X\Desktop\PILAR\entregable`):
```
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
```
Expected: `## main...origin/main` sin cambios pendientes.

- [ ] **Step 2: Copiar la página al repo (sin `.git`)**

Run:
```
robocopy "C:\Users\--X\Desktop\PILAR\site" "C:\Users\--X\Desktop\PILAR\entregable\site" /E /XD .git /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw "robocopy fallo: $LASTEXITCODE" } else { Write-Output "robocopy ok: $LASTEXITCODE" }
```
Expected: `robocopy ok: 1` (1 = copió archivos; códigos <8 son éxito).

- [ ] **Step 3: Verificar el árbol copiado**

Run:
```
Get-ChildItem -Recurse -File site | Select-Object -ExpandProperty FullName | ForEach-Object { $_.Replace("$PWD\", "") }
```
Expected: incluye `site\index.html`, `site\assets\estilo.css`, `site\assets\render.js`, `site\assets\carrusel.js`, `site\assets\app.js`, `site\data\links.js`, `site\data\feed.js`, `site\data\feed.json`, `site\test\*.test.js`, `site\docs\superpowers\...`, y **no** `site\.git`.

- [ ] **Step 4: Commit y push**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add -A
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: integra la pagina E (link-in-bio) en site/"
& 'C:\Program Files\Git\cmd\git.exe' push origin main
```
Expected: push correcto a `origin/main`.

- [ ] **Step 5: Hacer público el repo**

Run:
```
gh repo edit WalterSolorzano/UNI --visibility public --accept-visibility-change-consequences
gh repo view WalterSolorzano/UNI --json visibility
```
Expected: `{"visibility":"PUBLIC"}`.

- [ ] **Step 6: Activar GitHub Pages (rama `main`, carpeta `/`)**

Run:
```
'{"source":{"branch":"main","path":"/"}}' | gh api -X POST /repos/WalterSolorzano/UNI/pages --input -
gh api /repos/WalterSolorzano/UNI/pages --jq .html_url
```
Expected: imprime `https://waltersolorzano.github.io/UNI/`.

- [ ] **Step 7: Verificar que la página responde**

Run (esperar ~60 s tras activar Pages):
```
Start-Sleep -Seconds 60
(Invoke-WebRequest -UseBasicParsing "https://waltersolorzano.github.io/UNI/site/").StatusCode
```
Expected: `200`. (Si aún 404, esperar otro minuto y reintentar.)

- [ ] **Step 8: Commit** — ya hecho en Step 4 (no hay cambios nuevos).

---

### Task 2: Núcleo del pipeline Python (normalización, conserva-lo-bueno, escritura dual, purga)

**Files:**
- Create: `tools/build_feed.py`
- Test: `tools/tests/test_build_feed.py`
- Create: `tools/tests/__init__.py` (vacío)

**Interfaces:**
- Consumes: nada.
- Produces:
  - `normalize(net: str, cap: str, url: str, when: datetime|None, img: str|None, st: list|None) -> dict`
  - `merge_keep_last_good(old_pool: dict, new_pool: dict) -> dict`
  - `write_feed(feed: dict) -> None` (escribe `site/data/feed.json` y `site/data/feed.js`)
  - `load_old_feed() -> dict|None`
  - `purge_orphans(keep: set[str]) -> list[str]`
  - Constantes: `ORDER = ['tt','ig','fb']`, `SITE`, `POSTS`, `DATA`, `FEED_JSON`, `FEED_JS`

- [ ] **Step 1: Write the failing test**

Create `tools/tests/test_build_feed.py`:
```python
import datetime, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_feed as bf

class TestNormalize(unittest.TestCase):
    def test_basic_fields(self):
        when = datetime.datetime(2026, 10, 5, 12, 0, tzinfo=datetime.timezone.utc)
        p = bf.normalize('tt', '  Hola <mundo>  ', 'https://x/1', when=when)
        self.assertEqual(p['net'], 'tt')
        self.assertEqual(p['cap'], 'Hola <mundo>')
        self.assertEqual(p['url'], 'https://x/1')
        self.assertTrue(p['tm'].startswith('hace'))
        self.assertNotIn('img', p)
        self.assertNotIn('st', p)

    def test_optional_fields(self):
        p = bf.normalize('ig', 'c', 'u', when=None, img='assets/posts/ig_1.jpg', st=['1.2K'])
        self.assertEqual(p['img'], 'assets/posts/ig_1.jpg')
        self.assertEqual(p['st'], ['1.2K'])
        self.assertEqual(p['tm'], '')

class TestKeepLastGood(unittest.TestCase):
    def test_keeps_old_when_new_empty(self):
        old = {'tt': [{'net': 'tt'}], 'ig': [{'net': 'ig'}], 'fb': []}
        new = {'tt': [], 'ig': [{'net': 'ig', 'cap': 'nuevo'}], 'fb': [{'net': 'fb'}]}
        m = bf.merge_keep_last_good(old, new)
        self.assertEqual(m['tt'], [{'net': 'tt'}])
        self.assertEqual(m['ig'], [{'net': 'ig', 'cap': 'nuevo'}])
        self.assertEqual(m['fb'], [{'net': 'fb'}])

class TestPurgeOrphans(unittest.TestCase):
    def test_removes_unreferenced(self):
        d = tempfile.mkdtemp()
        old_posts = bf.POSTS
        bf.POSTS = d
        try:
            open(os.path.join(d, 'keep.jpg'), 'wb').write(b'x')
            open(os.path.join(d, 'drop.jpg'), 'wb').write(b'x')
            removed = bf.purge_orphans({'assets/posts/keep.jpg'})
            self.assertEqual(removed, ['drop.jpg'])
            self.assertTrue(os.path.exists(os.path.join(d, 'keep.jpg')))
        finally:
            bf.POSTS = old_posts

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `C:\Users\--X\Desktop\PILAR\entregable`):
```
python -m unittest tools.tests.test_build_feed -v
```
Expected: FAIL con `ModuleNotFoundError: No module named 'build_feed'`.

- [ ] **Step 3: Write minimal implementation**

Create `tools/build_feed.py`:
```python
#!/usr/bin/env python3
"""Genera site/data/feed.json y feed.js con publicaciones reales de tt/ig/fb."""
import argparse, datetime, json, os, re, sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
POSTS = os.path.join(SITE, 'assets', 'posts')
DATA = os.path.join(SITE, 'data')
FEED_JSON = os.path.join(DATA, 'feed.json')
FEED_JS = os.path.join(DATA, 'feed.js')

ORDER = ['tt', 'ig', 'fb']
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124 Safari/537.36')


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def relative(when, now=None):
    now = now or now_utc()
    s = int((now - when).total_seconds())
    if s < 3600:
        return 'hace %d min' % max(1, s // 60)
    if s < 86400:
        return 'hace %d h' % (s // 3600)
    d = s // 86400
    if d == 1:
        return 'ayer'
    if d < 7:
        return 'hace %d d' % d
    return when.strftime('%d/%m/%Y')


def normalize(net, cap, url, when=None, img=None, st=None):
    post = {
        'net': net,
        'cap': (cap or '').strip()[:220],
        'url': url or '',
        'tm': relative(when) if when else '',
    }
    if img:
        post['img'] = img
    if st:
        post['st'] = list(st)
    return post


def merge_keep_last_good(old_pool, new_pool):
    old_pool = old_pool or {}
    new_pool = new_pool or {}
    merged = {}
    for net in ORDER:
        new = new_pool.get(net) or []
        merged[net] = new if new else (old_pool.get(net) or [])
    return merged


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


def load_old_feed():
    try:
        with open(FEED_JSON, encoding='utf-8') as f:
            j = json.load(f)
        return j if isinstance(j, dict) else None
    except Exception:
        return None


def purge_orphans(keep):
    if not os.path.isdir(POSTS):
        return []
    removed = []
    for name in os.listdir(POSTS):
        p = os.path.join(POSTS, name)
        if os.path.isfile(p) and ('assets/posts/' + name) not in keep:
            os.remove(p)
            removed.append(name)
    return removed
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```
python -m unittest tools.tests.test_build_feed -v
```
Expected: PASS (3 tests). (Crear `tools/tests/__init__.py` vacío para que el paquete sea importable.)

- [ ] **Step 5: Commit**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add tools/build_feed.py tools/tests
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: nucleo del pipeline de feed (normaliza, conserva lo ultimo bueno, escribe dual)"
```

---

### Task 3: Fetcher de TikTok (embed → oEmbed → miniatura)

**Files:**
- Modify: `tools/build_feed.py`
- Test: `tools/tests/test_build_feed.py`
- Create: `tools/tests/fixtures/tt_embed.html`

**Interfaces:**
- Consumes: `normalize`, `POSTS`, `UA` (Task 2).
- Produces:
  - `tt_video_ids(html: str) -> list[str]`
  - `fetch_tiktok(limit: int = 4) -> list[dict]`
  - Constantes `TT_HANDLE = 'unen.industrial.uni'`, `TT_EMBED`, `TT_OEMBED`

- [ ] **Step 1: Capturar un fixture real**

Run (workdir repo):
```
python -c "import requests; open('tools/tests/fixtures/tt_embed.html','w',encoding='utf-8').write(requests.get('https://www.tiktok.com/embed/@unen.industrial.uni', headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}, timeout=30).text)"
```
Expected: archivo creado (>5 KB). Si falla por red, guardar cualquier HTML de la página embed como fixture y continuar.

- [ ] **Step 2: Write the failing test**

Añadir a `tools/tests/test_build_feed.py`:
```python
class TestTikTokParse(unittest.TestCase):
    def test_extracts_ids_from_embed(self):
        html = ('<div data-video-id="7412345678901234567"></div>'
                '<div data-video-id="7412345678901234568"></div>'
                '<div data-video-id="7412345678901234567"></div>')
        self.assertEqual(bf.tt_video_ids(html),
                         ['7412345678901234567', '7412345678901234568'])

    def test_falls_back_to_video_urls(self):
        html = '<a href="/@u/video/7411111111111111111">x</a>'
        self.assertEqual(bf.tt_video_ids(html), ['7411111111111111111'])

    def test_fixture_has_at_least_one_id(self):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'tt_embed.html')
        if os.path.exists(path):
            ids = bf.tt_video_ids(open(path, encoding='utf-8').read())
            self.assertGreaterEqual(len(ids), 1)
```

- [ ] **Step 3: Run test to verify it fails**

Run:
```
python -m unittest tools.tests.test_build_feed.TestTikTokParse -v
```
Expected: FAIL con `AttributeError: module 'build_feed' has no attribute 'tt_video_ids'`.

- [ ] **Step 4: Write minimal implementation**

Añadir a `tools/build_feed.py`:
```python
TT_HANDLE = 'unen.industrial.uni'
TT_EMBED = 'https://www.tiktok.com/embed/@' + TT_HANDLE
TT_OEMBED = 'https://www.tiktok.com/oembed?url='


def tt_video_ids(html):
    ids = re.findall(r'data-video-id="(\d+)"', html)
    if not ids:
        ids = re.findall(r'"videoId":"(\d+)"', html)
    if not ids:
        ids = re.findall(r'/video/(\d{6,})', html)
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def download(url, dest, timeout=30):
    r = requests.get(url, timeout=timeout, headers={'User-Agent': UA})
    r.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        f.write(r.content)
    return os.path.relpath(dest, SITE).replace('\\', '/')


def slug(net, ident):
    return '%s_%s' % (net, re.sub(r'[^A-Za-z0-9_-]', '', str(ident))[:40])


def fetch_tiktok(limit=4):
    r = requests.get(TT_EMBED, timeout=30, headers={'User-Agent': UA})
    r.raise_for_status()
    posts = []
    for vid in tt_video_ids(r.text)[:limit]:
        url = 'https://www.tiktok.com/@%s/video/%s' % (TT_HANDLE, vid)
        try:
            o = requests.get(TT_OEMBED + requests.utils.quote(url, safe=''),
                             timeout=30, headers={'User-Agent': UA})
            o.raise_for_status()
            j = o.json()
        except Exception:
            continue
        img = None
        if j.get('thumbnail_url'):
            try:
                img = download(j['thumbnail_url'],
                               os.path.join(POSTS, slug('tt', vid) + '.jpg'))
            except Exception:
                img = None
        posts.append(normalize('tt', j.get('title') or '', url, when=None, img=img))
    return posts
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```
python -m unittest tools.tests.test_build_feed -v
```
Expected: PASS (todos).

- [ ] **Step 6: Smoke test en vivo (opcional, requiere red)**

Run:
```
python -c "import tools.build_feed as b; ps=b.fetch_tiktok(2); print(len(ps), ps[0]['url'] if ps else 'vacio')"
```
Expected: `2 https://www.tiktok.com/@unen.industrial.uni/video/...` (si TikTok bloquea, `vacio` es aceptable; el Action degradará).

- [ ] **Step 7: Commit**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add tools/build_feed.py tools/tests
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: fetcher de TikTok (embed a oEmbed con miniatura descargada)"
```

---

### Task 4: Página "real" (3 slides tt/ig/fb, miniatura, enlace, métricas y fecha opcionales)

**Files:**
- Modify: `site/index.html` (quitar slide `wa`, reordenar tt/ig/fb, seed honesto)
- Modify: `site/assets/render.js` (helpers `thumbHTML`, `slideLinkHTML`)
- Modify: `site/assets/app.js` (imagen, enlace, ocultar métricas/fecha vacías, rótulo con fecha)
- Modify: `site/assets/estilo.css` (solo reglas nuevas al final)
- Modify: `site/data/feed.js` y `site/data/feed.json` (esquema v2 de arranque)
- Test: `site/test/estructura.test.js`, `site/test/datos.test.js`, `site/test/render.test.js`, `site/test/feedjson.test.js`

**Interfaces:**
- Consumes: `UNEN_FEED` v2 (`{generatedAt, rotationMs, order, pool}`), `Render.safeCaption`, `Carrusel.*` (existentes).
- Produces: `Render.thumbHTML(post) -> str`, `Render.slideLinkHTML(post) -> str`.

- [ ] **Step 1: Write the failing tests (esquema v2 y 3 slides)**

En `site/test/estructura.test.js`, cambiar el test de slides:
```js
test('hay 3 slides con data-net tt/ig/fb, 3 dots y 6 simbolos', () => {
  for (const n of ['tt', 'ig', 'fb']) assert.match(html, new RegExp('data-net="' + n + '"'));
  assert.doesNotMatch(html, /data-net="wa"/);
  assert.strictEqual((html.match(/class="sl"/g) || []).length, 3);
  const dotsWrap = html.match(/<div class="dots">([\s\S]*?)<\/div>/);
  assert.ok(dotsWrap, 'falta el contenedor .dots');
  assert.strictEqual((dotsWrap[1].match(/<i/g) || []).length, 3, 'deben ser 3 .dots i');
  assert.strictEqual((html.match(/<symbol/g) || []).length, 6, 'deben ser 6 <symbol>');
});
```
En `site/test/datos.test.js`, reemplazar el test de FEED:
```js
test('UNEN_FEED v2: generatedAt, order tt/ig/fb y posts con net/cap/url/tm', () => {
  assert.strictEqual(typeof FEED.generatedAt, 'string');
  assert.deepStrictEqual(FEED.order, ['tt', 'ig', 'fb']);
  assert.ok(FEED.rotationMs > 0);
  for (const net of FEED.order) {
    assert.ok(Array.isArray(FEED.pool[net]), net + ' debe ser array');
    for (const p of FEED.pool[net]) {
      assert.strictEqual(p.net, net);
      assert.strictEqual(typeof p.cap, 'string');
      assert.strictEqual(typeof p.url, 'string');
      assert.strictEqual(typeof p.tm, 'string');
      if (p.img !== undefined) assert.strictEqual(typeof p.img, 'string');
      if (p.st !== undefined) assert.ok(Array.isArray(p.st));
    }
  }
});
```
En `site/test/render.test.js`, añadir:
```js
test('thumbHTML produce img solo si hay img', () => {
  assert.strictEqual(Render.thumbHTML({}), '');
  assert.match(Render.thumbHTML({ img: 'assets/posts/tt_1.jpg' }),
    /<img class="thumb" src="assets\/posts\/tt_1\.jpg"/);
});

test('slideLinkHTML produce overlay solo si hay url', () => {
  assert.strictEqual(Render.slideLinkHTML({}), '');
  assert.match(Render.slideLinkHTML({ url: 'https://x', cap: 'hola' }),
    /class="open" href="https:\/\/x" target="_blank" rel="noopener"/);
});
```
En `site/test/feedjson.test.js`, añadir aserción de `generatedAt`:
```js
assert.strictEqual(typeof data.generatedAt, 'string');
```

- [ ] **Step 2: Run tests to verify they fail**

Run (workdir `C:\Users\--X\Desktop\PILAR\entregable\site`):
```
npm test
```
Expected: FAIL (slides=4≠3, `FEED.order` distinto, `Render.thumbHTML` no es función, `generatedAt` ausente).

- [ ] **Step 3: Implementar helpers en `render.js`**

Añadir antes del `return` de `site/assets/render.js`:
```js
  function thumbHTML(post) {
    if (!post || !post.img) return '';
    return '<img class="thumb" src="' + post.img + '" alt="" loading="lazy">';
  }

  function slideLinkHTML(post) {
    if (!post || !post.url) return '';
    var label = post.cap ? String(post.cap).slice(0, 80) : 'Ver publicacion';
    return '<a class="open" href="' + post.url + '" target="_blank" rel="noopener" ' +
      'aria-label="' + label.replace(/"/g, '&quot;') + '"></a>';
  }
```
Y cambiar el `return` final a:
```js
  return { iconSVG: iconSVG, linkButtonHTML: linkButtonHTML, safeCaption: safeCaption,
           thumbHTML: thumbHTML, slideLinkHTML: slideLinkHTML };
```

- [ ] **Step 4: Implementar cambios de página**

En `site/index.html`:
1. Sustituir el bloque `<div class="track">...</div>` por 3 slides tt/ig/fb con **seed honesto** (sin métricas falsas ni `dur`). Ejemplo:
```html
<div class="track">
  <div class="sl" data-net="tt"><div class="m g1"><span class="chipl tt"><svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-tt"/></svg></span><div class="play"></div></div><div class="bd"><div class="hd"><span class="av i-tt"></span><b class="who">@unen.industrial.uni</b><span class="tm"></span></div><div class="cap">Ver las ultimas publicaciones en TikTok</div><div class="st"></div></div></div>
  <div class="sl" data-net="ig"><div class="m g2"><span class="chipl ig"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/></svg></span><div class="play"></div></div><div class="bd"><div class="hd"><span class="av i-ig"></span><b class="who">@unen.industrial</b><span class="tm"></span></div><div class="cap">Ver las ultimas publicaciones en Instagram</div><div class="st"></div></div></div>
  <div class="sl" data-net="fb"><div class="m g3"><span class="chipl fb"><svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-fb"/></svg></span></div><div class="bd"><div class="hd"><span class="av i-fb"></span><b class="who">UNEN Industrial UNI</b><span class="tm"></span></div><div class="cap">Ver las ultimas publicaciones en Facebook</div><div class="st"></div></div></div>
</div>
```
2. Cambiar los dots a 3: `<div class="dots"><i class="on"></i><i></i><i></i></div>`.
3. Cambiar el rótulo: `<div class="live"><i></i><span class="live-txt">Actividad de las redes</span></div>`.
4. **Eliminar** el `<symbol id="i-wa">`? No: el botón "Canal de WhatsApp" usa `#i-wa`. **Conservarlo.**

En `site/assets/app.js`:
1. `var order = ['whatsappDirecto', 'instagram', 'facebook', 'tiktok', 'whatsapp'];` se mantiene (botones).
2. En `startCarousel`, cambiar `var idx = { ig: 0, fb: 0, tt: 0, wa: 0 };` por `var idx = { tt: 0, ig: 0, fb: 0 };`.
3. Reescribir `fillSlide` para cubrir imagen, enlace, métricas y fecha opcionales:
```js
  function fillSlide(slide, post) {
    var cap = slide.querySelector('.cap');
    var tm = slide.querySelector('.tm');
    var dur = slide.querySelector('.dur');
    var st = slide.querySelector('.st');
    var m = slide.querySelector('.m');
    if (cap) cap.innerHTML = window.Render.safeCaption(post.cap);
    if (tm) { tm.textContent = post.tm || ''; tm.style.display = post.tm ? '' : 'none'; }
    if (dur) { dur.textContent = post.dur || ''; dur.style.display = post.dur ? '' : 'none'; }
    if (st) st.innerHTML = (post.st || []).map(function (v) { return '<span><b>' + v + '</b></span>'; }).join('');
    if (m) {
      var img = m.querySelector('img.thumb');
      if (post.img) {
        if (!img) { m.insertAdjacentHTML('afterbegin', window.Render.thumbHTML(post)); }
        else { img.src = post.img; }
      } else if (img) { img.remove(); }
    }
    slide.querySelectorAll('.open').forEach(function (a) { a.remove(); });
    if (post.url) slide.insertAdjacentHTML('beforeend', window.Render.slideLinkHTML(post));
  }
```
4. Añadir el rótulo con fecha real en `startCarousel`, tras calcular `slides`:
```js
    var liveTxt = phone.querySelector('.car .live-txt');
    if (liveTxt && feed.generatedAt) {
      var d = new Date(feed.generatedAt);
      if (!isNaN(d.getTime())) {
        liveTxt.textContent = 'Actividad de las redes · actualizado ' + d.toLocaleDateString('es', { day: '2-digit', month: 'short' });
      }
    }
```
5. En `load()`, no cambiar: ya hace `fetch('data/feed.json')` con fallback a `window.UNEN_FEED`.

En `site/assets/estilo.css`, **añadir al final** (no tocar reglas previas):
```css
.car .sl { position:relative; }
.car .m img.thumb { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block; z-index:1; }
.car .m .play, .car .m .dur, .car .m .chipl { z-index:2; }
.car .m .dur:empty { display:none; }
.car .st:empty { display:none; }
.car .hd .tm:empty { display:none; }
.car .sl .open { position:absolute; inset:0; z-index:3; border-radius:15px; }
```

En `site/data/feed.js` y `site/data/feed.json`, poner el esquema v2 de arranque (datos reales de la primera corrida reemplazarán esto):
```js
(function (root) {
  root.UNEN_FEED = {
    generatedAt: '2026-10-07T00:00:00Z',
    rotationMs: 6000,
    order: ['tt', 'ig', 'fb'],
    pool: {
      tt: [{ net: 'tt', cap: 'Ver las ultimas publicaciones en TikTok', url: 'https://www.tiktok.com/@unen.industrial.uni', tm: '' }],
      ig: [{ net: 'ig', cap: 'Ver las ultimas publicaciones en Instagram', url: 'https://www.instagram.com/unen.industrial', tm: '' }],
      fb: [{ net: 'fb', cap: 'Ver las ultimas publicaciones en Facebook', url: 'https://www.facebook.com/Unen-Industrial-61594093749350', tm: '' }]
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
```
(`feed.json` con el mismo objeto, sin el wrapper.)

- [ ] **Step 5: Run tests to verify they pass**

Run:
```
npm test
```
Expected: PASS (todas).

- [ ] **Step 6: Verificar en navegador (visual + degradación)**

Run (abrir y medir):
```
Start-Process 'file:///C:/Users/--X/Desktop/PILAR/entregable/site/index.html'
```
Expected: carrusel con 3 slides, dots=3, sin métricas falsas, sin cajas vacías; los 5 botones siguen.

- [ ] **Step 7: Commit**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add site
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: carrusel real (3 slides tt/ig/fb, miniatura, enlace, metricas y fecha opcionales)"
```

---

### Task 5: Workflow de GitHub Actions (cron diario + dispatch) y primer run

**Files:**
- Create: `.github/workflows/feed.yml`
- Modify: `tools/build_feed.py` (añadir `main()` con `--check`/`--only`)

**Interfaces:**
- Consumes: `build()` y fetchers de Tasks 2–3.
- Produces: workflow `feed` que commitea `site/data` y `site/assets/posts`.

- [ ] **Step 1: Añadir `main()` y `build()` al script**

Añadir a `tools/build_feed.py`:
```python
FETCHERS = {'tt': fetch_tiktok}


def build(only=None, check=False):
    old = load_old_feed() or {}
    new_pool = {}
    for net in ORDER:
        if only and net not in only:
            new_pool[net] = (old.get('pool') or {}).get(net) or []
            continue
        fn = FETCHERS.get(net)
        if not fn:
            new_pool[net] = (old.get('pool') or {}).get(net) or []
            continue
        try:
            new_pool[net] = fn() or []
        except Exception as e:
            print('[warn] %s fallo: %s' % (net, e))
            new_pool[net] = []
    pool = merge_keep_last_good(old.get('pool') or {}, new_pool)
    feed = {
        'generatedAt': now_utc().replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'rotationMs': 6000,
        'order': ORDER,
        'pool': pool,
    }
    keep = set()
    for net in ORDER:
        for p in pool.get(net) or []:
            if p.get('img'):
                keep.add(p['img'])
    if check:
        print(json.dumps(feed, ensure_ascii=False)[:400])
        return 0
    write_feed(feed)
    removed = purge_orphans(keep)
    print('feed: %s | purgadas: %s' % ({n: len(pool.get(n) or []) for n in ORDER}, removed))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--only', default='')
    args = ap.parse_args(argv)
    only = [x for x in args.only.split(',') if x] if args.only else None
    return build(only=only, check=args.check)


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 2: Probar en local sin escribir**

Run:
```
python tools/build_feed.py --check --only tt
```
Expected: imprime un JSON con `"order": ["tt","ig","fb"]` y `"generatedAt"`. Exit 0.

- [ ] **Step 3: Crear el workflow**

Create `.github/workflows/feed.yml`:
```yaml
name: feed
on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:
permissions:
  contents: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install requests playwright
      - run: python -m playwright install --with-deps chromium
      - run: python tools/build_feed.py
      - name: Commit feed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add site/data site/assets/posts
          if git diff --cached --quiet; then
            echo "sin cambios"
          else
            git commit -m "chore: feed automatico"
            git push
          fi
```

- [ ] **Step 4: Commit y push del workflow**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add .github/workflows/feed.yml tools/build_feed.py
& 'C:\Program Files\Git\cmd\git.exe' commit -m "ci: workflow diario del feed (cron 06:00 UTC + dispatch)"
& 'C:\Program Files\Git\cmd\git.exe' push origin main
```

- [ ] **Step 5: Disparar el workflow manualmente**

Run:
```
gh workflow run feed --repo WalterSolorzano/UNI
Start-Sleep -Seconds 20
gh run list --repo WalterSolorzano/UNI --workflow feed --limit 1
```
Expected: aparece un run `in_progress`/`completed`.

- [ ] **Step 6: Verificar resultado**

Run:
```
gh run watch --repo WalterSolorzano/UNI $(gh run list --repo WalterSolorzano/UNI --workflow feed --limit 1 --json databaseId --jq '.[0].databaseId')
```
Expected: run en verde; si hubo datos, un commit `chore: feed automatico`. Luego:
```
gh api /repos/WalterSolorzano/UNI/contents/site/data/feed.json --jq .size
```
Expected: número > 0.

- [ ] **Step 7: Commit** — ya hecho en Step 4.

---

### Task 6: Fetcher de Instagram (RSS-Bridge, multi-instancia)

**Files:**
- Modify: `tools/build_feed.py`
- Test: `tools/tests/test_build_feed.py`
- Create: `tools/tests/fixtures/ig_atom.xml`

**Interfaces:**
- Consumes: `normalize`, `download`, `POSTS`.
- Produces: `ig_entries(xml_text: str) -> list[dict]`, `fetch_instagram(limit: int = 4) -> list[dict]`, `IG_USER`, `IG_BRIDGES`.

- [ ] **Step 1: Capturar un fixture real**

Run:
```
python -c "import requests; u='https://rss-bridge.org/bridge01/?action=display&bridge=InstagramBridge&context=Username&u=unen.industrial&format=Atom'; open('tools/tests/fixtures/ig_atom.xml','w',encoding='utf-8').write(requests.get(u, headers={'User-Agent':'Mozilla/5.0'}, timeout=40).text)"
```
Expected: XML con `<feed>` y al menos 1 `<entry>`. Si el bridge falla, probar otra instancia pública y guardar su respuesta.

- [ ] **Step 2: Write the failing test**

Añadir:
```python
IG_SAMPLE = '''<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
 <entry>
  <title>Reel de prueba</title>
  <link rel="alternate" href="https://www.instagram.com/p/ABC123/"/>
  <updated>2026-10-05T10:00:00+00:00</updated>
  <media:content url="https://example.com/x.jpg"/>
 </entry>
</feed>'''

class TestInstagramParse(unittest.TestCase):
    def test_parses_entry(self):
        rows = bf.ig_entries(IG_SAMPLE)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['cap'], 'Reel de prueba')
        self.assertEqual(rows[0]['url'], 'https://www.instagram.com/p/ABC123/')
        self.assertEqual(rows[0]['thumb'], 'https://example.com/x.jpg')
        self.assertIsNotNone(rows[0]['when'])
```

- [ ] **Step 3: Run test to verify it fails**

Run:
```
python -m unittest tools.tests.test_build_feed.TestInstagramParse -v
```
Expected: FAIL (`no attribute 'ig_entries'`).

- [ ] **Step 4: Write minimal implementation**

Añadir:
```python
import xml.etree.ElementTree as ET

IG_USER = 'unen.industrial'
IG_BRIDGES = ['https://rss-bridge.org/bridge01']
_ATOM = {'a': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}


def _parse_iso(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


def ig_entries(xml_text):
    root = ET.fromstring(xml_text)
    out = []
    for e in root.findall('a:entry', _ATOM):
        title = (e.findtext('a:title', '', _ATOM) or '').strip()
        link = ''
        for l in e.findall('a:link', _ATOM):
            if l.get('rel') in (None, 'alternate'):
                link = l.get('href') or link
        when = _parse_iso(e.findtext('a:updated', '', _ATOM) or e.findtext('a:published', '', _ATOM))
        thumb = ''
        mc = e.find('media:content', _ATOM)
        if mc is not None:
            thumb = mc.get('url') or ''
        if not thumb:
            enc = e.find('a:enclosure', _ATOM)
            if enc is not None:
                thumb = enc.get('url') or ''
        out.append({'cap': title, 'url': link, 'when': when, 'thumb': thumb})
    return out


def fetch_instagram(limit=4):
    for base in IG_BRIDGES:
        url = (base + '/?action=display&bridge=InstagramBridge&context=Username&u=' +
               requests.utils.quote(IG_USER) + '&format=Atom')
        try:
            r = requests.get(url, timeout=40, headers={'User-Agent': UA})
            r.raise_for_status()
            rows = ig_entries(r.text)
        except Exception as e:
            print('[warn] ig bridge %s fallo: %s' % (base, e))
            continue
        posts = []
        for row in rows[:limit]:
            img = None
            if row['thumb']:
                try:
                    img = download(row['thumb'],
                                   os.path.join(POSTS, slug('ig', (row['url'] or '').rstrip('/').split('/')[-1] or 'p') + '.jpg'))
                except Exception:
                    img = None
            posts.append(normalize('ig', row['cap'], row['url'], when=row['when'], img=img))
        if posts:
            return posts
    return []
```
Y registrar el fetcher: `FETCHERS = {'tt': fetch_tiktok, 'ig': fetch_instagram}`.

- [ ] **Step 5: Run test to verify it passes**

Run:
```
python -m unittest tools.tests.test_build_feed -v
```
Expected: PASS.

- [ ] **Step 6: Commit**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add tools/build_feed.py tools/tests
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: fetcher de Instagram via RSS-Bridge con miniatura"
```

---

### Task 7: Fetcher de Facebook (Playwright)

**Files:**
- Modify: `tools/build_feed.py`
- Test: `tools/tests/test_build_feed.py`
- Create: `tools/tests/fixtures/fb_page.html`

**Interfaces:**
- Consumes: `normalize`, `download`, `POSTS`.
- Produces: `fb_posts_from_html(html: str) -> list[dict]`, `fetch_facebook(limit: int = 3) -> list[dict]`, `FB_PAGE`.

- [ ] **Step 1: Capturar un fixture real (HTML del Page Plugin)**

Run:
```
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); pg=b.new_page(viewport={'width':420,'height':900}); pg.goto('https://www.facebook.com/plugins/page.php?href='+__import__('urllib.parse',fromlist=['quote']).quote('https://www.facebook.com/Unen-Industrial-61594093749350',safe='')+'&tabs=timeline&width=400&height=800', wait_until='networkidle', timeout=60000); pg.wait_for_timeout(4000); open('tools/tests/fixtures/fb_page.html','w',encoding='utf-8').write(pg.content()); b.close(); p.stop()"
```
Expected: `tools/tests/fixtures/fb_page.html` (>20 KB). Si el runner/PC no tiene Playwright, `pip install playwright` y `python -m playwright install chromium` primero.

- [ ] **Step 2: Write the failing test**

Añadir:
```python
FB_SAMPLE = ('<div role="article"><div><span>Texto del post de Facebook</span>'
             '<a href="https://www.facebook.com/Unen-Industrial-61594093749350/posts/123">'
             '<img src="https://example.com/fb.jpg"/></a></div></div>')

class TestFacebookParse(unittest.TestCase):
    def test_parses_post(self):
        rows = bf.fb_posts_from_html(FB_SAMPLE)
        self.assertEqual(len(rows), 1)
        self.assertIn('Texto del post', rows[0]['cap'])
        self.assertIn('/posts/123', rows[0]['url'])
        self.assertEqual(rows[0]['thumb'], 'https://example.com/fb.jpg')
```

- [ ] **Step 3: Run test to verify it fails**

Run:
```
python -m unittest tools.tests.test_build_feed.TestFacebookParse -v
```
Expected: FAIL (`no attribute 'fb_posts_from_html'`).

- [ ] **Step 4: Write minimal implementation**

Añadir:
```python
from html.parser import HTMLParser

FB_PAGE = 'Unen-Industrial-61594093749350'


class _FBParser(HTMLParser):
    """Extrae articulos con texto, enlace de post e imagen del Page Plugin."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.posts = []
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('role') == 'article':
            self.cur = {'cap': '', 'url': '', 'thumb': ''}
            self.depth = 1
            return
        if self.cur is not None:
            self.depth += 1
            href = a.get('href', '')
            if href and not self.cur['url'] and ('/posts/' in href or 'story_fbid' in href or '/photos/' in href):
                self.cur['url'] = href if href.startswith('http') else 'https://www.facebook.com' + href
            src = a.get('src', '')
            if src and not self.cur['thumb'] and src.startswith('http'):
                self.cur['thumb'] = src

    def handle_data(self, data):
        if self.cur is not None:
            self.cur['cap'] += data

    def handle_endtag(self, tag):
        if self.cur is not None:
            self.depth -= 1
            if self.depth <= 0:
                self.cur['cap'] = ' '.join(self.cur['cap'].split())[:220]
                if self.cur['cap'] or self.cur['url']:
                    self.posts.append(self.cur)
                self.cur = None


def fb_posts_from_html(html):
    p = _FBParser()
    p.feed(html)
    return p.posts


def fetch_facebook(limit=3):
    from playwright.sync_api import sync_playwright
    href = ('https://www.facebook.com/plugins/page.php?href=' +
            requests.utils.quote('https://www.facebook.com/' + FB_PAGE, safe='') +
            '&tabs=timeline&width=400&height=800')
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 420, 'height': 900})
        pg.goto(href, wait_until='networkidle', timeout=60000)
        pg.wait_for_timeout(4000)
        html = pg.content()
        b.close()
    posts = []
    for row in fb_posts_from_html(html)[:limit]:
        img = None
        if row['thumb']:
            try:
                img = download(row['thumb'],
                               os.path.join(POSTS, slug('fb', (row['url'] or 'p').rstrip('/').split('/')[-1]) + '.jpg'))
            except Exception:
                img = None
        posts.append(normalize('fb', row['cap'], row['url'], when=None, img=img))
    return posts
```
Y registrar: `FETCHERS = {'tt': fetch_tiktok, 'ig': fetch_instagram, 'fb': fetch_facebook}`.

- [ ] **Step 5: Run test to verify it passes**

Run:
```
python -m unittest tools.tests.test_build_feed -v
```
Expected: PASS.

- [ ] **Step 6: Probar en vivo (opcional)**

Run:
```
python tools/build_feed.py --check --only fb
```
Expected: imprime JSON. Si FB bloquea, `fb` queda vacío y se conservará lo previo (degradación esperada).

- [ ] **Step 7: Commit**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add tools/build_feed.py tools/tests
& 'C:\Program Files\Git\cmd\git.exe' commit -m "feat: fetcher de Facebook con Playwright (Page Plugin)"
```

---

### Task 8: Cierre — README, docs, purga y revisión final

**Files:**
- Modify: `site/README.md`
- Modify: `tools/build_feed.py` (purga ya incluida; verificar)

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: documentación de uso y operación.

- [ ] **Step 1: Actualizar `site/README.md`**

Añadir secciones (texto exacto):
```markdown
## Feed real (automático)
- El carrusel muestra publicaciones reales de TikTok, Instagram y Facebook.
- Se actualiza 1 vez al día con GitHub Actions (`.github/workflows/feed.yml`, 06:00 UTC).
- Datos: `site/data/feed.json` (online) y `site/data/feed.js` (respaldo en `file://`).
- Miniaturas: `site/assets/posts/` (descargadas; las URLs de origen caducan).
- Ejecutar a mano: `python tools/build_feed.py` (o `--check` / `--only tt,ig,fb`).
- Si una red falla, se conserva su última tanda buena (no se vacía).
- Publicado en: https://waltersolorzano.github.io/UNI/site/
```

- [ ] **Step 2: Verificación integral**

Run (workdir `C:\Users\--X\Desktop\PILAR\entregable\site`):
```
npm test
python -m unittest discover -s ../tools/tests -v
```
Expected: ambas suites en verde.

- [ ] **Step 3: Verificar la página publicada**

Run:
```
(Invoke-WebRequest -UseBasicParsing "https://waltersolorzano.github.io/UNI/site/").StatusCode
```
Expected: `200`. Abrir en el navegador y confirmar 3 slides, dots=3, 5 botones, sin métricas falsas.

- [ ] **Step 4: Commit y push**

Run:
```
& 'C:\Program Files\Git\cmd\git.exe' add -A
& 'C:\Program Files\Git\cmd\git.exe' commit -m "docs: README del feed real y cierre"
& 'C:\Program Files\Git\cmd\git.exe' push origin main
```

---

## Self-Review

**1. Spec coverage**
- §6.1 pipeline → Tasks 2, 3, 6, 7, 5 (main/build).
- §6.2 workflow → Task 5.
- §6.3 esquema v2 → Tasks 2 (write) y 4 (consumo + tests).
- §6.4 cambios de página → Task 4.
- §6.5 miniaturas (descarga + purga) → Tasks 3/6/7 (descarga) y 2/5 (purga).
- §7 pruebas → Tasks 2/3/6/7 (Python) y 4 (Node).
- §8 migración → Task 1.
- §9 riesgos → mitigados por `merge_keep_last_good` (Task 2) y captura de excepciones por red (Tasks 3/6/7).
- §10 fases → F1=Tasks 1–5, F2=Task 6, F3=Task 7, F4 documentado como escape hatch (no construido).

**2. Placeholder scan:** sin TBD/TODO; todos los pasos traen código o comandos exactos.

**3. Type consistency:** `normalize`, `merge_keep_last_good`, `write_feed`, `load_old_feed`, `purge_orphans`, `download`, `slug`, `tt_video_ids`, `ig_entries`, `fb_posts_from_html` se definen una vez y se consumen con la misma firma. `Render.thumbHTML`/`slideLinkHTML` coherentes entre test y `app.js`.

**4. Review Focus → tests:**
1. `file://` sin red → Task 4 Step 6 + `app.js` fallback existente (Task 4 Step 4.5).
2. Red sin publicaciones → `Carrusel.activeNets` (ya probado) + `merge_keep_last_good` (Task 2).
3. Post sin métricas/fecha → Task 4 Step 1/4 (`.st:empty`, `.tm:empty`, `.dur:empty`) y `fillSlide`.
4. Miniatura ausente/rota → `thumbHTML` devuelve `''` (Task 4 Step 3) y el degradado se conserva.
5. Datos sucios → `safeCaption` (existente) + `normalize` recorta a 220 (Task 2).
