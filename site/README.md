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
