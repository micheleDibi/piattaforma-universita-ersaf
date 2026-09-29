import { test } from "node:test";
import assert from "node:assert/strict";
import { creaPaginazioneCursore } from "../src/lib/edunews24Paginazione.js";
import { ErroreApi } from "../src/lib/erroriApi.js";

const notizia = (id) => ({ tipo: "notizia", id, titolo: `Titolo ${id}`, url: `https://edunews24.invalid/articoli/${id}` });
const pagina = (ids, cursore = null, extra = {}) => ({
  attiva: true, elementi: ids.map(notizia), cursore, stantio: false, aggiornatoIl: "2026-09-28T08:00:00Z", ricevutoIl: 0, ...extra,
});
const intervallo = (da, a) => Array.from({ length: a - da + 1 }, (_, i) => da + i);

function sospesa() {
  let risolvi, rifiuta;
  const promessa = new Promise((ok, ko) => { risolvi = ok; rifiuta = ko; });
  return { promessa, risolvi, rifiuta };
}

// Ogni esito e' una pagina, un errore da sollevare o una promessa da attendere.
function prepara(...esiti) {
  const chiamate = [];
  const stati = [];
  let tempo = 1000;
  const paginazione = creaPaginazioneCursore({
    richiedi: async (cursore, signal) => {
      chiamate.push({ cursore, signal });
      assert.ok(esiti.length > 0, "richiesta inattesa");
      const esito = esiti.shift();
      if (esito instanceof Error) throw esito;
      return esito;
    },
    pubblica: (stato) => stati.push(stato),
    orologio: () => (tempo += 1000),
  });
  return { paginazione, chiamate, stati, ultimo: () => stati.at(-1) };
}

test("avvia non pubblica in modo sincrono; la prima pagina fissa adesso e quantePrimaPagina", async () => {
  const { paginazione, chiamate, stati, ultimo } = prepara(pagina(intervallo(1, 20), "c2"));
  const avvio = paginazione.avvia();
  assert.equal(stati.length, 0);
  assert.equal(chiamate[0].cursore, null);
  await avvio;
  assert.equal(stati.length, 1);
  const stato = ultimo();
  assert.deepEqual(
    [stato.elementi.length, stato.altri, stato.loading, stato.primaCaricata, stato.quantePrimaPagina, stato.adesso, stato.errore],
    [20, true, false, true, 20, 2000, null],
  );
  assert.deepEqual(stato.lunghezzePagine, [20]);
  assert.deepEqual([stato.stantio, stato.aggiornatoIl, stato.disattivata, stato.ripartito], [false, "2026-09-28T08:00:00Z", false, false]);
});

test("prossima pubblica subito il caricamento e poi accoda deduplicando", async () => {
  const { paginazione, chiamate, stati, ultimo } = prepara(pagina(intervallo(1, 20), "c2"), pagina(intervallo(19, 28), null));
  await paginazione.avvia();
  const altra = paginazione.prossima();
  assert.equal(ultimo().loading, true);
  assert.equal(ultimo().elementi.length, 20);
  await altra;
  assert.equal(chiamate[1].cursore, "c2");
  assert.deepEqual(ultimo().elementi.map((v) => v.id), intervallo(1, 28));
  assert.deepEqual(ultimo().lunghezzePagine, [20, 8]);
  // adesso resta quello della prima pagina.
  assert.deepEqual([ultimo().adesso, ultimo().quantePrimaPagina, ultimo().altri], [2000, 20, false]);
  const prima = stati.length;
  await paginazione.prossima();
  assert.equal(chiamate.length, 2, "all'ultima pagina non si chiede piu' nulla");
  assert.equal(stati.length, prima);
});

test("una pagina vuota con cursore lascia Carica altri", async () => {
  const { paginazione, ultimo } = prepara(pagina([], "c2"), pagina([1, 2], null));
  await paginazione.avvia();
  assert.deepEqual([ultimo().altri, ultimo().primaCaricata, ultimo().elementi, ultimo().lunghezzePagine], [true, true, [], [0]]);
  await paginazione.prossima();
  assert.deepEqual([ultimo().altri, ultimo().lunghezzePagine], [false, [0, 2]]);
});

test("il primo 409 riparte una volta sola dalla prima pagina e ignora le prossima nel frattempo", async () => {
  const ripartenza = sospesa();
  const { paginazione, chiamate, stati, ultimo } = prepara(
    pagina(intervallo(1, 20), "c2"), new ErroreApi("cambiato", 409), ripartenza.promessa,
  );
  await paginazione.avvia();
  const altra = paginazione.prossima();
  await new Promise((fatto) => setTimeout(fatto, 0));
  const stato = ultimo();
  assert.deepEqual([stato.elementi, stato.loading, stato.primaCaricata, stato.ripartito, stato.errore], [[], true, false, true, null]);
  assert.deepEqual(stato.lunghezzePagine, []);
  assert.equal(chiamate.length, 3);
  assert.equal(chiamate[2].cursore, null);
  const pubblicati = stati.length;
  await paginazione.prossima();
  assert.equal(chiamate.length, 3, "una prossima durante la ripartenza si ignora");
  assert.equal(stati.length, pubblicati);
  ripartenza.risolvi(pagina(intervallo(101, 120), "d2"));
  await altra;
  assert.deepEqual([ultimo().elementi[0].id, ultimo().primaCaricata, ultimo().ripartito, ultimo().quantePrimaPagina], [101, true, true, 20]);
  assert.equal(ultimo().adesso, 3000);
});

test("il secondo 409 pubblica l'errore e Riprova riparte dalla prima pagina", async () => {
  const { paginazione, chiamate, ultimo } = prepara(
    pagina(intervallo(1, 20), "c2"), new ErroreApi("cambiato", 409), pagina(intervallo(101, 120), "d2"),
    new ErroreApi("di nuovo", 409), pagina(intervallo(201, 220), "e2"),
  );
  await paginazione.avvia();
  await paginazione.prossima();
  await paginazione.prossima();
  assert.equal(chiamate[3].cursore, "d2");
  assert.deepEqual([ultimo().errore, ultimo().statoErrore, ultimo().elementi.length, ultimo().loading], ["di nuovo", 409, 20, false]);
  const riprova = paginazione.prossima();
  assert.deepEqual([ultimo().elementi, ultimo().loading, ultimo().primaCaricata, ultimo().errore], [[], true, false, null]);
  await riprova;
  assert.equal(chiamate[4].cursore, null);
  assert.deepEqual([ultimo().elementi[0].id, ultimo().errore, ultimo().lunghezzePagine], [201, null, [20]]);
});

test("un 503 conserva voci e cursore, e il nuovo tentativo riusa lo stesso cursore", async () => {
  const { paginazione, chiamate, ultimo } = prepara(
    pagina(intervallo(1, 20), "c2"), new ErroreApi("non risponde", 503, 30), pagina(intervallo(21, 25), null),
  );
  await paginazione.avvia();
  await paginazione.prossima();
  assert.deepEqual([ultimo().errore, ultimo().statoErrore, ultimo().attesaSecondi, ultimo().elementi.length, ultimo().altri],
    ["non risponde", 503, 30, 20, true]);
  const riprova = paginazione.prossima();
  assert.deepEqual([ultimo().errore, ultimo().attesaSecondi, ultimo().loading], [null, 0, true]);
  await riprova;
  assert.equal(chiamate[2].cursore, "c2");
  assert.deepEqual([ultimo().elementi.length, ultimo().altri, ultimo().lunghezzePagine], [25, false, [20, 5]]);
});

test("dopo un errore della prima pagina si richiede di nuovo la prima pagina", async () => {
  const { paginazione, chiamate, ultimo } = prepara(new ErroreApi("non risponde", 503, 5), pagina([1, 2], null));
  await paginazione.avvia();
  assert.deepEqual([ultimo().primaCaricata, ultimo().statoErrore, ultimo().attesaSecondi], [false, 503, 5]);
  await paginazione.prossima();
  assert.equal(chiamate[1].cursore, null);
  assert.deepEqual([ultimo().primaCaricata, ultimo().elementi.length], [true, 2]);
});

test("un errore senza messaggio ha comunque un testo", async () => {
  const { paginazione, ultimo } = prepara(new Error(""));
  await paginazione.avvia();
  assert.ok(ultimo().errore);
  assert.equal(ultimo().statoErrore, 0);
});

test("un 401 non pubblica nulla", async () => {
  const { paginazione, stati } = prepara(new ErroreApi("sessione", 401));
  await paginazione.avvia();
  assert.equal(stati.length, 0);
  const seconda = prepara(pagina([1], "c2"), new ErroreApi("sessione", 401));
  await seconda.paginazione.avvia();
  await seconda.paginazione.prossima();
  assert.equal(seconda.stati.length, 2);
  assert.equal(seconda.ultimo().loading, true);
});

test("un annullamento ignora l'esito, anche di un errore", async () => {
  const attesa = sospesa();
  const { paginazione, stati } = prepara(attesa.promessa);
  const avvio = paginazione.avvia();
  paginazione.annulla();
  attesa.risolvi(pagina([1, 2], null));
  await avvio;
  assert.equal(stati.length, 0);
  const errore = sospesa();
  const seconda = prepara(errore.promessa);
  const avvioSeconda = seconda.paginazione.avvia();
  seconda.paginazione.annulla();
  errore.rifiuta(new ErroreApi("annullata", 0));
  await avvioSeconda;
  assert.equal(seconda.stati.length, 0);
  await seconda.paginazione.prossima();
  assert.equal(seconda.chiamate.length, 1);
});

test("attiva false pubblica la funzione disattivata e ferma la paginazione", async () => {
  const { paginazione, chiamate, ultimo } = prepara({ attiva: false, elementi: [], cursore: null, stantio: false, aggiornatoIl: null });
  await paginazione.avvia();
  assert.deepEqual([ultimo().disattivata, ultimo().altri, ultimo().elementi], [true, false, []]);
  await paginazione.prossima();
  assert.equal(chiamate.length, 1);
});

test("una prossima concorrente si ignora", async () => {
  const seconda = sospesa();
  const { paginazione, chiamate } = prepara(pagina(intervallo(1, 20), "c2"), seconda.promessa);
  await paginazione.avvia();
  const prima = paginazione.prossima();
  await paginazione.prossima();
  assert.equal(chiamate.length, 2);
  seconda.risolvi(pagina([21], null));
  await prima;
});

test("stantio resta vero se una pagina lo era; aggiornatoIl e' il piu' vecchio", async () => {
  const { paginazione, ultimo } = prepara(
    pagina([1], "c2", { aggiornatoIl: "2026-09-28T08:00:00Z" }),
    pagina([2], "c3", { stantio: true, aggiornatoIl: "2026-09-27T16:40:00Z" }),
    pagina([3], null, { aggiornatoIl: null }),
  );
  await paginazione.avvia();
  await paginazione.prossima();
  await paginazione.prossima();
  assert.deepEqual([ultimo().stantio, ultimo().aggiornatoIl], [true, "2026-09-27T16:40:00Z"]);
});
