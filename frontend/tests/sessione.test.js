import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { accedi } from "../src/lib/accesso.js";
import { operazioniAccessoOtp, operazioniContattoOtp } from "../src/lib/otp.js";
import { apiFetch, caricaSessione, messaggioErrore } from "../src/lib/api.js";
import { logout } from "../src/lib/logout.js";
import { haSessione, leggiCsrf, leggiUtenteId, pulisciSessione, salvaSessione } from "../src/lib/sessione.js";
import { conservaDestinazione, destinazioneDopoAccesso, percorsoSicuro } from "../src/lib/ritornoAccesso.js";

const dati = { utente_id: 42, ruolo_codice: "Regionale", csrf_token: "a".repeat(64) };
const richieste = [];
const risposte = [];
const redirect = [];
const deposito = () => {
  const valori = new Map();
  return { getItem: (k) => valori.get(k) ?? null, setItem: (k, v) => valori.set(k, String(v)), removeItem: (k) => valori.delete(k) };
};
const json = (d, status = 200, headers = {}) => new Response(JSON.stringify(d), { status, headers });

beforeEach(() => {
  globalThis.window = {
    localStorage: deposito(), sessionStorage: deposito(),
    location: { origin: "https://ersaf.example", pathname: "/sottoscrittori", search: "?ricerca=rossi", hash: "#righe", replace: (url) => redirect.push(url) },
  };
  richieste.length = risposte.length = redirect.length = 0;
  pulisciSessione();
  globalThis.fetch = async (url, opzioni) => {
    richieste.push({ url, ...opzioni });
    const risposta = risposte.shift();
    if (risposta instanceof Error) throw risposta;
    assert.ok(risposta, "richiesta HTTP inattesa");
    return risposta;
  };
});

test("login usa cookie, restituisce metadati e rimuove le credenziali legacy", async () => {
  window.localStorage.setItem("sessione_token", "vecchio-segreto");
  window.sessionStorage.setItem("token", "vecchio-segreto");
  risposte.push(json(dati));
  assert.equal(await accedi("utente", "password"), true);
  assert.equal(richieste[0].credentials, "include");
  assert.equal(richieste[0].headers["X-ERSAF-Request"], "1");
  assert.equal(richieste[0].headers.Authorization, undefined);
  assert.equal(window.localStorage.getItem("sessione_token"), null);
  assert.equal(window.sessionStorage.getItem("token"), null);
  assert.equal(window.localStorage.getItem("csrf_token"), null);
  assert.equal(leggiUtenteId(), 42);
  assert.equal(leggiCsrf(), dati.csrf_token);
});

for (const [nome, risposta, messaggio] of [
  ["502 HTML", new Response("<html>Bad Gateway</html>", { status: 502 }), /Servizio temporaneamente/],
  ["401 JSON", json({ detail: "Credenziali non valide" }, 401), /Credenziali non valide/],
  ["connessione interrotta", new TypeError("Failed to fetch"), /connessione/i],
  ["risposta 200 incompleta", json({ token: "vecchio-contratto" }), /Risposta del server non valida/],
]) {
  test(`login distingue ${nome}`, async () => {
    risposte.push(risposta);
    await assert.rejects(accedi("utente", "password"), messaggio);
    assert.equal(haSessione(), false);
    assert.equal(redirect.length, 0);
  });
}

test("429 espone Retry-After per il conto alla rovescia", async () => {
  risposte.push(json({}, 429, { "Retry-After": "16" }));
  await assert.rejects(accedi("utente", "password"), (e) => e.stato === 429 && e.attesaSecondi === 16);
});

test("Nazionale resta al passaggio 2FA senza creare una sessione", async () => {
  risposte.push(json({ requires_2fa: true }));
  assert.deepEqual(await accedi("nazionale", "password"), { requires_2fa: true });
  assert.equal(haSessione(), false);
});

test("OTP completa la sessione cookie e non conserva la sfida nello storage", async () => {
  risposte.push(json(dati));
  await operazioniAccessoOtp.verifica({ sfida: "sfida-segreta", codice: "123456" });
  assert.equal(haSessione(), true);
  assert.equal(richieste[0].credentials, "include");
  assert.equal(window.localStorage.getItem("sfida"), null);
  assert.equal(window.sessionStorage.getItem("sfida"), null);
});

test("errore OTP non espelle la sessione e il contatto usa il CSRF comune", async () => {
  salvaSessione(dati);
  risposte.push(json({ detail: "Codice scaduto" }, 400));
  await assert.rejects(operazioniContattoOtp(7, "email", "prova@example.org").verifica({ sfida: "prova", codice: "123456" }), /Codice scaduto/);
  assert.equal(richieste[0].headers["X-CSRF-Token"], dati.csrf_token);
  assert.equal(haSessione(), true);
  assert.equal(redirect.length, 0);
});

test("bootstrap paralleli condividono la richiesta, la scrittura allega il CSRF", async () => {
  risposte.push(json(dati), json({ ok: true }));
  assert.deepEqual(await Promise.all([caricaSessione(), caricaSessione()]), [true, true]);
  await apiFetch("/utenti/", { method: "POST", body: "{}" });
  assert.equal(richieste.length, 2);
  assert.match(richieste[0].url, /\/auth\/session$/);
  assert.equal(richieste[1].headers["X-CSRF-Token"], dati.csrf_token);
  assert.equal(richieste[1].credentials, "include");
});

test("errore di bootstrap non finge una scadenza e consente il nuovo tentativo", async () => {
  risposte.push(new Response("Bad Gateway", { status: 502 }), json(dati));
  await assert.rejects(caricaSessione(), /Servizio temporaneamente/);
  assert.equal(redirect.length, 0);
  assert.equal(await caricaSessione(), true);
});

test("401 salva pagina, query e ancora, spiega la scadenza e consuma il ritorno una volta", async () => {
  salvaSessione(dati);
  risposte.push(json({}, 401));
  await assert.rejects(apiFetch("/clienti"), /Sessione scaduta/);
  assert.equal(haSessione(), false);
  assert.deepEqual(redirect, ["/?sessione=scaduta"]);
  assert.equal(destinazioneDopoAccesso("/dashboard"), "/sottoscrittori?ricerca=rossi#righe");
  assert.equal(destinazioneDopoAccesso("/dashboard"), "/dashboard");
});

test("logout fallito conserva la sessione e segnala l'errore", async () => {
  salvaSessione(dati);
  risposte.push(new TypeError("Failed to fetch"));
  await assert.rejects(logout(), /connessione/i);
  assert.equal(haSessione(), true);
});

test("logout riuscito invia CSRF e pulisce i metadati", async () => {
  salvaSessione(dati);
  risposte.push(new Response(null, { status: 204 }));
  await logout();
  assert.equal(richieste[0].headers["X-CSRF-Token"], dati.csrf_token);
  assert.equal(haSessione(), false);
});

test("ritorno rifiuta URL esterni, pagine pubbliche e caratteri ambigui", () => {
  for (const percorso of ["https://male.example", "//male.example", "/\\male.example", "/\n/male.example", "/", "/password-dimenticata", "/reimposta-password?token=segreto", "/reimposta-password/?token=segreto"]) {
    assert.equal(percorsoSicuro(percorso), null, percorso);
  }
  conservaDestinazione();
  window.sessionStorage.setItem("ritorno_accesso", "//male.example");
  assert.equal(destinazioneDopoAccesso("/dashboard"), "/dashboard");
});

test("422 mantiene i dettagli dei campi nelle altre pagine", async () => {
  const risposta = json({ detail: [{ loc: ["body", "email"], msg: "Campo richiesto" }] }, 422);
  assert.equal(await messaggioErrore(risposta), "email: Campo richiesto");
});
