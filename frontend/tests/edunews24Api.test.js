import { beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { API_BASE_URL } from "../src/lib/api.js";
import {
  azzeraEsitoFunzione,
  caricaCategorieEduNews24,
  caricaElencoEduNews24,
  leggiEsitoFunzione,
  osservaEsitoFunzione,
} from "../src/lib/edunews24Api.js";
import { TESTI_EDUNEWS24 as testi } from "../src/config/testi/edunews24.js";

const richieste = [];
const risposte = [];
const redirect = [];
const deposito = () => {
  const valori = new Map();
  return { getItem: (k) => valori.get(k) ?? null, setItem: (k, v) => valori.set(k, String(v)), removeItem: (k) => valori.delete(k) };
};
const json = (dati, status = 200, headers = {}) => new Response(JSON.stringify(dati), { status, headers });
const notizia = (id) => ({
  tipo: "notizia", id, titolo: `Titolo ${id}`, titolo_breve: null, sintesi: null, url: `https://edunews24.invalid/articoli/${id}`,
  pubblicato_il: "2026-09-28T08:00:00+02:00", categoria: { slug: "scuola", nome: "Scuola" }, immagine: null, video: null, ha_video: false,
});
const elenco = (ids, meta = { cursore_successivo: null, aggiornato_il: "2026-09-28T08:00:00Z", stantio: false }) =>
  ({ attiva: true, elementi: ids.map(notizia), meta });
const SPENTA = { attiva: false, elementi: [], meta: null };

beforeEach(() => {
  globalThis.window = {
    localStorage: deposito(), sessionStorage: deposito(),
    location: { origin: "https://ersaf.invalid", pathname: "/edunews24", search: "", hash: "", replace: (url) => redirect.push(url) },
  };
  richieste.length = risposte.length = redirect.length = 0;
  azzeraEsitoFunzione();
  globalThis.fetch = async (url, opzioni) => {
    richieste.push({ url, ...opzioni });
    const risposta = risposte.shift();
    if (risposta instanceof Error) throw risposta;
    assert.ok(risposta, "richiesta HTTP inattesa");
    return risposta;
  };
});

test("chiama il backend con la sessione, senza cache e con il segnale", async () => {
  const controller = new AbortController();
  risposte.push(json(elenco([1, 2], { cursore_successivo: "m20-abcdef12", aggiornato_il: "2026-09-28T08:00:00Z", stantio: true })));
  const pagina = await caricaElencoEduNews24("/edunews24/notizie?categoria=scuola", null, controller.signal, () => 1234);
  assert.equal(richieste[0].url, `${API_BASE_URL}/edunews24/notizie?categoria=scuola`);
  assert.equal(richieste[0].headers["X-ERSAF-Request"], "1");
  assert.equal(richieste[0].credentials, "include");
  assert.equal(richieste[0].cache, "no-store");
  assert.equal(richieste[0].signal, controller.signal);
  assert.deepEqual(pagina.elementi.map((v) => v.id), [1, 2]);
  assert.deepEqual([pagina.attiva, pagina.cursore, pagina.stantio, pagina.aggiornatoIl, pagina.ricevutoIl],
    [true, "m20-abcdef12", true, "2026-09-28T08:00:00Z", 1234]);
});

test("il cursore si aggiunge solo se ha la forma giusta", async () => {
  risposte.push(json(elenco([1])), json(elenco([2])));
  await caricaElencoEduNews24("/edunews24/interpelli?area=lazio", "m20-abcdef12", undefined, () => 0);
  await caricaElencoEduNews24("/edunews24/interpelli", "a&b=c", undefined, () => 0);
  assert.equal(richieste[0].url, `${API_BASE_URL}/edunews24/interpelli?area=lazio&cursore=m20-abcdef12`);
  assert.equal(richieste[1].url, `${API_BASE_URL}/edunews24/interpelli`);
});

test("il registro dell'esito cambia con una sola notifica", async () => {
  let notifiche = 0;
  const smetti = osservaEsitoFunzione(() => { notifiche += 1; });
  try {
    assert.equal(leggiEsitoFunzione(), "ignota");
    risposte.push(json(elenco([1])), json(elenco([2])), json(SPENTA));
    await caricaElencoEduNews24("/edunews24/notizie", null);
    assert.deepEqual([leggiEsitoFunzione(), notifiche], ["attiva", 1]);
    await caricaElencoEduNews24("/edunews24/notizie", null);
    assert.deepEqual([leggiEsitoFunzione(), notifiche], ["attiva", 1]);
    const spenta = await caricaElencoEduNews24("/edunews24/notizie", null);
    assert.deepEqual([spenta.attiva, spenta.elementi], [false, []]);
    assert.deepEqual([leggiEsitoFunzione(), notifiche], ["disattivata", 2]);
  } finally {
    smetti();
  }
});

test("un errore non cambia il registro dell'esito", async () => {
  risposte.push(json({ detail: "x" }, 503, { "Retry-After": "30" }));
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null));
  assert.equal(leggiEsitoFunzione(), "ignota");
});

test("503 con Retry-After conserva stato e secondi nell'ErroreApi", async () => {
  risposte.push(json({ detail: "EduNews24 non è raggiungibile in questo momento. Riprova più tardi." }, 503, { "Retry-After": "30" }));
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null), (e) => {
    assert.equal(e.name, "ErroreApi");
    assert.deepEqual([e.stato, e.attesaSecondi, e.tipo, e.message], [503, 30, "servizio", testi.erroreModulo]);
    return true;
  });
});

test("409 e 400 portano il tipo e il testo del loro contesto", async () => {
  risposte.push(json({ detail: "x" }, 409), json({ detail: "Categoria sconosciuta." }, 400), json({ detail: [] }, 422));
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", "m20-abcdef12"),
    (e) => e.stato === 409 && e.tipo === "cursore" && e.message === testi.cursore && e.attesaSecondi === 0);
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie?categoria=inesistente", null),
    (e) => e.stato === 400 && e.tipo === "richiesta" && e.message === testi.filtroNonValido);
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null), (e) => e.stato === 422 && e.tipo === "richiesta");
});

test("401 porta al login e risale cosi' com'e'", async () => {
  risposte.push(json({ detail: "Sessione scaduta" }, 401));
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null), (e) => e.stato === 401 && e.tipo === undefined);
  assert.equal(redirect.length, 1);
  assert.match(redirect[0], /^\/\?sessione=scaduta$/);
  assert.equal(window.sessionStorage.getItem("ritorno_accesso"), "/edunews24");
});

test("JSON non valido o forma sbagliata danno una risposta non valida", async () => {
  risposte.push(
    new Response("<html>non json</html>", { status: 200 }),
    json({ attiva: "si", elementi: [] }),
    json({ attiva: true, elementi: "nessuno", meta: null }),
  );
  for (let i = 0; i < 3; i += 1) {
    await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null),
      (e) => e.tipo === "risposta" && e.stato === 200 && e.message === testi.erroreModulo);
  }
  assert.equal(leggiEsitoFunzione(), "ignota");
});

test("un errore di rete diventa un errore di tipo rete, un annullamento no", async () => {
  risposte.push(new TypeError("Failed to fetch"));
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null), (e) => e.stato === 0 && e.tipo === "rete");
  const controller = new AbortController();
  controller.abort();
  risposte.push(new DOMException("annullata", "AbortError"));
  await assert.rejects(caricaElencoEduNews24("/edunews24/notizie", null, controller.signal),
    (e) => e.name === "ErroreApi" && e.stato === 0 && e.tipo === undefined);
});

test("le categorie arrivano dagli elementi e aggiornano l'esito", async () => {
  risposte.push(json({ attiva: true, elementi: [{ slug: "scuola", nome: "Scuola" }, { slug: "X", nome: "X" }], meta: null }));
  const controller = new AbortController();
  assert.deepEqual(await caricaCategorieEduNews24(controller.signal),
    { attiva: true, categorie: [{ slug: "scuola", nome: "Scuola" }], stantio: false });
  assert.equal(richieste[0].url, `${API_BASE_URL}/edunews24/categorie`);
  assert.equal(richieste[0].cache, "no-store");
  assert.equal(leggiEsitoFunzione(), "attiva");
  risposte.push(json({ attiva: true, elementi: null, meta: null }));
  await assert.rejects(caricaCategorieEduNews24(controller.signal), (e) => e.tipo === "risposta");
});
