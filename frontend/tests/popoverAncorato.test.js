import test from "node:test";
import assert from "node:assert/strict";
import { posizionePopover } from "../src/lib/popoverAncorato.js";

const desktop = { left: 0, top: 0, width: 1440, height: 900 };
const pannello = { width: 320, height: 396 };

test("il popup si allinea al bordo destro del comando senza spostare l'elenco", () => {
  const p = posizionePopover({ top: 32, bottom: 76, right: 1200 }, pannello, desktop, 16);
  assert.equal(p.left, 880);
  assert.equal(p.top, 92);
  assert.ok(p.maxHeight >= pannello.height);
});

test("su mobile rispetta entrambi i margini anche con il comando vicino al bordo", () => {
  const p = posizionePopover({ top: 160, bottom: 204, right: 284 },
    { width: 288, height: 396 }, { left: 0, top: 0, width: 320, height: 700 }, 16);
  assert.equal(p.left, 16);
  assert.ok(p.left + 288 <= 304);
  assert.equal(p.top, 220);
});

test("vicino al fondo apre sopra il comando e conserva spazio per il pannello", () => {
  const p = posizionePopover({ top: 810, bottom: 854, right: 1438 }, pannello, desktop, 16);
  assert.equal(p.left, 1104);
  assert.equal(p.top, 398);
  assert.equal(p.top + pannello.height, 794);
});

test("un viewport corto limita l'altezza e lascia il contenuto scorrere nel popup", () => {
  const p = posizionePopover({ top: 90, bottom: 134, right: 350 }, pannello,
    { left: 0, top: 0, width: 390, height: 360 }, 16);
  assert.equal(p.top, 150);
  assert.equal(p.maxHeight, 194);
  assert.equal(p.top + p.maxHeight, 344);
});

test("offset del viewport visibile: il popup resta raggiungibile con zoom o tastiera", () => {
  const viewport = { left: 50, top: 100, width: 390, height: 400 };
  const p = posizionePopover({ top: 180, bottom: 224, right: 425 }, pannello, viewport, 16);
  assert.ok(p.left >= 66 && p.left + pannello.width <= 424);
  assert.ok(p.top >= 116 && p.top + Math.min(pannello.height, p.maxHeight) <= 484);
});
