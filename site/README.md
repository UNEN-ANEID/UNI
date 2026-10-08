# UNEN Industrial · página E

Página link-in-bio estática (variante E "Papel + carrusel"). Sin dependencias ni build.
Publicada en: https://unen-aneid.github.io/UNI/site/

## Uso local
- Abrir `index.html` (doble clic) — funciona sin servidor.
- Opcional (para probar `feed.json`): `python -m http.server 8080` y abrir `http://localhost:8080/`.

## Feed real (automático)
- El carrusel muestra publicaciones reales de **TikTok** e **Instagram**.
- Se actualiza **1 vez al día** con GitHub Actions (`.github/workflows/feed.yml`, 06:00 UTC) y también se puede lanzar a mano (`workflow_dispatch`). Corre **en la nube**: no depende de ninguna PC.
- Datos: `data/feed.json` (online) y `data/feed.js` (respaldo para abrir en `file://`).
- Miniaturas: `assets/posts/` (descargadas al repo, porque las URLs de origen caducan).
- Si una red falla ese día, se conserva su última tanda buena (el carrusel nunca se vacía).
- Fuentes: TikTok = urlebird + oEmbed oficial; Instagram = RSS-Bridge público (varias instancias con failover).
- **Facebook**: Facebook exige sesión, así que la nube no puede leerlo (probado: bridge roto en todas las instancias, `mbasic`/`m.facebook` dan 400). Se conserva la última tanda buena. Para forzar el bridge: `--with-fb`.
- WhatsApp queda fuera del carrusel; su botón de enlace se mantiene.

### Facebook desde una hoja de Google (opcional)
Como Facebook no es automatizable gratis en la nube, el Action puede leer de una **hoja publicada** (o cualquier CSV/RSS externo) indicada por la variable de repositorio `FB_FEED_URL`. Si no está puesta, todo funciona igual que ahora (se conserva la última tanda buena).

1. Crea una hoja con encabezados: `Caption`, `Enlace`, `Fecha`, `Imagen` (también valen `cap`, `url`, `fecha`, `imagen`; si no hay encabezado se lee en ese orden).
2. Compártela como *Cualquiera con el enlace: Lector* (o *Archivo → Compartir → Publicar en la web → CSV*).
3. Guarda la URL del CSV como variable del repo:
   `gh variable set FB_FEED_URL --repo UNEN-ANEID/UNI --body "<url>"`
4. El Action la lee en cada corrida. Si la hoja falla o está vacía, se conserva la última tanda buena.
   Fechas admitidas: `aaaa-mm-dd`, `dd/mm/aaaa`, `dd-mm-aaaa` o ISO. `Imagen` es una URL pública (se descarga al repo).

## Ejecutar el feed a mano
```bash
python tools/build_feed.py              # TikTok + Instagram
python tools/build_feed.py --with-fb    # intenta también Facebook
python tools/build_feed.py --only tt,ig # solo algunas redes
python tools/build_feed.py --check      # no escribe nada, imprime el feed
```
Solo requiere `requests` (`pip install requests`). No usa navegador.

## Editar
- Enlaces reales: `data/links.js` (campo `url`).
- Aspecto: `assets/estilo.css` (el bloque final son añadidos; el resto es el CSS original de la variante E).

## Pruebas
`npm test` (usa el test runner de Node, sin instalar nada).
