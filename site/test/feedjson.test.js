const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const raw = fs.readFileSync(path.join(__dirname, '..', 'data', 'feed.json'), 'utf8');
const json = JSON.parse(raw);

test('feed.json tiene el mismo esquema v2 que UNEN_FEED', () => {
  assert.strictEqual(typeof json.generatedAt, 'string');
  assert.ok(!isNaN(new Date(json.generatedAt).getTime()), 'generatedAt debe ser fecha valida');
  assert.strictEqual(typeof json.rotationMs, 'number');
  assert.deepStrictEqual(json.order, ['tt', 'ig', 'fb']);
  for (const net of json.order) {
    assert.ok(Array.isArray(json.pool[net]), net + ' debe ser array');
    for (const p of json.pool[net]) {
      assert.strictEqual(p.net, net);
      assert.strictEqual(typeof p.cap, 'string');
      assert.strictEqual(typeof p.url, 'string');
      assert.strictEqual(typeof p.tm, 'string');
    }
  }
});
