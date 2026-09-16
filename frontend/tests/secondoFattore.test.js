import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { cambiaMetodo, metodiAlternativi, operazioniPerMetodo } from "../src/lib/secondoFattore.js";
import { operazioniAccessoOtp } from "../src/lib/otp.js";
import { attivaAuthenticator, caricaStatoMfa, dataAttivazione, disattivaAuthenticator } from "../src/lib/sicurezza.js";
import { haSessione, leggiUtenteId, pulisciSessione, salvaSessione } from "../src/lib/sessione.js";

const dati = { utente_id: 42, ruolo_codice: "Nazionale", csrf_token: "a".repeat(64) };
const richieste = [];
const risposte = [];
const deposito = () => {
  const valori = new Map();
  return { getItem: (k) => valori.get(k) ?? null, setItem: (k, v) => valori.set(k, String(v)), removeItem: (k) => valori.delete(k) };
};
const json = (d, status = 200, headers = {}) => new Response(JSON.stringify(d), { status, headers });

beforeEach(() => {
  globalThis.window = {
    localStorage: deposito(), sessionStorage: deposito(),
    location: { origin: "https://ersaf.example", pathname: "/", search: "", hash: "", replace: () => {} },
  };
  richieste.length = risposte.length = 0;
  pulisciSessione();
  globalThis.fetch = async (url, opzioni) => {
    richieste.push({ url, ...opzioni });
    const risposta = risposte.shift();
    if (risposta instanceof Error) throw risposta;
    assert.ok(risposta, "richiesta HTTP inattesa");
    return risposta;
  };
});

test("il codice dell'app completa la sessione senza CSRF e senza reinvio", async () => {
  const operazioni = operazioniPerMetodo("totp");
  assert.equal(operazioni.invia, null, "l'app non reinvia nulla");
  risposte.push(json(dati));
  await operazioni.verifica({ sfida: "s".repeat(43), codice: "123456" });
  assert.ok(richieste[0].url.endsWith("/auth/mfa/verifica-totp"));
  assert.equal(richieste[0].method, "POST");
  assert.equal(richieste[0].headers["X-CSRF-Token"], undefined, "prima della sessione non c'e' CSRF");
  assert.equal(haSessione(), true);
  assert.equal(leggiUtenteId(), 42);
});

test("per l'email valgono le operazioni OTP esistenti", () => {
  assert.equal(operazioniPerMetodo("email"), operazioniAccessoOtp);
  assert.equal(operazioniPerMetodo("email_accesso"), operazioniAccessoOtp);
});

test("usa un altro metodo chiede al server la nuova sfida", async () => {
  const sfida = { sfida: "s".repeat(43), metodo: "totp", metodi: ["totp", "email"] };
  assert.deepEqual(metodiAlternativi(sfida), ["email"]);
  assert.deepEqual(metodiAlternativi({ sfida: "x", metodo: "email_accesso", metodi: [] }), []);
  risposte.push(json({ requires_2fa: true, metodo: "email", metodi: ["totp", "email"], sfida: "n".repeat(43), destinatario: "m•••@ersaf.it" }));
  const nuova = await cambiaMetodo(sfida, "email");
  assert.ok(richieste[0].url.endsWith("/auth/mfa/metodo"));
  assert.deepEqual(JSON.parse(richieste[0].body), { sfida: sfida.sfida, metodo: "email" });
  assert.equal(nuova.metodo, "email");
  assert.equal(haSessione(), false, "cambiare metodo non autentica");
});

test("la gestione dal profilo passa dalla sessione con il CSRF", async () => {
  salvaSessione(dati);
  risposte.push(json({ metodi: ["email"], proposto: "email", email: { verificata: true, destinatario: "m•••@ersaf.it" }, totp: { attivo: false, pendente: false, attivato_il: null }, passkey: [] }));
  const stato = await caricaStatoMfa();
  assert.equal(stato.proposto, "email");
  assert.ok(richieste[0].url.endsWith("/auth/mfa"));

  risposte.push(json({ uri: "otpauth://totp/x", segreto: "ABCDEF", qr_svg: "<svg/>" }));
  const avvio = await attivaAuthenticator("password-lunga");
  assert.equal(avvio.segreto, "ABCDEF");
  assert.equal(richieste[1].method, "POST");
  assert.equal(richieste[1].headers["X-CSRF-Token"], dati.csrf_token);
  assert.deepEqual(JSON.parse(richieste[1].body), { password: "password-lunga" });

  risposte.push(json({ detail: "Codice non valido: controlla l'ora del telefono e riprova." }, 400));
  await assert.rejects(disattivaAuthenticator("password-lunga", "000000"), /ora del telefono/);
});

test("un limite sui tentativi espone l'attesa", async () => {
  salvaSessione(dati);
  risposte.push(json({ detail: "Troppi tentativi" }, 429, { "Retry-After": "30" }));
  await assert.rejects(attivaAuthenticator("x"), (errore) => errore.attesaSecondi === 30);
});

test("la data di attivazione e' leggibile o vuota", () => {
  assert.equal(dataAttivazione(null), "");
  assert.equal(dataAttivazione("non-una-data"), "");
  assert.match(dataAttivazione("2026-09-16T10:00:00"), /2026/);
});
