import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { b64url, messaggioErrorePasskey, opzioniCreazione, opzioniRichiesta, passkeySupportate, serializza } from "../src/lib/passkey.js";
import { verificaPasskey } from "../src/lib/secondoFattore.js";
import { haSessione, pulisciSessione } from "../src/lib/sessione.js";

const richieste = [];
const risposte = [];
const deposito = () => {
  const valori = new Map();
  return { getItem: (k) => valori.get(k) ?? null, setItem: (k, v) => valori.set(k, String(v)), removeItem: (k) => valori.delete(k) };
};
const json = (d, status = 200) => new Response(JSON.stringify(d), { status });

beforeEach(() => {
  // Un browser senza gli aiuti recenti: le conversioni le fa il nostro codice.
  globalThis.window = { localStorage: deposito(), sessionStorage: deposito(), location: { origin: "https://ersaf.example", pathname: "/", search: "", hash: "", replace: () => {} } };
  richieste.length = risposte.length = 0;
  pulisciSessione();
  globalThis.fetch = async (url, opzioni) => { richieste.push({ url, ...opzioni }); const r = risposte.shift(); assert.ok(r, "richiesta inattesa"); return r; };
});

test("base64url va e torna senza riempimento", () => {
  const byte = new Uint8Array([0, 1, 2, 250, 251, 252, 253, 254, 255]);
  const testo = b64url.a(byte);
  assert.ok(!testo.includes("=") && !testo.includes("+") && !testo.includes("/"));
  assert.deepEqual([...b64url.da(testo)], [...byte]);
});

test("senza PublicKeyCredential il browser non supporta le passkey", () => {
  assert.equal(passkeySupportate(), false);
});

test("le opzioni del server diventano ArrayBuffer per il browser", () => {
  const creazione = opzioniCreazione({ challenge: b64url.a(new Uint8Array([9, 8, 7])), rp: { id: "ersaf.example" }, hints: ["hybrid"],
    user: { id: b64url.a(new Uint8Array([1, 2])), name: "collaudo.prova" }, excludeCredentials: [{ id: b64url.a(new Uint8Array([5])), type: "public-key" }] });
  assert.deepEqual([...creazione.challenge], [9, 8, 7]);
  assert.deepEqual(creazione.hints, ["hybrid"]);  // i suggerimenti passano intatti al browser
  assert.deepEqual([...creazione.user.id], [1, 2]);
  assert.deepEqual([...creazione.excludeCredentials[0].id], [5]);
  const richiesta = opzioniRichiesta({ challenge: b64url.a(new Uint8Array([3])), rpId: "ersaf.example", allowCredentials: [] });
  assert.deepEqual([...richiesta.challenge], [3]);
  assert.deepEqual(richiesta.allowCredentials, []);
});

test("la credenziale del browser si serializza nel JSON che il server aspetta", () => {
  const raw = new Uint8Array([10, 11]).buffer;
  const risposta = {
    clientDataJSON: new Uint8Array([1]).buffer, authenticatorData: new Uint8Array([2]).buffer,
    signature: new Uint8Array([3]).buffer, userHandle: null,
  };
  const serializzata = serializza({ id: "CgsL", rawId: raw, type: "public-key", authenticatorAttachment: "cross-platform", response: risposta, getClientExtensionResults: () => ({}) });
  assert.equal(serializzata.rawId, b64url.a(raw));
  assert.equal(serializzata.response.signature, b64url.a(risposta.signature));
  assert.equal(serializzata.response.userHandle, undefined);
  assert.equal(serializzata.response.attestationObject, undefined);
});

test("gli errori del browser diventano frasi per l'utente", () => {
  assert.match(messaggioErrorePasskey({ name: "NotAllowedError" }), /annullata/i);
  assert.match(messaggioErrorePasskey({ name: "SecurityError" }), /sito/i);
  assert.match(messaggioErrorePasskey({ name: "InvalidStateError" }), /già registrata/i);
  assert.equal(messaggioErrorePasskey(new Error("boom")), "boom");
});

test("la risposta del telefono completa la sessione", async () => {
  risposte.push(json({ utente_id: 7, ruolo_codice: "Nazionale", csrf_token: "b".repeat(64) }));
  await verificaPasskey({ sfida: "s".repeat(43), metodo: "passkey" }, { id: "x", rawId: "x", type: "public-key", response: {} });
  assert.ok(richieste[0].url.endsWith("/auth/mfa/verifica-passkey"));
  assert.deepEqual(Object.keys(JSON.parse(richieste[0].body)), ["sfida", "credenziale"]);
  assert.equal(haSessione(), true);
});
