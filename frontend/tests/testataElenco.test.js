import test from "node:test";
import assert from "node:assert/strict";
import { osservaTestataElenco } from "../src/lib/testataElenco.js";

function scenario(t, posizione = 32) {
  const stato = { posizione, offset: 0, altezza: 122 };
  const intersection = [];
  const resize = [];
  class Observer {
    constructor(callback, opzioni) { this.callback = callback; this.opzioni = opzioni; }
    observe() {}
    disconnect() { this.disconnesso = true; }
  }
  t.mock.method(globalThis, "getComputedStyle", () => ({ top: `${stato.offset}px` }));
  t.mock.method(globalThis, "IntersectionObserver", function (cb, options) {
    const observer = new Observer(cb, options); intersection.push(observer); return observer;
  });
  t.mock.method(globalThis, "ResizeObserver", function (cb) {
    const observer = new Observer(cb); resize.push(observer); return observer;
  });
  const proprieta = new Map();
  const testata = { dataset: {}, style: { setProperty: (k, v) => proprieta.set(k, v) } };
  testata.firstElementChild = { getBoundingClientRect: () => ({ height: testata.dataset.compatta === "true" ? 64 : stato.altezza }) };
  const soglia = { getBoundingClientRect: () => ({ top: stato.posizione }) };
  const chiudi = osservaTestataElenco(soglia, testata);
  return { stato, testata, proprieta, intersection, resize, chiudi };
}

// API browser minime per la prova del lifecycle; nessuna dipendenza DOM aggiunta.
globalThis.getComputedStyle ??= () => ({});
globalThis.IntersectionObserver ??= class {};
globalThis.ResizeObserver ??= class {};

test("aggancio e ritorno conservano lo spazio della testata estesa", (t) => {
  const s = scenario(t);
  assert.equal(s.testata.dataset.compatta, "false");
  s.stato.posizione = -40;
  s.intersection[0].callback();
  s.resize[0].callback();
  assert.equal(s.testata.dataset.compatta, "true");
  assert.equal(s.proprieta.get("--altezza-testata-estesa"), "122px");
  s.stato.posizione = 0;
  s.intersection[0].callback();
  assert.equal(s.testata.dataset.compatta, "false");
  s.chiudi();
});

test("il ripristino di una pagina già scorsa parte compatto", (t) => {
  const s = scenario(t, -200);
  assert.equal(s.testata.dataset.compatta, "true");
  assert.equal(s.proprieta.get("--altezza-testata-estesa"), "122px");
  s.chiudi();
});

test("il cambio desktop/mobile aggiorna soglia e altezza e disconnette il vecchio observer", (t) => {
  const s = scenario(t);
  s.stato.offset = 80;
  s.stato.altezza = 174;
  s.resize[0].callback();
  assert.equal(s.intersection[0].disconnesso, true);
  assert.equal(s.intersection[1].opzioni.rootMargin, "-80px 0px 0px 0px");
  assert.equal(s.testata.dataset.compatta, "true");
  assert.equal(s.proprieta.get("--altezza-testata-estesa"), "174px");
  s.chiudi();
  assert.equal(s.intersection[1].disconnesso, true);
  assert.equal(s.resize[0].disconnesso, true);
});

test("aprire i filtri aggiorna la riserva senza ricreare l'osservatore di scroll", (t) => {
  const s = scenario(t, -100);
  s.stato.altezza = 290;
  s.resize[0].callback();
  assert.equal(s.proprieta.get("--altezza-testata-estesa"), "290px");
  assert.equal(s.intersection.length, 1);
  assert.equal(s.testata.dataset.compatta, "true");
  s.chiudi();
});
