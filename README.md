# UNEN Industrial · página E

Página link-in-bio estática (variante E "Papel + carrusel"). Sin dependencias ni build.
Publicada en: https://unen-aneid.github.io/UNI/site/

## Uso local
- Abrir `index.html` (doble clic) — funciona sin servidor.
- Opcional (para probar `feed.json`): `python -m http.server 8080` y abrir `http://localhost:8080/`.

## Feed real (automático)
- El carrusel muestra publicaciones reales de **TikTok, Instagram y Facebook**.
- Se actualiza **1 vez al día** con GitHub Actions (`.github/workflows/feed.yml`, 06:00 UTC) y también se puede lanzar a mano (`workflow_dispatch`).
- Datos: `data/feed.json` (online) y `data/feed.js` (respaldo para abrir en `file://`).
- Miniaturas: `assets/posts/` (descargadas al repo, porque las URLs de origen caducan).
- Si una red falla ese día, se conserva su última tanda buena (el carrusel nunca se vacía).
- Ejecutar a mano: `python tools/build_feed.py` (opciones: `--check` no escribe, `--only tt,ig,fb`).
- WhatsApp queda fuera del carrusel; su botón de enlace se mantiene.

## Editar
- Enlaces reales: `data/links.js` (campo `url`).
- Aspecto: `assets/estilo.css` (el bloque final son añadidos; el resto es el CSS original de la variante E).

## Pruebas
`npm test` (usa el test runner de Node, sin instalar nada).
