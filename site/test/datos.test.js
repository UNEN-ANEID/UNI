const test = require('node:test');
const assert = require('node:assert');
require('../data/links.js');
require('../data/feed.js');

const LINKS = globalThis.UNEN_LINKS;
const FEED = globalThis.UNEN_FEED;

test('UNEN_LINKS tiene las redes con net y url', () => {
  for (const key of ['whatsappDirecto', 'instagram', 'facebook', 'tiktok', 'whatsapp']) {
    assert.ok(LINKS[key], 'falta ' + key);
    assert.ok(['ig', 'fb', 'tt', 'wa'].includes(LINKS[key].net));
    assert.strictEqual(typeof LINKS[key].url, 'string');
    assert.strictEqual(typeof LINKS[key].label, 'string');
    assert.strictEqual(typeof LINKS[key].handle, 'string');
  }
});

test('UNEN_FEED v2: generatedAt, order tt/ig/fb y posts con net/cap/url/tm', () => {
  assert.strictEqual(typeof FEED.generatedAt, 'string');
  assert.ok(!isNaN(new Date(FEED.generatedAt).getTime()), 'generatedAt debe ser fecha valida');
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
