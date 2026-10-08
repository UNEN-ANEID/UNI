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

test('safeCaption conserva <em> y escapa el resto', () => {
  assert.strictEqual(Render.safeCaption('<em>x</em>'), '<em>x</em>');
  const evil = Render.safeCaption('<img src=x onerror=alert(1)>');
  assert.doesNotMatch(evil, /<img/);
  assert.match(evil, /^&lt;img /);
});

test('thumbHTML produce <img> solo si hay miniatura', () => {
  assert.strictEqual(Render.thumbHTML({}), '');
  assert.strictEqual(Render.thumbHTML(null), '');
  const html = Render.thumbHTML({ img: 'assets/posts/tt_1.jpg' });
  assert.match(html, /<img class="thumb" src="assets\/posts\/tt_1\.jpg"/);
  assert.match(html, /loading="lazy"/);
});

test('slideLinkHTML produce overlay solo si hay url', () => {
  assert.strictEqual(Render.slideLinkHTML({}), '');
  const html = Render.slideLinkHTML({ url: 'https://x/1', cap: 'hola' });
  assert.match(html, /class="open" href="https:\/\/x\/1"/);
  assert.match(html, /target="_blank"/);
  assert.match(html, /rel="noopener"/);
  assert.match(html, /aria-label="hola"/);
});
