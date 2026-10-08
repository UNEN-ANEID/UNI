# Spec — Feed real automatizado para la página E (UNEN Industrial)

- Fecha: 2026-10-07
- Estado: propuesto (pendiente de aprobación del usuario)
- Relacionado: `2026-10-07-unen-e-funcional-design.md` (página E base, ya construida)
- Evidencia previa: `pruebas/REPORTE.md` (métodos gratuitos sin login por red)

## 1. Objetivo

Reemplazar los datos **de demostración** del carrusel de la página E por
publicaciones **reales** de **TikTok, Instagram y Facebook**, actualizadas
**automáticamente una vez al día** con GitHub Actions y publicadas en GitHub
Pages, **sin costo**, sin backend, y sin dejar la página rota cuando una red
falle.

Motivo: el carrusel actual funciona (rota, dots, pools) pero su contenido está
**hardcodeado** (captions y métricas inventadas) y el rótulo "se actualiza sola"
es **falso** hoy. Se quiere que sea verdad.

## 2. Criterios de éxito

1. `site/data/feed.json` **y** `site/data/feed.js` contienen publicaciones
   reales (caption, enlace al post, fecha, miniatura) de TikTok/Instagram/Facebook.
2. Cada slide del carrusel: **enlace a la publicación real** y **miniatura real**
   descargada al repo (si existe; si no, degradado actual).
3. La página se actualiza sola **1 vez/día**; si una red falla, **conserva su
   última tanda real** (nunca queda vacía ni rompe).
4. Funciona en `file://` (datos del último build) y en GitHub Pages.
5. `npm test` verde; el **diseño E no cambia** (CSS E intacto salvo estilos
   nuevos de miniatura/enlace).
6. Costo **cero**; sin backend, sin login, sin tokens de API.

## 3. No-objetivos

- WhatsApp **dentro** del carrusel (sigue solo como botón de enlace).
- Panel de administración, login, analítica, formularios.
- APIs oficiales de Meta/TikTok (requieren token).
- Dominio propio.
- Automatización 100% perfecta de IG/FB (se acepta "semi-auto con degradación").

## 4. Contexto y restricciones

- Repo `UNI` (hoy **privado**) se hará **público**; Pages gratis solo con repo público.
- La página vivirá en `site/` dentro del repo UNI →
  `https://waltersolorzano.github.io/UNI/site/`.
- Restricciones heredadas: CSS E **verbatim** del mockup; **cero build** para la
  página; UI en español; **no tocar** `mockups/` ni el presentador A–F.
- Realidad técnica (de `pruebas/REPORTE.md`):
  - **TikTok**: automatizable de verdad (oEmbed por video; miniatura con expiración ~3 días → hay que descargarla).
  - **Instagram**: sin feed público; única vía sin login = **RSS-Bridge** (instancias públicas frágiles).
  - **Facebook**: HTML directo bloqueado; requiere **navegador headless** (Playwright).
  - **WhatsApp**: imposible sin login.
- El runner de GitHub Actions es IP de datacenter → IG (vía bridge, no toca la IP del runner) y TikTok suelen ir; **FB es el eslabón frágil**.

## 5. Arquitectura

```
repo UNI (público)
├─ site/                        ← página E (se mueve desde PILAR/site)
│   ├─ index.html
│   ├─ assets/{estilo.css,render.js,carrusel.js,app.js}
│   ├─ assets/posts/*.jpg       ← miniaturas REALES descargadas
│   ├─ data/{links.js,feed.js,feed.json}
│   ├─ test/*.test.js
│   └─ docs/superpowers/{specs,plans}/
├─ tools/build_feed.py          ← pipeline (corre en la Action)
└─ .github/workflows/feed.yml   ← cron diario + dispatch manual
```

- **GitHub Pages**: rama `main`, carpeta `/` → URL `.../UNI/site/`.
- La carpeta `site/` pierde su `.git` interno al integrarse al repo UNI.
- Reparto de roles: la **Action** corre Python (TikTok/IG/FB) y **commitea**
  `feed.json` + `feed.js` + `assets/posts/*.jpg`; **Pages** solo los sirve.

## 6. Componentes

### 6.1 `tools/build_feed.py` (el pipeline)

- Responsabilidad única: producir un `feed` normalizado y **nunca** romper el Action.
- Funciones por red (independientes entre sí):
  - `fetch_tiktok()` → GET `https://www.tiktok.com/embed/@unen.industrial.uni`
    para listar ids de video; por cada id, GET oEmbed
    (`https://www.tiktok.com/oembed?url=<video url>`) → `title`, `thumbnail_url`.
    Descarga la miniatura a `site/assets/posts/tt_<id>.jpg`.
  - `fetch_instagram()` → intenta varias instancias de **RSS-Bridge** (Atom) con
    reintentos; extrae caption, fecha, enlace y miniatura; descarga la imagen.
  - `fetch_facebook()` → **Playwright** headless sobre el Page Plugin; extrae
    texto, permalink, fecha e imagen; descarga la imagen.
- Normaliza cada post a: `{ net, cap, url, tm, img?, st? }`.
  - `cap`: texto real (plano; se sanea igual con `Render.safeCaption`).
  - `url`: enlace **real** a la publicación.
  - `tm`: fecha legible ("hace 2 d") calculada desde la fecha real.
  - `img`: ruta relativa `assets/posts/...` (opcional).
  - `st`: métricas **solo si son reales**; si no hay dato, se omite (la fila se oculta).
- **Conserva lo último bueno**: lee el `feed.json` previo y, si una red falla,
  mantiene sus entradas anteriores.
- Escribe **`feed.json` y `feed.js`** con los mismos datos reales (para que
  `file://` también muestre datos reales del último build).
- Limpia miniaturas huérfanas (`assets/posts/`) que ya no se usan.
- Flags: `--check` (valida esquema sin escribir), `--only tt|ig|fb` (depurar una red).
- Reintentos + timeouts; cualquier excepción por red se captura y se degrada.

### 6.2 `.github/workflows/feed.yml`

- `on:` `schedule: [{ cron: '0 6 * * *' }]` (diario 06:00 UTC) + `workflow_dispatch`.
- Pasos: checkout → setup Python 3.13 → `pip install requests` →
  `npx playwright install --with-deps chromium` (para FB) →
  `python tools/build_feed.py` → commit & push si hay cambios.
- `permissions: contents: write`.
- Si no hay cambios, **no** commitea.

### 6.3 Esquema de datos (v2)

```js
UNEN_FEED = {
  generatedAt: '2026-10-07T06:00:00Z',   // ISO, para "Actualizado: ..."
  rotationMs: 6000,
  order: ['tt', 'ig', 'fb'],             // orden de slides del carrusel
  pool: {
    tt: [ { net:'tt', cap, url, tm, img?, st? }, ... ],
    ig: [ ... ],
    fb: [ ... ]
  }
}
```

- `order` y `pool` pueden traer **menos** redes si alguna no tiene datos
  (el carrusel ya omite redes sin publicaciones y ajusta los dots).
- `st` es **opcional**; `img` es **opcional**.

### 6.4 Cambios en la página

- **Slides estáticos**: se conservan como *seed* sin JS, pero ahora **3**
  (tt/ig/fb). Se **retira el slide `wa`** del carrusel (WhatsApp sale del
  carrusel; su botón de enlace se queda).
- `assets/app.js`:
  - Rellena caption, fecha y métricas; **oculta la fila `.st`** si el post no trae métricas.
  - Si `post.img`, muestra la **miniatura real** en `.m` (si no, degradado actual).
  - Hace el slide **clicable** a `post.url` (overlay `<a>` con `target=_blank rel=noopener`).
  - Rótulo `.live`: pasa de "se actualiza sola" a **"Actualizado: <fecha>"** real,
    derivado de `generatedAt`.
- `assets/estilo.css`: se añaden **solo** estilos nuevos para la miniatura
  (`img` en `.m`, `object-fit:cover`) y el overlay de enlace; **el resto del CSS E
  no se toca**.
- `assets/render.js`: se añaden helpers puros (p. ej. `slideLinkHTML`, `thumbHTML`)
  y se mantiene `safeCaption`.

### 6.5 Miniaturas

- Se **descargan** al repo (las URLs de TikTok/IG caducan). Rutas relativas
  (`assets/posts/...`) para que funcionen en `file://` y en Pages.
- Se purgan las que ya no se referencian.

## 7. Pruebas y verificación

- **Node** (`node --test`):
  - `estructura.test.js`: ahora **3 slides** (tt/ig/fb), sin `wa`; siguen 5 botones.
  - `datos.test.js`: `order = ['tt','ig','fb']`; pools con `net/cap/url/tm` y `img`/`st` opcionales; `generatedAt` presente.
  - `render.test.js`: helpers nuevos (enlace de slide, miniatura) + `safeCaption`.
  - `feedjson.test.js`: `feed.json` cumple el esquema v2 (incluye `generatedAt`).
- **Python**: `python tools/build_feed.py --check` valida el esquema del feed sin escribir.
- **Manual**: correr el workflow con `workflow_dispatch` y confirmar el commit +
  que la página en Pages muestra datos reales.

## 8. Migración (pasos)

1. Hacer **público** el repo `UNI`.
2. Copiar `PILAR/site/` → `UNI/site/` (sin el `.git` interno).
3. Añadir `tools/build_feed.py` y `.github/workflows/feed.yml`.
4. Activar **Pages** (rama `main`, carpeta `/`).
5. Ejecutar el workflow una vez (manual) y verificar.

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Facebook bloquea la IP del runner | "Conserva lo último bueno"; escape hatch = Google Sheet (F4) |
| RSS-Bridge público caído | Varias instancias + reintentos + conserva lo último bueno |
| Miniaturas caducan | Se descargan al repo en cada corrida |
| El repo público expone el presentador A–F | Decisión explícita del usuario (aceptada) |
| Cambios de HTML de las plataformas | El pipeline degrada por red; no rompe la página |

## 10. Fases

- **F1** — Mover `site/` al repo UNI, activar Pages, pipeline **TikTok** + cambios
  de página a "real" (miniatura, enlace, ocultar métricas vacías, rótulo con fecha).
- **F2** — **Instagram** vía RSS-Bridge.
- **F3** — **Facebook** vía Playwright.
- **F4** *(escape hatch, solo si F2/F3 fallan)* — Google Sheet para IG/FB.

## 11. Fuera de alcance / futuro

- Auto-hospedar RSS-Bridge propio (si las instancias públicas no bastan).
- Automatización de WhatsApp (imposible sin login).
- Reintentos más agresivos / cache CDN.
