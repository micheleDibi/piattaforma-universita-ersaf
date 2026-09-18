import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { documentoDisponibile, nomeDaIntestazione, scaricaDocumento } from "../src/lib/documentoPratica.js";
import { pulisciSessione } from "../src/lib/sessione.js";

const richieste = [];
const risposte = [];
const deposito = () => {
  const valori = new Map();
  return { getItem: (k) => valori.get(k) ?? null, setItem: (k, v) => valori.set(k, String(v)), removeItem: (k) => valori.delete(k) };
};

beforeEach(() => {
  globalThis.window = { localStorage: deposito(), sessionStorage: deposito(),
    location: { origin: "https://ersaf.example", pathname: "/pratiche/7", search: "", hash: "", replace: () => {} } };
  richieste.length = risposte.length = 0;
  pulisciSessione();
  globalThis.fetch = async (url, opzioni) => { richieste.push({ url, ...opzioni }); const r = risposte.shift(); assert.ok(r, "richiesta inattesa"); return r; };
});

function ambienteFinto() {
  const eventi = [];
  const timer = [];
  return {
    eventi, timer,
    URL: { createObjectURL: (blob) => { eventi.push(["crea", blob.size]); return "blob:ersaf/1"; }, revokeObjectURL: (url) => eventi.push(["revoca", url]) },
    document: {
      body: { append: (el) => eventi.push(["aggiungi", el.download]) },
      createElement: () => ({ click() { eventi.push(["click", this.href, this.download]); }, remove() { eventi.push(["rimuovi"]); } }),
    },
    setTimeout: (fn, ms) => timer.push({ fn, ms }),
  };
}

test("la disponibilita' arriva dal server e senza modulo il pulsante resta nascosto", async () => {
  risposte.push(new Response(JSON.stringify({ disponibile: true, nome_file: "pratica-000045.pdf" }), { status: 200 }));
  assert.deepEqual(await documentoDisponibile(7), { disponibile: true, nomeFile: "pratica-000045.pdf" });
  assert.ok(richieste[0].url.endsWith("/pratiche/7/documento/disponibile"));
  risposte.push(new Response(JSON.stringify({ disponibile: false, nome_file: null }), { status: 200 }));
  assert.deepEqual(await documentoDisponibile(8), { disponibile: false, nomeFile: null });
});

test("il PDF si salva con il nome indicato dal server e l'URL del blob si libera dopo", async () => {
  risposte.push(new Response(new Blob(["%PDF-1.7 prova"], { type: "application/pdf" }), {
    status: 200, headers: { "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="pratica-000045.pdf"' },
  }));
  const ambiente = ambienteFinto();
  assert.equal(await scaricaDocumento(7, ambiente), "pratica-000045.pdf");
  assert.ok(richieste[0].url.endsWith("/pratiche/7/documento"));
  assert.deepEqual(ambiente.eventi.map((e) => e[0]), ["crea", "aggiungi", "click", "rimuovi"]);
  assert.deepEqual(ambiente.eventi[2], ["click", "blob:ersaf/1", "pratica-000045.pdf"]);
  assert.equal(ambiente.timer.length, 1);
  ambiente.timer[0].fn();
  assert.deepEqual(ambiente.eventi.at(-1), ["revoca", "blob:ersaf/1"]);
});

test("un errore del server arriva come messaggio leggibile, senza download", async () => {
  risposte.push(new Response(JSON.stringify({ detail: "Per questo tipo di pratica il documento non è ancora disponibile." }),
    { status: 404, headers: { "Content-Type": "application/json" } }));
  const ambiente = ambienteFinto();
  await assert.rejects(scaricaDocumento(9, ambiente), /non è ancora disponibile/);
  assert.equal(ambiente.eventi.length, 0);
});

test("il nome del file si legge nelle due forme di Content-Disposition", () => {
  assert.equal(nomeDaIntestazione('attachment; filename="pratica-1.pdf"', "x.pdf"), "pratica-1.pdf");
  assert.equal(nomeDaIntestazione("attachment; filename*=UTF-8''pratica%20ecampus.pdf; filename=\"p.pdf\"", "x.pdf"), "pratica ecampus.pdf");
  assert.equal(nomeDaIntestazione("attachment", "pratica-9.pdf"), "pratica-9.pdf");
  assert.equal(nomeDaIntestazione(null, "pratica-9.pdf"), "pratica-9.pdf");
});
