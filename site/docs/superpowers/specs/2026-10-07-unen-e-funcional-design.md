# Diseño — UNEN Industrial "E" funcional (link-in-bio)

- Fecha: 2026-10-07
- Estado: aprobado en chat (enfoque A), pendiente de revisión de esta spec
- Autor: sesión de diseño

## 1. Propósito

Llevar el **mockup E** ("Papel + carrusel") de `entregable/mockup.html` a una
**página real y funcional**, conservando el diseño **al pie de la letra**.

Producto: página link-in-bio de **UNEN Industrial** (UNEN–ANEID, Universidad
Nacional de Ingeniería). Una columna móvil centrada con:

1. Aro de plano técnico con el logo al centro.
2. Título + subtítulo.
3. Carrusel de redes que rota solo.
4. Botones grandes de enlaces a redes.

## 2. Objetivo de éxito

- La página **funciona** de verdad en local: enlaces abren, carrusel rota, responsive.
- El diseño es **visualmente idéntico** a la variante E del mockup.
- Cero costo. Sin backend obligatorio.
- Lista para publicar (GitHub Pages) sin cambios de código.

## 3. Fuera de alcance (non-goals)

- No se publica todavía.
- No se toca `mockups/` ni el presentador A–F de `entregable/`.
- No hay backend propio, ni login, ni analítica, ni formularios.
- No se implementa feed en vivo con APIs oficiales de Meta/TikTok.
- No se construye un panel de administración.

## 4. Restricciones

- **Diseño al pie de la letra**: el CSS de la variante E se reutiliza verbatim.
- **Gratis total**: solo servicios gratuitos (GitHub, RSS bridge free, Actions free).
- **Sin backend**: operación estática.
- **Enlaces reales pendientes**: el usuario los entregará luego → viven en un
  archivo de datos editable con placeholders ahora.
- **Compatible con `file://`**: doble clic debe funcionar (sin servidor).

## 5. Arquitectura

Proyecto estático, sin build. Capas aisladas:

```
site/
  index.html                 pagina E real (columna max 430px, fondo #0B0F18)
  assets/estilo.css          reglas v-E extraidas VERBATIM del mockup
  assets/app.js              render de enlaces + carrusel + fallback
  data/links.js              window.UNEN_LINKS  (URLs/handles reales, editable)
  data/feed.js               window.UNEN_FEED   (publicaciones curadas, default)
  data/feed.json             mismo esquema; el Action lo sobrescribe (futuro)
.github/workflows/feed.yml   cron gratis -> feed.json (best-effort, opcional)
docs/superpowers/specs/...   esta spec
```

- Repo git propio en `site/` (decidido). No se toca el remoto `UNI.git` de
  `entregable/`; se puede reubicar o empujar después sin cambios de código.
- Despliegue futuro: GitHub Pages sirviendo `site/` en la raíz.

### Capa de datos (aislamiento)

El diseño **no depende** de la fuente de datos. Contrato único:

- `data/links.js` → objeto de 4 redes.
- `data/feed.js` → estructura de carrusel (default embebido).
- `data/feed.json` → mismo esquema que `feed.js`, cargado con `fetch` para el
  modo auto-actualizado.
- `app.js`: intenta `fetch('data/feed.json')`; si falla (p. ej. `file://`),
  usa `window.UNEN_FEED`. **Nunca se rompe.**

Cambiar la fuente del carrusel (curado → Action → API futura) no toca CSS ni HTML.

## 6. Tokens de diseño (variante E — verbatim)

- Fondo página: `#0B0F18`; tipografía `Poppins`.
- Tema E (claro, "papel"):
  - `--bg:#F3F4F6` `--panel:#FFFFFF` `--panel2:#FBFBFC`
  - `--txt:#0E1116` `--mut:#6B7280` `--lnb:rgba(14,17,22,.10)`
  - `--acc:#1565C0` (acento azul)
  - `--glow1:rgba(21,101,192,.20)` `--glow2:rgba(30,64,120,.11)` `--glow3:rgba(21,101,192,.11)`
  - `border-radius:26px`; `padding:28px 15px 26px`; `min-height:660px`
  - Rejilla: `repeating-linear-gradient` 0deg y 90deg, `rgba(21,101,192,.06) 0 1px, transparent 1px 26px`.
- Logo `.core`: `clamp(146px,46vw,172px)`, círculo blanco, `img object-position:41% 50%; transform:scale(1.18)`.
- Aro `.bp` (236×236): `ring1` punteado girando 60s, `ring2` inset 26px sólido,
  `axes` (cruz) con máscara radial, 4 esquinas `corners`.
- Blobs `.blob` con `filter:blur(56px)`, animaciones `d1`/`d2`.
- Colores de marca: IG degradado `#FEDA75→#FA7E1E→#D62976→#962FBF→#4F5BD5`;
  FB `#1877F2`; TikTok `#010101`; WhatsApp `#25D366`.
- Tipografía: `h4` 1.12rem/800 centrado, `em` en `--acc`; `.sub` .68rem `--mut`.

## 7. Componentes y comportamiento

### 7.1 Enlaces (`.lklist`)

- 4 botones **de lado a lado** (estilo Linktree), columna, `gap:10px`.
- Cada botón: cuadrito de marca 44×44, título, `small` con handle, LED pulsante.
- Hover: `translateY(-2px)` + borde acento + sombra.
- `target="_blank" rel="noopener"`. URL desde `data/links.js`.
- Si la URL es placeholder (`#`), el botón no navega (no rompe).

### 7.2 Carrusel (`.car`)

- 4 slides (una por red: ig, fb, tt, wa), visible 1 a la vez.
- Rota cada **6000 ms**; `transform:translateX(-n*100%)`; transición .62s.
- Puntos (`dots`) marcan el slide actual; animación `fresh` al cambiar.
- Al avanzar, el **pool** de la red del siguiente slide avanza (no repite seguido).
- Encabezado "Actividad de las redes · se actualiza sola" con LED.

### 7.3 Presentación

- Columna `max-width:430px` centrada; en escritorio se ve como el modo `embed`.
- Responsive sin cambios: los `clamp()` y `%` del mockup ya lo cubren.

## 8. Esquema de datos

```js
// data/links.js
window.UNEN_LINKS = {
  instagram: { label:'Instagram',         handle:'@...',  url:'#', net:'ig' },
  facebook:  { label:'Facebook Oficial',  handle:'...',   url:'#', net:'fb' },
  tiktok:    { label:'TikTok',            handle:'@...',  url:'#', net:'tt' },
  whatsapp:  { label:'Canal de WhatsApp', handle:'...',   url:'#', net:'wa' }
};

// data/feed.js  (y data/feed.json con el mismo cuerpo)
window.UNEN_FEED = {
  rotationMs: 6000,
  order: ['ig','fb','tt','wa'],           // orden de slides
  pool: {
    ig: [ { tm:'hace 2 d', dur:'0:21', cap:'... <em>tiempo estandar</em> ...', st:['1.2K','84','21'] }, /* x3 */ ],
    fb: [ { tm:'ayer',     cap:'...', st:['640','37','9'] }, /* x3 */ ],
    tt: [ { tm:'hace 2 d', dur:'0:34', cap:'...', st:['4.2K','312','76'] }, /* x3 */ ],
    wa: [ { tm:'ahora',    cap:'...', st:['460 vistas','12 reenvios'] }, /* x3 */ ]
  }
};
```

- `st` para ig/fb/tt = [likes, comentarios, compartidos]; para wa = [vistas, reenvíos].
- Miniaturas/gradientes de marca y glifos: fijos por red (no en datos).

## 9. Manejo de errores y robustez

- `fetch(feed.json)` falla → usa `feed.js`. Sin pantallas rotas.
- Red sin datos → no se genera su slide; el resto sigue.
- URL placeholder → botón inerte, sin error.
- JS deshabilitado → HTML muestra estructura y enlaces base (degradación aceptable).

## 10. Estrategia de pruebas

- **Manual (checklist)**: abrir `index.html` con doble clic y vía servidor local;
  verificar aro, carrusel rotando, dots, hover, clic de cada enlace, responsive
  en ancho ~390px y ~1180px.
- **Paridad visual**: comparar lado a lado contra `mockup.html?v=E&embed=1`.
- **Datos**: validar que `feed.js` y `feed.json` tengan el mismo esquema.
- **Fallback**: renombrar/ocultar `feed.json` y confirmar que sigue funcionando.

## 11. Feed auto-actualizado (fase 2, gratis)

- `.github/workflows/feed.yml`: `schedule: cron` cada N horas.
- Baja feeds vía puente RSS gratuito (p. ej. Rss.app) para las redes que lo
  soporten y escribe `data/feed.json` en el repo.
- **Límite honesto**: IG/TikTok no dan RSS oficial y WhatsApp Channel no tiene
  feed público. Se cubren las redes disponibles; las demás caen a curado.
  Si el plan gratis se agota, el carrusel sigue con `feed.js`.
- Sin Action configurado, el producto funciona igual con contenido curado.

## 12. Supuestos y preguntas abiertas

1. Ubicación del proyecto: **`PILAR/site/`** con git propio (o dentro de
   `entregable/` que ya tiene remoto UNI.git). ← confirmar.
2. URLs/handles reales: el usuario los entregará luego.
3. Se conserva `mockups/` y `entregable/` intactos.
4. Solo se construye la página E (no el presentador A–F).
