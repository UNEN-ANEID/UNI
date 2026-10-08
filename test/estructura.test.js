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

test('existen 5 <a class="lk2"> estaticos (degradacion sin JS)', () => {
  const anchors = html.match(/class="lk2"/g) || [];
  assert.strictEqual(anchors.length, 5);
  const after = html.slice(html.indexOf('class="lklist"'));
  const block = after.slice(0, after.indexOf('<svg width="0"'));
  assert.strictEqual((block.match(/<a class="lk2"/g) || []).length, 5);
});

test('hay 3 slides con data-net tt/ig/fb, 3 dots y 6 simbolos', () => {
  const nets = ['tt', 'ig', 'fb'];
  for (const n of nets) assert.match(html, new RegExp('data-net="' + n + '"'));
  assert.doesNotMatch(html, /data-net="wa"/);
  const slides = html.match(/class="sl"/g) || [];
  assert.strictEqual(slides.length, 3);
  const dotsWrap = html.match(/<div class="dots">([\s\S]*?)<\/div>/);
  assert.ok(dotsWrap, 'falta el contenedor .dots');
  assert.strictEqual((dotsWrap[1].match(/<i/g) || []).length, 3, 'deben ser 3 .dots i');
  assert.strictEqual((html.match(/<symbol/g) || []).length, 6, 'deben ser 6 <symbol>');
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

test('la pagina tiene diseno responsivo centrado', () => {
  assert.match(css, /max-width:\s*480px/);
});

test('respeta prefers-reduced-motion', () => {
  assert.match(css, /prefers-reduced-motion/);
});
