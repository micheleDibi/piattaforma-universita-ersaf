import { test } from "node:test";
import assert from "node:assert/strict";
import { avviaEsclusivo, rilasciaVideo, svuotaVideo } from "../src/lib/videoEsclusivo.js";

const video = () => ({ paused: false, pause() { this.paused = true; this.pause_chiamate = (this.pause_chiamate ?? 0) + 1; } });

test("avviare un secondo video mette in pausa il primo", () => {
  const primo = video();
  const secondo = video();
  avviaEsclusivo(primo);
  avviaEsclusivo(secondo);
  assert.equal(primo.paused, true);
  assert.equal(primo.pause_chiamate, 1);
  assert.equal(secondo.paused, false);
  rilasciaVideo(secondo);
});

test("lo stesso video non si mette in pausa da solo", () => {
  const primo = video();
  avviaEsclusivo(primo);
  avviaEsclusivo(primo);
  assert.equal(primo.pause_chiamate, undefined);
  rilasciaVideo(primo);
});

test("rilasciaVideo libera il registro", () => {
  const primo = video();
  const secondo = video();
  avviaEsclusivo(primo);
  rilasciaVideo(primo);
  avviaEsclusivo(secondo);
  assert.equal(primo.pause_chiamate, undefined);
  // Rilasciare un video che non e' quello corrente non cambia nulla.
  rilasciaVideo(primo);
  const terzo = video();
  avviaEsclusivo(terzo);
  assert.equal(secondo.pause_chiamate, 1);
  rilasciaVideo(terzo);
});

test("svuotaVideo ferma lo scaricamento: pausa, sorgenti tolte, src tolto, poi load()", () => {
  const passi = [];
  const sorgente = (tipo) => ({ remove() { passi.push(`remove ${tipo}`); } });
  const player = {
    pause() { passi.push("pause"); },
    querySelectorAll(selettore) {
      passi.push(`querySelectorAll ${selettore}`);
      return [sorgente("mp4"), sorgente("webm")];
    },
    removeAttribute(nome) { passi.push(`removeAttribute ${nome}`); },
    load() { passi.push("load"); },
  };
  svuotaVideo(player);
  // load() viene per ultimo: con le sorgenti ancora al loro posto ripartirebbe
  // la selezione della risorsa, cioe' un nuovo scaricamento.
  assert.deepEqual(passi, [
    "pause", "querySelectorAll source", "remove mp4", "remove webm", "removeAttribute src", "load",
  ]);
});

test("un video gia' in pausa non riceve pause()", () => {
  const primo = video();
  const secondo = video();
  avviaEsclusivo(primo);
  primo.paused = true;
  avviaEsclusivo(secondo);
  assert.equal(primo.pause_chiamate, undefined);
  rilasciaVideo(secondo);
});
