# UNEN Industrial "E" funcional — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir el mockup E (link-in-bio UNEN Industrial) en una página estática real, funcional y publicable, con el diseño al pie de la letra.

**Architecture:** Sitio estático sin build ni dependencias de runtime. El CSS de la variante E se copia verbatim del mockup. Los datos viven aislados en `data/` (enlaces + publicaciones del carrusel). La lógica no-DOM se aísla en módulos puros (`render.js`, `carrusel.js`) con doble export (browser global + CommonJS) para poder probarla con el test runner de Node. `app.js` solo cablea DOM.

**Tech Stack:** HTML5, CSS3, JavaScript vanilla (ES5-compatible), Node.js `node --test` (solo para pruebas, sin dependencias).

**Spec:** `site/docs/superpowers/specs/2026-10-07-unen-e-funcional-design.md`

## Global Constraints

- Diseño **al pie de la letra**: el CSS de la variante E se copia **verbatim** de `entregable/mockup.html` (fuente de verdad visual).
- **Cero dependencias** de runtime; **cero build**. El sitio debe funcionar con doble clic (`file://`).
- **Cero costo**: sin servicios de pago.
- Idioma de la UI y textos: **español**, igual que el mockup.
- Paleta E: acento `#1565C0`; fondo página `#0B0F18`; tema claro `#F3F4F6`; fuentes `Poppins`.
- No tocar `mockups/` ni `entregable/`.
- Cada `<script>` de datos/lógica debe funcionar **tanto en navegador como en Node** (`globalThis`).
- Commits frecuentes, mensajes en inglés (Conventional Commits).

## Review Focus

Casos o condiciones que la spec no fija explícitamente pero que un usuario razonable esperaría que no rompan:

1. **URL de enlace en placeholder (`#`)**: el botón no debe navegar ni lanzar error.
2. **`data/feed.json` ausente o corrupto** (o `file://`): debe caer a `data/feed.js` sin romperse.
3. **Una red sin publicaciones en `feed`**: su slide se omite, el carrusel sigue y los puntos coinciden con el número de slides.
4. **Viewport angosto (~320px)**: el diseño no debe desbordar horizontalmente.
5. **`prefers-reduced-motion: reduce`**: aro/LEDs/carrusel no deben animar en bucle; la página sigue usable.
6. **Siguiente slide sin `dur` (FB/WA)**: rellenar sin error cuando el elemento `.dur` no existe.

Cada línea se pinea con un test o verificación en la tarea dueña (indicado en cada tarea).

---

## File Structure

```
site/
  index.html                     pagina E real (columna max 430px centrada)
  assets/
    estilo.css                   CSS E verbatim + centrado de pagina + reduced-motion
    render.js                    (puro) HTML de enlaces y slides
    carrusel.js                  (puro) indices y orden del carrusel
    app.js                       cableado DOM: render enlaces + carrusel + fallback
  data/
    links.js                     window.UNEN_LINKS (URLs/handles, editable)
    feed.js                      window.UNEN_FEED  (curado, default)
    feed.json                    mismo esquema; el Action lo sobrescribe (fase 2)
  test/
    estructura.test.js
    datos.test.js
    render.test.js
    carrusel.test.js
    feedjson.test.js
  package.json                   dev-only; scripts.test = node --test
  README.md
  .github/workflows/feed.yml     (Task 5, opcional/fase 2)
  docs/superpowers/...
```

---

### Task 1: Estructura, CSS E verbatim e `index.html` estático

**Files:**
- Create: `site/index.html`
- Create: `site/assets/estilo.css`
- Create: `site/test/estructura.test.js`
- Create: `site/package.json`
- Create: `site/README.md`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `index.html` contiene el contenedor raíz `#p4phone.phone2.v-E` con: `.hero.hero-bp` (aro), `h4`, `.sub`, `.car > .win > .track` con 4 `.sl[data-net]` (ig, fb, tt, wa), `.car .dots` con 4 `i`, `.lklist` (vacío), y los `<symbol>` SVG (`i-fb`, `i-tt`, `i-wa`, `i-heart`, `i-cmt`, `i-share`).
  - `assets/estilo.css` con la clase `.phone2.v-E` y tokens `--acc:#1565C0`.
  - Scripts de la página cargados en este orden en `index.html`: `data/links.js`, `data/feed.js`, `assets/render.js`, `assets/carrusel.js`, `assets/app.js`.

- [ ] **Step 1: Init del proyecto y repo git**

```bash
cd C:/Users/--X/Desktop/PILAR/site
git init
```

- [ ] **Step 2: Crear `package.json`**

```json
{
  "name": "unen-industrial-e",
  "version": "1.0.0",
  "private": true,
  "description": "Pagina link-in-bio UNEN Industrial (variante E) - estatica, sin dependencias",
  "scripts": {
    "test": "node --test"
  }
}
```

- [ ] **Step 3: Escribir el test de estructura (falla primero)**

`site/test/estructura.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(ROOT, 'assets', 'estilo.css'), 'utf8');

test('index.html tiene la estructura base de la variante E', () => {
  assert.match(html, /id="p4phone"/);
  assert.match(html, /class="phone2 v-E"/);
  assert.match(html, /hero-bp/);
  assert.match(html, /class="car"/);
  assert.match(html, /class="lklist"/);
});

test('hay 4 slides con data-net ig/fb/tt/wa y 4 dots', () => {
  const nets = ['ig', 'fb', 'tt', 'wa'];
  for (const n of nets) assert.match(html, new RegExp('data-net="' + n + '"'));
  const slides = html.match(/class="sl"/g) || [];
  assert.strictEqual(slides.length, 4);
});

test('los 4 simbolos SVG usados existen', () => {
  for (const id of ['i-fb', 'i-tt', 'i-wa', 'i-heart', 'i-cmt', 'i-share']) {
    assert.match(html, new RegExp('id="' + id + '"'));
  }
});

test('el CSS conserva los tokens verbatim de la variante E', () => {
  assert.match(css, /--acc:\s*#1565C0/);
  assert.match(css, /\.phone2\.v-E\s*\{/);
  assert.match(css, /\.bp\s*\{/);
  assert.match(css, /\.car\s+\.track\s*\{/);
  assert.match(css, /\.core\s*\{/);
  assert.match(css, /--bg:\s*#F3F4F6/);
});

test('el CSS no arrastra selectores de otras variantes', () => {
  assert.doesNotMatch(css, /\.phone2\.v-A\s*\{/);
  assert.doesNotMatch(css, /\.phone2\.v-D\s*\{/);
  assert.doesNotMatch(css, /\.pchip/);
  assert.doesNotMatch(css, /\.newbox/);
});

test('la pagina centra la columna en fondo oscuro', () => {
  assert.match(css, /max-width:\s*430px/);
  assert.match(css, /#0B0F18|#0b0f18/);
});

test('respeta prefers-reduced-motion', () => {
  assert.match(css, /prefers-reduced-motion/);
});
```

- [ ] **Step 4: Ejecutar el test y verlo fallar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: FAIL — `index.html` no existe (`ENOENT`).

- [ ] **Step 5: Crear `assets/estilo.css`**

Copiar **verbatim** del mockup `entregable/mockup.html` los bloques CSS usados por E y descartar los de otras variantes. Contenido resultante (fusionando los bloques originales en un solo archivo):

```css
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:#0B0F18;
  font-family:Poppins,system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;
  min-height:100vh;
  display:flex;
  justify-content:center;
  align-items:flex-start;
  padding:18px 14px 24px;
}
.phone2{ --bg:#F3F4F6; --panel:#FFFFFF; --panel2:#FBFBFC; --txt:#0E1116; --mut:#6B7280; --acc:#D2232A; --lnb:rgba(14,17,22,.10);
  position:relative; isolation:isolate; overflow:hidden; border-radius:26px; border:1px solid rgba(14,17,22,.08);
  padding:28px 15px 26px; min-height:660px; color:var(--txt); background:var(--bg);
  box-shadow:0 26px 60px rgba(14,17,22,.22);
  width:100%; max-width:430px; margin:0 auto;
  background-image:repeating-linear-gradient(0deg,rgba(21,101,192,.06) 0 1px,transparent 1px 26px),
                   repeating-linear-gradient(90deg,rgba(21,101,192,.06) 0 1px,transparent 1px 26px); }
.phone2.v-E { --acc:#1565C0; --glow1:rgba(21,101,192,.20); --glow2:rgba(30,64,120,.11); --glow3:rgba(21,101,192,.11); }

.phone2 .blob { position:absolute; border-radius:50%; z-index:-1; filter:blur(56px); }
.phone2 .b1 { width:210px; height:210px; left:-90px; bottom:-90px; background:var(--glow1); animation:d1 17s ease-in-out infinite alternate; }
.phone2 .b2 { width:200px; height:200px; right:-80px; top:-60px; background:var(--glow2); animation:d2 21s ease-in-out infinite alternate; }
.phone2 .b3 { width:180px; height:180px; right:-56px; bottom:30px; background:var(--glow3); animation:d1 26s ease-in-out infinite alternate-reverse; }
@keyframes d1 { from{transform:translate(0,0) scale(1)} to{transform:translate(30px,-26px) scale(1.2)} }
@keyframes d2 { from{transform:translate(0,0) scale(1.12)} to{transform:translate(-28px,26px) scale(.9)} }

.hero { display:none; }
.phone2.v-E .hero-bp { display:block; }

.core { position:absolute; left:50%; top:50%; width:clamp(146px,46vw,172px); aspect-ratio:1; transform:translate(-50%,-50%);
  border-radius:50%; background:#fff; overflow:hidden;
  box-shadow:0 12px 30px rgba(0,0,0,.20), 0 0 0 1px rgba(14,17,22,.06); }
.core img { width:100%; height:100%; object-fit:cover; object-position:41% 50%; transform:scale(1.18); display:block; }

.bp { position:relative; width:236px; height:236px; margin:16px auto 30px; }
.bp .ring1 { position:absolute; inset:5px; border-radius:50%; border:1px dashed color-mix(in srgb, var(--acc) 45%, transparent); animation:turn 60s linear infinite; }
.bp .ring2 { position:absolute; inset:26px; border-radius:50%; border:1px solid var(--lnb); }
.bp .axes { position:absolute; inset:0; border-radius:50%; opacity:.5;
  background:
    linear-gradient(to right, transparent calc(50% - .5px), color-mix(in srgb, var(--acc) 50%, transparent) calc(50% - .5px), color-mix(in srgb, var(--acc) 50%, transparent) calc(50% + .5px), transparent calc(50% + .5px)),
    linear-gradient(to bottom, transparent calc(50% - .5px), color-mix(in srgb, var(--acc) 50%, transparent) calc(50% - .5px), color-mix(in srgb, var(--acc) 50%, transparent) calc(50% + .5px), transparent calc(50% + .5px));
  -webkit-mask:radial-gradient(closest-side, transparent 56%, #000 58%);
          mask:radial-gradient(closest-side, transparent 56%, #000 58%); }
.bp .corners i { position:absolute; width:20px; height:20px; border:2px solid color-mix(in srgb, var(--acc) 60%, transparent); }
.bp .corners i:nth-child(1){ left:0; top:0; border-right:0; border-bottom:0; border-radius:7px 0 0 0; }
.bp .corners i:nth-child(2){ right:0; top:0; border-left:0; border-bottom:0; border-radius:0 7px 0 0; }
.bp .corners i:nth-child(3){ right:0; bottom:0; border-left:0; border-top:0; border-radius:0 0 7px 0; }
.bp .corners i:nth-child(4){ left:0; bottom:0; border-right:0; border-top:0; border-radius:0 0 0 7px; }

.car { display:none; }
.phone2.v-E .car { display:block; margin:14px 0 0; }
.car .live { display:flex; align-items:center; gap:6px; font-size:.55rem; text-transform:uppercase; letter-spacing:.08em; color:var(--mut); margin-bottom:7px; }
.car .live i { width:6px; height:6px; border-radius:50%; background:var(--acc); animation:pulse 2s ease-in-out infinite; }
.car .win { overflow:hidden; border-radius:15px; }
.car .track { display:flex; transition:transform .62s cubic-bezier(.5,.05,.2,1); }
.car .sl { flex:0 0 100%; background:var(--panel); border:1px solid var(--lnb); border-radius:15px; padding:11px; display:flex; gap:11px; }
.car .m { width:92px; height:146px; flex:none; border-radius:11px; position:relative; overflow:hidden; }
.car .m.g1 { background:linear-gradient(155deg,#2b3550,#0d1220 65%); }
.car .m.g2 { background:linear-gradient(155deg,#FEDA75,#D62976 55%,#4F5BD5); }
.car .m.g3 { background:linear-gradient(155deg,#1877F2,#0b3f8a); }
.car .m.g4 { background:linear-gradient(155deg,#25D366,#0f7a63); }
.car .m .play { position:absolute; left:50%; top:50%; width:30px; height:30px; margin:-15px 0 0 -15px; border-radius:50%;
  background:rgba(10,12,20,.40); border:1.5px solid rgba(255,255,255,.85); display:flex; align-items:center; justify-content:center; }
.car .m .play::before { content:''; border-left:9px solid #fff; border-top:6px solid transparent; border-bottom:6px solid transparent; margin-left:3px; }
.car .m .dur { position:absolute; left:6px; bottom:6px; font-size:.5rem; font-weight:600; color:#fff; background:rgba(10,12,20,.55); border-radius:20px; padding:2px 6px; }
.car .m .bub { position:absolute; left:8px; right:8px; height:15px; border-radius:8px; background:rgba(255,255,255,.82); }
.car .m .bub.a { top:46px; } .car .m .bub.b { top:67px; right:30px; }
.car .chipl { position:absolute; right:6px; top:6px; width:20px; height:20px; border-radius:6px;
  display:flex; align-items:center; justify-content:center; color:#fff; box-shadow:0 2px 6px rgba(0,0,0,.25); }
.car .chipl svg { width:12px; height:12px; }
.car .bd { flex:1; min-width:0; display:flex; flex-direction:column; }
.car .hd { display:flex; align-items:center; gap:6px; }
.car .hd .av { width:16px; height:16px; border-radius:50%; flex:none; }
.car .hd .av.i-ig { background:linear-gradient(135deg,#FEDA75,#D62976 55%,#4F5BD5); }
.car .hd .av.i-fb { background:#1877F2; }
.car .hd .av.i-tt { background:#010101; border:1px solid rgba(255,255,255,.35); }
.car .hd .av.i-wa { background:#25D366; }
.car .hd b { font-size:.62rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.car .hd .tm { margin-left:auto; font-size:.52rem; color:var(--mut); flex:none; }
.car .cap { font-size:.7rem; line-height:1.35; margin-top:8px; }
.car .cap em { font-style:normal; font-weight:700; color:var(--acc); }
.car .cap.fresh { animation:fresh .9s ease-out; }
@keyframes fresh { from{ opacity:.2; transform:translateY(4px) } to{ opacity:1; transform:none } }
.car .st { margin-top:auto; padding-top:8px; display:flex; gap:11px; align-items:center; color:var(--mut); font-size:.57rem; }
.car .st span { display:flex; align-items:center; gap:4px; }
.car .st b { font-weight:600; }
.car .st svg { width:13px; height:13px; }
.car .dots { display:flex; gap:6px; justify-content:center; margin-top:10px; }
.car .dots i { width:6px; height:6px; border-radius:50%; background:var(--lnb); transition:.3s; }
.car .dots i.on { background:var(--acc); transform:scale(1.45); }

.phone2 h4 { font-size:1.12rem; font-weight:800; text-align:center; margin:12px 0 0; letter-spacing:.01em; }
.phone2 h4 em { font-style:normal; color:var(--acc); }
.phone2 .sub { font-size:.68rem; color:var(--mut); text-align:center; margin-top:3px; line-height:1.35; }

.stats { display:flex; gap:7px; margin:14px 0 4px; }
.stats div { flex:1; background:var(--panel); border:1px solid var(--lnb); border-radius:12px; padding:8px 6px; text-align:center; }
.stats b { display:block; font-size:.9rem; font-weight:700; }
.stats span { font-size:.54rem; color:var(--mut); text-transform:uppercase; letter-spacing:.06em; }

.lk2 { display:flex; align-items:center; gap:11px; padding:12px; border-radius:14px; margin-top:9px;
  background:var(--panel); border:1px solid var(--lnb); position:relative; overflow:hidden; }
.lk2 .chipl { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex:none;
  background:var(--panel2); border:1px solid var(--lnb); color:var(--txt); box-shadow:0 4px 12px rgba(0,0,0,.14); }
.lk2 .chipl svg { width:18px; height:18px; }
.lk2 .tx { flex:1; font-size:.79rem; font-weight:600; line-height:1.12; }
.lk2 .tx small { display:block; font-weight:400; font-size:.6rem; color:var(--mut); margin-top:2px; }
.lk2 .led { width:7px; height:7px; border-radius:50%; background:var(--acc); box-shadow:0 0 9px var(--acc); flex:none; animation:pulse 2.2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:.35; transform:scale(.85)} 50%{opacity:1; transform:scale(1)} }
.lk2::before { content:''; position:absolute; top:0; left:-40%; width:40%; height:100%;
  background:linear-gradient(90deg,transparent,color-mix(in srgb, var(--acc) 20%, transparent),transparent);
  animation:sheen 5.5s ease-in-out infinite; }
.lk2:nth-of-type(2)::before{ animation-delay:.5s } .lk2:nth-of-type(3)::before{ animation-delay:1s }
.lk2:nth-of-type(4)::before{ animation-delay:1.5s } .lk2:nth-of-type(5)::before{ animation-delay:2s }
@keyframes sheen { 0%{left:-40%} 55%{left:130%} 100%{left:130%} }

@keyframes turn { to{ transform:rotate(360deg) } }

.phone2.v-E .stats { display:none; }
.phone2.v-E .lklist { display:flex; flex-direction:column; gap:10px; margin-top:10px; }
.phone2.v-E .lklist .lk2 { margin-top:0; padding:14px 15px; border-radius:15px; gap:13px;
  transition:transform .28s cubic-bezier(.2,.7,.2,1), box-shadow .28s, border-color .28s; }
.phone2.v-E .lklist .lk2 .chipl { width:44px; height:44px; border-radius:13px; }
.phone2.v-E .lklist .lk2 .chipl svg { width:22px; height:22px; }
.phone2.v-E .lklist .lk2 .tx { font-size:.86rem; }
.phone2.v-E .lklist .lk2 .tx small { font-size:.64rem; }
.phone2.v-E .lklist .lk2:hover { transform:translateY(-2px); border-color:color-mix(in srgb, var(--acc) 50%, transparent); box-shadow:0 14px 28px rgba(0,0,0,.14); }

.chipl.ig { background:linear-gradient(135deg,#FEDA75 0%,#FA7E1E 26%,#D62976 58%,#962FBF 82%,#4F5BD5 100%); color:#fff; border-color:transparent; }
.chipl.fb { background:#1877F2; color:#fff; border-color:transparent; }
.chipl.tt { background:#010101; color:#fff; border-color:rgba(255,255,255,.30); }
.chipl.wa { background:#25D366; color:#fff; border-color:transparent; }
.lk2 .chipl.ig { background:linear-gradient(135deg,#FEDA75 0%,#FA7E1E 26%,#D62976 58%,#962FBF 82%,#4F5BD5 100%); color:#fff; border-color:transparent; }
.lk2 .chipl.fb { background:#1877F2; color:#fff; border-color:transparent; }
.lk2 .chipl.tt { background:#010101; color:#fff; border-color:rgba(255,255,255,.30); }
.lk2 .chipl.wa { background:#25D366; color:#fff; border-color:transparent; }

@media (prefers-reduced-motion: reduce) {
  .phone2 .blob, .bp .ring1, .car .live i, .lk2 .led, .lk2::before { animation:none !important; }
  .car .track { transition:none; }
}
```

- [ ] **Step 6: Crear `index.html`**

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>UNEN Industrial</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/estilo.css">
</head>
<body>

<div class="phone2 v-E" id="p4phone">
  <div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>

  <div class="hero hero-bp">
    <div class="bp">
      <div class="ring1"></div>
      <div class="axes"></div>
      <div class="ring2"></div>
      <div class="corners"><i></i><i></i><i></i><i></i></div>
      <div class="core"><img src="logo.png" alt="UNEN – ANEID"></div>
    </div>
  </div>

  <h4>UNEN <em>Industrial</em></h4>
  <div class="sub">UNEN–ANEID · Universidad Nacional de Ingeniería</div>

  <div class="car">
    <div class="live"><i></i>Actividad de las redes · se actualiza sola</div>
    <div class="win">
      <div class="track">
        <div class="sl" data-net="ig"><div class="m g2"><span class="chipl ig"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none"/></svg></span><div class="play"></div><div class="dur">0:21</div></div><div class="bd"><div class="hd"><span class="av i-ig"></span><b class="who">@unen_industrial</b><span class="tm">hace 2 d</span></div><div class="cap">Reel: cómo se calcula un <em>tiempo estándar</em> en planta 👷</div><div class="st"><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-heart"/></svg><b>1.2K</b></span><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-cmt"/></svg><b>84</b></span><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-share"/></svg><b>21</b></span></div></div></div>
        <div class="sl" data-net="fb"><div class="m g3"><span class="chipl fb"><svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-fb"/></svg></span></div><div class="bd"><div class="hd"><span class="av i-fb"></span><b class="who">UNEN Industrial UNI</b><span class="tm">ayer</span></div><div class="cap">Recorrido por la <em>planta de producción</em> 🏭</div><div class="st"><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-heart"/></svg><b>640</b></span><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-cmt"/></svg><b>37</b></span><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-share"/></svg><b>9</b></span></div></div></div>
        <div class="sl" data-net="tt"><div class="m g1"><span class="chipl tt"><svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-tt"/></svg></span><div class="play"></div><div class="dur">0:34</div></div><div class="bd"><div class="hd"><span class="av i-tt"></span><b class="who">@unen_ind</b><span class="tm">hace 2 d</span></div><div class="cap">Un día en <em>Ingeniería Industrial</em> 🎬</div><div class="st"><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-heart"/></svg><b>4.2K</b></span><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-cmt"/></svg><b>312</b></span><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><use href="#i-share"/></svg><b>76</b></span></div></div></div>
        <div class="sl" data-net="wa"><div class="m g4"><span class="chipl wa"><svg viewBox="0 0 24 24" fill="currentColor"><use href="#i-wa"/></svg></span><div class="bub a"></div><div class="bub b"></div></div><div class="bd"><div class="hd"><span class="av i-wa"></span><b class="who">Canal UNEN</b><span class="tm">ahora</span></div><div class="cap">Aviso: charla de <em>seguridad industrial</em>, jueves 4 pm 📢</div><div class="st"><span><b>460 vistas</b></span><span><b>12 reenvíos</b></span></div></div></div>
      </div>
    </div>
    <div class="dots"><i class="on"></i><i></i><i></i><i></i></div>
  </div>

  <div class="stats">
    <div><b>2K</b><span>Seguidores</span></div>
    <div><b>4</b><span>Redes</span></div>
    <div><b>+120</b><span>Publicaciones</span></div>
  </div>

  <div class="lklist"></div>
</div>

<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-fb" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></symbol>
  <symbol id="i-tt" viewBox="0 0 24 24"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.16 15.3a6.34 6.34 0 0010.98 4.36V13.3a8.16 8.16 0 004.77 1.52V11.4a4.85 4.85 0 01-1.32-.2z"/></symbol>
  <symbol id="i-wa" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></symbol>
  <symbol id="i-heart" viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21.2l7.8-7.7 1-1.1a5.5 5.5 0 0 0 0-7.8z"/></symbol>
  <symbol id="i-cmt" viewBox="0 0 24 24"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.4 8.9 8.9 0 0 1-3.9-.9L3 21l1.9-5.3a8.4 8.4 0 0 1 8.6-12.6A8.4 8.4 0 0 1 21 11.5z"/></symbol>
  <symbol id="i-share" viewBox="0 0 24 24"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M16 6l-4-4-4 4"/><path d="M12 2v14"/></symbol>
</svg>

<script src="data/links.js"></script>
<script src="data/feed.js"></script>
<script src="assets/render.js"></script>
<script src="assets/carrusel.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
```

- [ ] **Step 7: Copiar el logo**

```bash
cp C:/Users/--X/Desktop/PILAR/mockups/logo.png C:/Users/--X/Desktop/PILAR/site/logo.png
```

- [ ] **Step 8: Crear placeholders vacíos para los scripts referenciados (para que el test y la página no den 404)**

Crear `data/links.js`, `data/feed.js`, `assets/render.js`, `assets/carrusel.js`, `assets/app.js` con una línea vacía cada uno. Se rellenan en Task 2–4.

- [ ] **Step 9: Ejecutar el test y verlo pasar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: PASS (tests de estructura). Los scripts vacíos no rompen.

- [ ] **Step 10: Verificación manual visual**

Abrir `index.html` con doble clic y comparar contra `entregable/mockup.html?v=E&embed=1`.
Expected: aro de plano técnico azul, rejilla azul, título, carrusel con 4 tarjetas (estáticas), botones vacíos. Diseño idéntico.

- [ ] **Step 11: Crear `README.md`**

```markdown
# UNEN Industrial · página E

Página link-in-bio estática (variante E "Papel + carrusel"). Sin dependencias ni build.

## Uso local
- Abrir `index.html` (doble clic) — funciona sin servidor.
- Opcional (para probar `feed.json`): `python -m http.server 8080` y abrir `http://localhost:8080/`.

## Editar
- Enlaces reales: `data/links.js` (campo `url`).
- Publicaciones del carrusel: `data/feed.js` (curado) y/o `data/feed.json` (auto).

## Pruebas
`npm test` (usa el test runner de Node, sin instalar nada).
```

- [ ] **Step 12: Commit**

```bash
cd C:/Users/--X/Desktop/PILAR/site
git add -A
git commit -m "feat: estructura + CSS variante E verbatim + pagina estatica"
```

---

### Task 2: Datos — `data/links.js` y `data/feed.js`

**Files:**
- Create: `site/data/links.js`
- Create: `site/data/feed.js`
- Create: `site/test/datos.test.js`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `globalThis.UNEN_LINKS` = objeto con claves `instagram|facebook|tiktok|whatsapp`; cada valor `{ label:string, handle:string, url:string, net:'ig'|'fb'|'tt'|'wa' }`.
  - `globalThis.UNEN_FEED` = `{ rotationMs:number, order:string[], pool:{ [net]: Array<{ tm:string, dur?:string, cap:string, st:string[] }> } }`.

- [ ] **Step 1: Escribir el test de datos (falla primero)**

`site/test/datos.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
require('../data/links.js');
require('../data/feed.js');

const LINKS = globalThis.UNEN_LINKS;
const FEED = globalThis.UNEN_FEED;

test('UNEN_LINKS tiene las 4 redes con net y url', () => {
  for (const key of ['instagram', 'facebook', 'tiktok', 'whatsapp']) {
    assert.ok(LINKS[key], 'falta ' + key);
    assert.ok(['ig', 'fb', 'tt', 'wa'].includes(LINKS[key].net));
    assert.strictEqual(typeof LINKS[key].url, 'string');
    assert.strictEqual(typeof LINKS[key].label, 'string');
    assert.strictEqual(typeof LINKS[key].handle, 'string');
  }
});

test('UNEN_FEED tiene order y pools de 3 por red', () => {
  assert.deepStrictEqual(FEED.order, ['ig', 'fb', 'tt', 'wa']);
  assert.ok(FEED.rotationMs > 0);
  for (const net of FEED.order) {
    assert.strictEqual(FEED.pool[net].length, 3, net + ' debe tener 3 publicaciones');
    for (const p of FEED.pool[net]) {
      assert.strictEqual(typeof p.tm, 'string');
      assert.strictEqual(typeof p.cap, 'string');
      assert.ok(Array.isArray(p.st) && p.st.length >= 2);
    }
  }
});
```

- [ ] **Step 2: Ejecutar y verlo fallar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: FAIL — `UNEN_LINKS` es `undefined`.

- [ ] **Step 3: Escribir `data/links.js`**

```js
(function (root) {
  root.UNEN_LINKS = {
    instagram: { label: 'Instagram', handle: '@unen_industrial', url: '#', net: 'ig' },
    facebook: { label: 'Facebook Oficial', handle: 'UNEN Industrial UNI', url: '#', net: 'fb' },
    tiktok: { label: 'TikTok', handle: '@unen_ind', url: '#', net: 'tt' },
    whatsapp: { label: 'Canal de WhatsApp', handle: 'Divulgación y avisos', url: '#', net: 'wa' }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
```

- [ ] **Step 4: Escribir `data/feed.js`**

```js
(function (root) {
  root.UNEN_FEED = {
    rotationMs: 6000,
    order: ['ig', 'fb', 'tt', 'wa'],
    pool: {
      ig: [
        { tm: 'hace 2 d', dur: '0:21', cap: 'Reel: cómo se calcula un <em>tiempo estándar</em> en planta', st: ['1.2K', '84', '21'] },
        { tm: 'hoy', dur: '0:38', cap: 'Nuevo reel: <em>5S</em> aplicado a un taller pequeño', st: ['3.4K', '210', '58'] },
        { tm: 'hace 4 d', dur: '0:16', cap: 'Carrusel: <em>salidas laborales</em> de Ing. Industrial', st: ['980', '63', '17'] }
      ],
      fb: [
        { tm: 'ayer', cap: 'Recorrido por la <em>planta de producción</em>', st: ['640', '37', '9'] },
        { tm: 'hace 3 d', cap: 'Álbum: <em>feria de proyectos</em> de la carrera', st: ['1.1K', '52', '23'] },
        { tm: 'hace 6 d', cap: 'Convocatoria abierta a <em>nuevos miembros</em>', st: ['870', '41', '31'] }
      ],
      tt: [
        { tm: 'hace 2 d', dur: '0:34', cap: 'Un día en <em>Ingeniería Industrial</em>', st: ['4.2K', '312', '76'] },
        { tm: 'hoy', dur: '0:27', cap: 'POV: <em>primer día</em> en el laboratorio', st: ['6.8K', '540', '132'] },
        { tm: 'hace 5 d', dur: '0:45', cap: 'Así se arma un <em>diagrama de Ishikawa</em>', st: ['2.7K', '188', '44'] }
      ],
      wa: [
        { tm: 'ahora', cap: 'Aviso: charla de <em>seguridad industrial</em>, jueves 4 pm', st: ['460 vistas', '12 reenvíos'] },
        { tm: 'hace 1 d', cap: 'Recordatorio: entrega de <em>informe de prácticas</em>', st: ['1.2K vistas', '38 reenvíos'] },
        { tm: 'hace 2 d', cap: 'Publicado el calendario de <em>exámenes</em> del semestre', st: ['2.1K vistas', '64 reenvíos'] }
      ]
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
```

- [ ] **Step 5: Ejecutar el test y verlo pasar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: PASS (datos + estructura).

- [ ] **Step 6: Commit**

```bash
git add data/links.js data/feed.js test/datos.test.js
git commit -m "feat: datos de enlaces y publicaciones del carrusel"
```

---

### Task 3: Lógica pura — `assets/render.js` y `assets/carrusel.js`

**Files:**
- Create: `site/assets/render.js`
- Create: `site/assets/carrusel.js`
- Create: `site/test/render.test.js`
- Create: `site/test/carrusel.test.js`

**Interfaces:**
- Consumes: nada (funciones puras).
- Produces:
  - `Render.linkButtonHTML(net, cfg)` → `string` con el markup `<a class="lk2" ...>` del botón de red. `cfg = {label, handle, url}`.
  - `Render.iconSVG(net)` → `string` con el `<svg>` del icono de la red (`ig` dibujado inline; `fb`/`tt`/`wa` vía `<use href="#i-X">`).
  - `Carrusel.nextIndex(cur, total)` → `(cur + 1) % total` (0 si `total===0`).
  - `Carrusel.cyclePool(cur, len)` → `(cur + 1) % len` (0 si `len===0`).
  - `Carrusel.orderSlides(present, order)` → array de nets: los de `order` que estén en `present`, seguidos de los de `present` no listados en `order`.

- [ ] **Step 1: Escribir los tests (fallan primero)**

`site/test/carrusel.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const C = require('../assets/carrusel.js');

test('nextIndex avanza y cicla', () => {
  assert.strictEqual(C.nextIndex(0, 4), 1);
  assert.strictEqual(C.nextIndex(3, 4), 0);
  assert.strictEqual(C.nextIndex(0, 0), 0);
});

test('cyclePool cicla el pool', () => {
  assert.strictEqual(C.cyclePool(1, 3), 2);
  assert.strictEqual(C.cyclePool(2, 3), 0);
  assert.strictEqual(C.cyclePool(5, 0), 0);
});

test('orderSlides respeta orden y agrega los no listados', () => {
  assert.deepStrictEqual(C.orderSlides(['ig', 'fb', 'tt', 'wa'], ['ig', 'fb', 'tt', 'wa']),
    ['ig', 'fb', 'tt', 'wa']);
  assert.deepStrictEqual(C.orderSlides(['tt', 'ig'], ['ig', 'fb', 'tt', 'wa']), ['ig', 'tt']);
  assert.deepStrictEqual(C.orderSlides(['ig', 'xx'], ['ig']), ['ig', 'xx']);
  assert.deepStrictEqual(C.orderSlides([], ['ig']), []);
});
```

`site/test/render.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const Render = require('../assets/render.js');

test('linkButtonHTML genera un <a> con url, label, handle y net', () => {
  const html = Render.linkButtonHTML('ig', { label: 'Instagram', handle: '@u', url: 'https://x' });
  assert.match(html, /^<a class="lk2"/);
  assert.match(html, /href="https:\/\/x"/);
  assert.match(html, /Instagram/);
  assert.match(html, /@u/);
  assert.match(html, /class="chipl ig"/);
});

test('linkButtonHTML con url placeholder "#" no navega', () => {
  const html = Render.linkButtonHTML('fb', { label: 'FB', handle: 'h', url: '#' });
  assert.doesNotMatch(html, /target="_blank"/);
  assert.match(html, /aria-disabled="true"/);
});

test('linkButtonHTML con url real abre en pestana nueva', () => {
  const html = Render.linkButtonHTML('fb', { label: 'FB', handle: 'h', url: 'https://fb.com' });
  assert.match(html, /target="_blank"/);
  assert.match(html, /rel="noopener"/);
});

test('iconSVG usa <use> para fb/tt/wa e inline para ig', () => {
  assert.match(Render.iconSVG('fb'), /href="#i-fb"/);
  assert.match(Render.iconSVG('tt'), /href="#i-tt"/);
  assert.match(Render.iconSVG('wa'), /href="#i-wa"/);
  assert.match(Render.iconSVG('ig'), /<rect/);
});
```

- [ ] **Step 2: Ejecutar y verlo fallar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: FAIL — módulos no existen.

- [ ] **Step 3: Escribir `assets/carrusel.js`**

```js
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
  return { nextIndex: nextIndex, cyclePool: cyclePool, orderSlides: orderSlides };
});
```

- [ ] **Step 4: Escribir `assets/render.js`**

```js
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

  function linkButtonHTML(net, cfg) {
    var isPlaceholder = !cfg.url || cfg.url === '#';
    var attrs = isPlaceholder
      ? ' href="#" aria-disabled="true"'
      : ' href="' + cfg.url + '" target="_blank" rel="noopener"';
    return '<a class="lk2"' + attrs + '>' +
      '<div class="chipl ' + net + '">' + iconSVG(net) + '</div>' +
      '<div class="tx">' + cfg.label + '<small>' + cfg.handle + '</small></div>' +
      '<div class="led"></div>' +
      '</a>';
  }

  return { iconSVG: iconSVG, linkButtonHTML: linkButtonHTML };
});
```

- [ ] **Step 5: Ejecutar el test y verlo pasar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: PASS (carrusel + render + datos + estructura).

- [ ] **Step 6: Commit**

```bash
git add assets/render.js assets/carrusel.js test/render.test.js test/carrusel.test.js
git commit -m "feat: modulos puros de render y logica de carrusel"
```

---

### Task 4: `app.js` — cableado DOM, carrusel y fallback de datos

**Files:**
- Create: `site/assets/app.js`
- Create: `site/data/feed.json`
- Create: `site/test/feedjson.test.js`

**Interfaces:**
- Consumes: `window.Render`, `window.Carrusel`, `window.UNEN_LINKS`, `window.UNEN_FEED`; nodos `#p4phone .lklist`, `.car .track .sl`, `.car .dots`.
- Produces: página funcional (enlaces + carrusel en vivo). Sin API exportada.

- [ ] **Step 1: Escribir el test de esquema de `feed.json` (falla primero)**

`site/test/feedjson.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const raw = fs.readFileSync(path.join(__dirname, '..', 'data', 'feed.json'), 'utf8');
const json = JSON.parse(raw);

test('feed.json tiene el mismo esquema que UNEN_FEED', () => {
  assert.strictEqual(typeof json.rotationMs, 'number');
  assert.deepStrictEqual(json.order, ['ig', 'fb', 'tt', 'wa']);
  for (const net of json.order) {
    assert.strictEqual(json.pool[net].length, 3);
  }
});
```

- [ ] **Step 2: Ejecutar y verlo fallar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: FAIL — `data/feed.json` no existe.

- [ ] **Step 3: Crear `data/feed.json`** (mismo cuerpo que `UNEN_FEED`, sin el envoltorio de script)

```json
{
  "rotationMs": 6000,
  "order": ["ig", "fb", "tt", "wa"],
  "pool": {
    "ig": [
      { "tm": "hace 2 d", "dur": "0:21", "cap": "Reel: cómo se calcula un <em>tiempo estándar</em> en planta", "st": ["1.2K", "84", "21"] },
      { "tm": "hoy", "dur": "0:38", "cap": "Nuevo reel: <em>5S</em> aplicado a un taller pequeño", "st": ["3.4K", "210", "58"] },
      { "tm": "hace 4 d", "dur": "0:16", "cap": "Carrusel: <em>salidas laborales</em> de Ing. Industrial", "st": ["980", "63", "17"] }
    ],
    "fb": [
      { "tm": "ayer", "cap": "Recorrido por la <em>planta de producción</em>", "st": ["640", "37", "9"] },
      { "tm": "hace 3 d", "cap": "Álbum: <em>feria de proyectos</em> de la carrera", "st": ["1.1K", "52", "23"] },
      { "tm": "hace 6 d", "cap": "Convocatoria abierta a <em>nuevos miembros</em>", "st": ["870", "41", "31"] }
    ],
    "tt": [
      { "tm": "hace 2 d", "dur": "0:34", "cap": "Un día en <em>Ingeniería Industrial</em>", "st": ["4.2K", "312", "76"] },
      { "tm": "hoy", "dur": "0:27", "cap": "POV: <em>primer día</em> en el laboratorio", "st": ["6.8K", "540", "132"] },
      { "tm": "hace 5 d", "dur": "0:45", "cap": "Así se arma un <em>diagrama de Ishikawa</em>", "st": ["2.7K", "188", "44"] }
    ],
    "wa": [
      { "tm": "ahora", "cap": "Aviso: charla de <em>seguridad industrial</em>, jueves 4 pm", "st": ["460 vistas", "12 reenvíos"] },
      { "tm": "hace 1 d", "cap": "Recordatorio: entrega de <em>informe de prácticas</em>", "st": ["1.2K vistas", "38 reenvíos"] },
      { "tm": "hace 2 d", "cap": "Publicado el calendario de <em>exámenes</em> del semestre", "st": ["2.1K vistas", "64 reenvíos"] }
    ]
  }
}
```

- [ ] **Step 4: Escribir `assets/app.js`**

```js
(function () {
  'use strict';

  // ---------- Enlaces ----------
  function renderLinks() {
    var list = document.querySelector('#p4phone .lklist');
    if (!list || !window.UNEN_LINKS || !window.Render) return;
    var order = ['instagram', 'facebook', 'tiktok', 'whatsapp'];
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
    if (cap) cap.innerHTML = post.cap;
    if (tm) tm.textContent = post.tm;
    if (dur && post.dur) dur.textContent = post.dur;
    var st = slide.querySelectorAll('.st b');
    for (var k = 0; k < st.length && k < post.st.length; k++) {
      st[k].textContent = post.st[k];
    }
  }

  function startCarousel(feed) {
    var phone = document.getElementById('p4phone');
    if (!phone || !feed || !feed.pool) return;
    var track = phone.querySelector('.car .track');
    if (!track) return;

    var allSlides = [].slice.call(track.querySelectorAll('.sl'));
    var present = allSlides.map(netOf);
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

    var idx = { ig: 0, fb: 0, tt: 0, wa: 0 };
    var cur = 0;

    function go(n) {
      cur = ((n % slides.length) + slides.length) % slides.length;
      track.style.transform = 'translateX(' + (-cur * 100) + '%)';
      dots.forEach(function (d, i) { d.className = (i === cur) ? 'on' : ''; });
      var cap = slides[cur].querySelector('.cap');
      if (cap) { cap.classList.remove('fresh'); void cap.offsetWidth; cap.classList.add('fresh'); }
      var nxt = slides[window.Carrusel.nextIndex(cur, slides.length)];
      if (nxt) {
        var nn = netOf(nxt);
        var pool = feed.pool[nn] || [];
        idx[nn] = window.Carrusel.cyclePool(idx[nn], pool.length);
        if (pool.length) fillSlide(nxt, pool[idx[nn]]);
      }
    }

    go(0);
    var ms = feed.rotationMs || 6000;
    setInterval(function () { go(cur + 1); }, ms);
  }

  // ---------- Datos con fallback ----------
  function isValidFeed(f) {
    return f && typeof f === 'object' && f.pool && typeof f.pool === 'object';
  }

  function load() {
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
```

- [ ] **Step 5: Ejecutar el test y verlo pasar**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: PASS (todos).

- [ ] **Step 6: Verificación manual — funcional y fallback**

1. Abrir `index.html` (doble clic): carrusel rota cada 6 s, puntos marcan el slide, 4 botones con icono de marca y LED. Clic en cada botón: como la URL es `#` (placeholder), **no navega ni da error** (Review Focus 1).
2. Servidor local: `python -m http.server 8080` en `site/`, abrir `http://localhost:8080/`. El carrusel usa `data/feed.json` (mismo contenido).
3. Fallback (Review Focus 2): renombrar `data/feed.json` a `feed.json.bak`, recargar → el carrusel sigue (usa `feed.js`). Restaurar.
4. Red faltante (Review Focus 3): comentar el pool de `fb` en `feed.js`, abrir en `file://` → 3 slides, 3 puntos, sin error. Revertir.
5. Viewport ~320px (Review Focus 4): sin scroll horizontal.
6. `prefers-reduced-motion` (Review Focus 5): en DevTools → Rendering → emular reduce; aro/LED/carrusel no animan, todo legible.
7. Slide sin `dur` (Review Focus 6): el slide de FB (sin `.dur`) se rellena sin error (ya cubierto al ver el carrusel).

- [ ] **Step 7: Commit**

```bash
git add assets/app.js data/feed.json test/feedjson.test.js
git commit -m "feat: app.js cablea enlaces y carrusel con fallback de datos"
```

---

### Task 5: Actualización de enlaces reales + README + verificación final (sin código nuevo)

**Files:**
- Modify: `site/data/links.js`
- Modify: `site/README.md`

**Interfaces:**
- Consumes: `data/links.js` de Task 2.
- Produces: enlaces reales navegables.

- [ ] **Step 1: Prueba de regresión de enlaces placeholder**

Run: `cd C:/Users/--X/Desktop/PILAR/site && npm test`
Expected: PASS (los tests no dependen de las URLs concretas).

- [ ] **Step 2: Checklist de cierre (manual)**

- [ ] Cada enlace con URL real abre la red en pestaña nueva (`target="_blank"`, `rel="noopener"`).
- [ ] Diseño idéntico a `entregable/mockup.html?v=E&embed=1` (comparación lado a lado).
- [ ] Sin errores en la consola del navegador (en `file://` el 404 de `feed.json` es esperado y manejado).
- [ ] `npm test` en verde.

- [ ] **Step 3: Commit**

```bash
git add data/links.js README.md
git commit -m "docs: README y enlaces reales listos para pegar"
```

---

### Task 6 (Opcional, fase 2): Scaffold del GitHub Action `feed.yml`

> Solo si el usuario provee una fuente RSS gratuita. No bloquea la entrega.
> Sin fuente, el producto ya funciona con datos curados.

**Files:**
- Create: `site/.github/workflows/feed.yml`
- Modify: `site/README.md`

**Interfaces:**
- Consumes: nada.
- Produces: workflow que cada 6 h actualiza `data/feed.json` (best-effort).

- [ ] **Step 1: Escribir `feed.yml`**

```yaml
name: Actualizar feed
on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:
permissions:
  contents: write
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Descargar feeds y generar data/feed.json
        run: |
          echo "TODO: configurar fuente RSS gratuita (Rss.app) y generar el JSON."
          # Placeholder: sin fuente configurada, no modifica el archivo.
      - name: Commit si cambió
        run: |
          git config user.name "github-actions"
          git config user.email "actions@users.noreply.github.com"
          git add data/feed.json
          git diff --cached --quiet || git commit -m "chore: actualizar feed"
          git push || true
```

- [ ] **Step 2: Verificar YAML**

Run: `python -c "import yaml,sys; yaml.safe_load(open('C:/Users/--X/Desktop/PILAR/site/.github/workflows/feed.yml',encoding='utf-8')); print('YAML OK')"`
Expected: `YAML OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/feed.yml README.md
git commit -m "ci: scaffold de actualizacion de feed (fase 2, opcional)"
```

---

## Self-Review

**Cobertura de la spec:**
- Propósito / éxito (funciona local, idéntico, gratis, publicable) → Tasks 1, 4, 5.
- Non-goals (no tocar mockups, sin backend) → Global Constraints + File Structure.
- Restricciones (verbatim, gratis, file://, enlaces luego) → Task 1, Task 5.
- Arquitectura y capa de datos aislada → File Structure + Task 4 (fallback).
- Tokens verbatim → Task 1 Step 5 (+ test).
- Componentes: enlaces → Task 2/3/4; carrusel → Task 3/4; presentación centrada → Task 1.
- Esquema de datos → Task 2 y Task 4 (feed.json).
- Errores/robustez (fallback, red faltante, placeholder) → Task 4 Step 6.
- Pruebas → tests en cada tarea + checklist Task 5.
- Feed fase 2 → Task 6.
- Supuestos/preguntas abiertas: ubicación resuelta en la spec (`site/` con git propio).

**Placeholder scan:** Task 6 contiene un `TODO` intencional y explícito (bloque opcional, no implementable sin la cuenta externa); está marcado como opcional y no bloquea. El resto no tiene placeholders.

**Consistencia de tipos:** `UNEN_LINKS`/`UNEN_FEED` con el mismo esquema en Tasks 2, 3, 4, 5. `Render.linkButtonHTML(net, cfg)`, `Carrusel.nextIndex/cyclePool/orderSlides` se definen en Task 3 y se consumen en Task 4 con las mismas firmas.

**Review Focus:** cada línea tiene su verificación en Task 4 Step 6 (1–6) y/o test (2 vía fallback manual, 6 vía slide FB sin `.dur`, 5 vía media query en Task 1 Step 5).
