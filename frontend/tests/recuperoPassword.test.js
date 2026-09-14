import { afterEach, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { confermaReset, richiediRecupero, verificaLinkReset } from "../src/lib/recuperoPassword.js";
import { TESTI_RESET } from "../src/config/testi/accesso.js";

const fetchOriginale = globalThis.fetch;
const richieste = [];
let risposta;
const json = (dati, status = 200) => new Response(JSON.stringify(dati), { status });

beforeEach(() => {
  richieste.length = 0;
  globalThis.fetch = async (url, opzioni) => {
    richieste.push({ url, ...opzioni });
    if (risposta instanceof Error) throw risposta;
    return risposta;
  };
});
afterEach(() => { globalThis.fetch = fetchOriginale; });

for (const [nome, creaRisposta] of [
  ["account noto o sconosciuto", () => json({})],
  ["servizio indisponibile", () => new Response("Bad Gateway", { status: 502 })],
  ["nessuna connessione", () => new TypeError("Failed to fetch")],
]) test(`recupero: esito indistinguibile per ${nome}`, async () => {
  risposta = creaRisposta();
  assert.equal(await richiediRecupero("persona@example.org"), undefined);
  assert.deepEqual(JSON.parse(richieste[0].body), { email: "persona@example.org" });
  assert.match(richieste[0].url, /\/auth\/password-reset\/request$/);
  assert.equal(richieste[0].credentials, "include");
  assert.equal(richieste[0].headers["X-ERSAF-Request"], "1");
});

test("verifica: codifica il token e distingue link valido, scaduto e gia usato", async () => {
  risposta = json({ valido: true });
  assert.deepEqual(await verificaLinkReset("a+b/c="), { stato: "valido" });
  assert.match(richieste[0].url, /token=a%2Bb%2Fc%3D$/);
  for (const motivo of ["scaduto", "gia_usato", "non_valido"]) {
    risposta = json({ valido: false, motivo });
    assert.deepEqual(await verificaLinkReset("token-sintetico"), { stato: "non_valido", motivo });
  }
});

test("verifica: una risposta non JSON non rende mai disponibile il modulo", async () => {
  risposta = new Response("Bad Gateway", { status: 502 });
  assert.deepEqual(await verificaLinkReset("token-sintetico"), { stato: "non_valido", motivo: "non_valido" });
  risposta = new TypeError("Failed to fetch");
  assert.deepEqual(await verificaLinkReset("token-sintetico"), { stato: "non_valido", motivo: "rete" });
});

const conferma = { token: "token-sintetico", password: "Nuova-frase-2026", conferma: "Nuova-frase-2026" };
test("conferma: conserva il contratto e riconosce il salvataggio senza leggere metadati di sessione", async () => {
  risposta = new Response(null, { status: 204 });
  assert.deepEqual(await confermaReset(conferma), { ok: true });
  assert.deepEqual(JSON.parse(richieste[0].body), {
    token: conferma.token, password: conferma.password, password_conferma: conferma.conferma,
  });
});

test("conferma: collega il rifiuto del server alla regola pertinente", async () => {
  risposta = json({ detail: { regole_violate: ["uguale_username"], messaggi: ["Scegli una password diversa dal nome utente."] } }, 422);
  assert.deepEqual(await confermaReset(conferma), {
    ok: false, regoleRifiutate: ["identificativo"], errore: "Scegli una password diversa dal nome utente.",
  });
});

test("conferma: errore HTTP pubblico e rete non causano un redirect di sessione", async () => {
  risposta = json({ detail: "Link già usato." }, 401);
  assert.equal((await confermaReset(conferma)).errore, "Link già usato.");
  risposta = new Response("Bad Gateway", { status: 502 });
  assert.equal((await confermaReset(conferma)).errore, TESTI_RESET.errore);
  risposta = new TypeError("Failed to fetch");
  assert.equal((await confermaReset(conferma)).errore, TESTI_RESET.rete);
});
