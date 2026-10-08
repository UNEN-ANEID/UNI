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

test('activeNets solo deja las redes con publicaciones', () => {
  assert.deepStrictEqual(C.activeNets(['ig', 'fb'], { ig: [{ tm: 'x' }], fb: [] }), ['ig']);
  assert.deepStrictEqual(C.activeNets(['ig', 'fb'], {}), []);
  assert.deepStrictEqual(C.activeNets([], { ig: [{ tm: 'x' }] }), []);
});

test('wrap normaliza indices (incluidos negativos)', () => {
  assert.strictEqual(C.wrap(0, 4), 0);
  assert.strictEqual(C.wrap(4, 4), 0);
  assert.strictEqual(C.wrap(-1, 4), 3);
  assert.strictEqual(C.wrap(3, 0), 0);
});
