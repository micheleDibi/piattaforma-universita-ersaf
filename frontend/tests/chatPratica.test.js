import { setImmediate } from "node:timers";
import test from "node:test";
import assert from "node:assert/strict";
import { ConversazionePratica, unisciMessaggi } from "../src/lib/conversazionePratica.js";

const tick = () => new Promise(resolve => setImmediate(resolve));
const pagina = (ids, cursore = null) => ({ elementi: ids.map(id => ({ id, testo: id })), altri: !!cursore, cursore });
function fixture(overrides = {}) {
  const sent = [];
  const ws = { readyState: 1, send: frame => sent.push(JSON.parse(frame)), close: () => {} };
  const api = { leggi: async () => pagina(["2", "1"]), socket: async () => ws,
    prepara: async (_id, _testo, clientMessageId) => ({ clientMessageId, cifrato: "u2.cifrato-identico" }), ...overrides };
  const chat = new ConversazionePratica("101", api);
  const evento = data => ws.onmessage({ data: JSON.stringify(data) });
  return { chat, ws, sent, evento };
}

test("ordine e deduplica preservano ID superiori al massimo intero JS", () => {
  assert.deepEqual(unisciMessaggi([{ id: "9007199254740993" }], [{ id: "9007199254740992" }, { id: "9007199254740993" }]).map(m => m.id),
    ["9007199254740992", "9007199254740993"]);
});

test("retry conserva ID e ciphertext, e la conferma rimuove il pendente", async t => {
  const f = fixture(); t.after(() => f.chat.stop());
  f.chat.start(); await tick(); f.evento({ tipo: "connesso" }); await tick();
  assert.equal(await f.chat.invia("Ciao"), true);
  assert.equal(await f.chat.invia("Doppio click"), false);
  f.chat.riprovaInvio();
  assert.deepEqual(f.sent[1], f.sent[0]);
  f.evento({ tipo: "messaggio", id: "2", clientMessageId: f.sent[0].clientMessageId, consegna: "consegna-2" });
  await tick();
  assert.equal(f.chat.snapshot().invio, null);
  assert.deepEqual(f.sent.at(-1), { tipo: "conferma", consegna: "consegna-2" });
});

test("errore in preparazione mantiene recuperabile la bozza e non invia", async t => {
  const f = fixture({ prepara: async () => { throw new Error("Connessione interrotta"); } });
  t.after(() => f.chat.stop()); f.chat.start(); await tick(); f.evento({ tipo: "connesso" });
  await assert.rejects(f.chat.invia("La bozza"), /Connessione interrotta/);
  assert.equal(f.chat.snapshot().invio, null); assert.equal(f.sent.length, 0);
});

test("il recupero dopo disconnessione riempie il salto tra pagine", async t => {
  let recente = false;
  const f = fixture({ leggi: async (_id, cursor) => !recente ? pagina(["2", "1"]) : cursor ? pagina(["4", "3", "2"], "older") : pagina(["6", "5"], "next") });
  t.after(() => f.chat.stop()); f.chat.start(); await tick();
  recente = true; await f.chat.aggiorna();
  assert.deepEqual(f.chat.snapshot().elementi.map(m => m.id), ["1", "2", "3", "4", "5", "6"]);
});

test("cleanup e doppio avvio React non lasciano la chat bloccata", async t => {
  const resolves = [];
  const f = fixture({ leggi: () => new Promise(resolve => resolves.push(resolve)) });
  t.after(() => f.chat.stop());
  f.chat.start(); f.chat.stop(); f.chat.start();
  resolves[0](pagina(["99"])); await tick();
  resolves[1](pagina(["2"])); await tick();
  assert.equal(f.chat.snapshot().caricamento, false);
  assert.deepEqual(f.chat.snapshot().elementi.map(m => m.id), ["2"]);
  assert.equal(typeof f.ws.onmessage, "function");
});

test("ricifra solo dopo il rifiuto definitivo per chiave scaduta", async t => {
  let preparazioni = 0;
  const f = fixture({ prepara: async (_id, _testo, clientMessageId) => ({ clientMessageId, cifrato: `u2.prova-${++preparazioni}` }) });
  t.after(() => f.chat.stop()); f.chat.start(); await tick(); f.evento({ tipo: "connesso" }); await tick();
  await f.chat.invia("A cavallo dell'ora");
  const id = f.sent[0].clientMessageId;
  f.evento({ tipo: "errore", clientMessageId: id, messaggio: "Riprova", ricifra: false });
  await f.chat.riprovaInvio();
  assert.equal(preparazioni, 1);
  assert.deepEqual(f.sent[0], f.sent[1]);
  f.evento({ tipo: "errore", clientMessageId: id, messaggio: "Chiave scaduta", ricifra: true });
  await f.chat.riprovaInvio();
  assert.equal(preparazioni, 2);
  assert.equal(f.sent[2].clientMessageId, id);
  assert.notEqual(f.sent[2].cifrato, f.sent[1].cifrato);
});

test("la presenza usa ID utente, sostituisce il quadro precedente e scarta frame malformati", async t => {
  const f = fixture({ leggi: async () => ({ ...pagina(["1"]), elementi: [{ id: "1", autoreId: "4845", mio: false }] }) });
  t.after(() => f.chat.stop()); f.chat.start(); await tick();
  f.evento({ tipo: "connesso" }); await tick();
  assert.deepEqual(f.chat.snapshot().online, []);
  f.evento({ tipo: "presenza", utenti: ["4845", "4845", "3956", 4846, "0", "", "Elena"] });
  assert.deepEqual(f.chat.snapshot().online, ["4845", "3956"]);
  assert.ok(f.chat.snapshot().online.includes(f.chat.snapshot().elementi[0].autoreId));
  f.evento({ tipo: "presenza", utenti: null });
  assert.deepEqual(f.chat.snapshot().online, ["4845", "3956"]);
  f.evento({ tipo: "presenza", utenti: [] });
  assert.deepEqual(f.chat.snapshot().online, []);
});

test("disconnessione e chiusura rimuovono la presenza, e i vecchi socket non la ripristinano", async t => {
  const f = fixture(); t.after(() => f.chat.stop());
  f.chat.start(); await tick(); f.evento({ tipo: "connesso" });
  f.evento({ tipo: "presenza", utenti: ["4845"] });
  f.ws.onclose();
  assert.deepEqual(f.chat.snapshot().online, []);
  f.evento({ tipo: "presenza", utenti: ["4845"] });
  assert.deepEqual(f.chat.snapshot().online, []);
  f.chat.stop();
  f.evento({ tipo: "presenza", utenti: ["4845"] });
  assert.deepEqual(f.chat.snapshot().online, []);
  f.chat.start(); await tick();
  assert.deepEqual(f.chat.snapshot().online, []);
});
