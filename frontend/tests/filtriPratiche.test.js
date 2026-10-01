import test from "node:test";
import assert from "node:assert/strict";
import { gruppoUnico, queryConteggiNazionale, queryPratiche, queryPraticheNazionale, raggruppaPerStato, statiNazionale } from "../src/lib/pratiche.js";
import { cambiaSelezione } from "../src/lib/selezioneRicercabile.js";
import { creaPaginazione } from "../src/lib/pagineRemote.js";

const SENZA_FILTRI = { ricerca: "", numeroPratica: "", stato: "", studenti: [], universita: "", tipoCorso: [], tipoSelezionato: "" };

test("query conserva ricerca, numero pratica, stato, universita', tipi di corso e tutti gli ID cliente", () => {
  const query = new URL(queryPratiche({ ...SENZA_FILTRI, ricerca: " A&B ", numeroPratica: " 000045 ", stato: "2",
    studenti: [{ id: 7 }, { id: 19 }], universita: "5", tipoCorso: [3, 8] }), "https://example.org");
  assert.equal(query.searchParams.get("search"), "A&B");
  assert.equal(query.searchParams.get("numero_pratica"), "000045");
  assert.equal(query.searchParams.get("pratica_stato_id"), "2");
  assert.deepEqual(query.searchParams.getAll("studenti"), ["7", "19"]);
  assert.equal(query.searchParams.get("nome_universita_id"), "5");
  assert.deepEqual(query.searchParams.getAll("listino_tipo_corso_id"), ["3", "8"]);
  assert.equal(queryPratiche(SENZA_FILTRI), "/pratiche/?limit=40");
});

test("un tipo di corso selezionato prevale sull'elenco dei tipi", () => {
  const query = new URL(queryPratiche({ ...SENZA_FILTRI, tipoCorso: [3, 8], tipoSelezionato: "8" }), "https://example.org");
  assert.deepEqual(query.searchParams.getAll("listino_tipo_corso_id"), ["8"]);
});

test("selezioni indipendenti dai risultati e rimozione per ID anche con omonimi", () => {
  const anna = { id: 1, label: "Anna" }, altra = { id: 2, label: "Anna" };
  assert.deepEqual(cambiaSelezione([anna], altra, true), [anna, altra]);
  assert.deepEqual(cambiaSelezione([anna, altra], anna, true), [altra]);
  assert.deepEqual(cambiaSelezione([anna], altra, false), [altra]);
});

test("risposta obsoleta dopo cambio filtro non viene pubblicata", async () => {
  let risolvi;
  const stati = [];
  const pagine = creaPaginazione(() => new Promise(resolve => { risolvi = resolve; }), s => stati.push(s));
  const richiesta = pagine.prossima();
  pagine.annulla();
  risolvi({ elementi: [1], altri: false });
  await richiesta;
  assert.equal(stati.length, 1);
  assert.deepEqual(stati[0].elementi, []);
});

test("errore pagina non avanza offset, riprova conserva risultati, richieste simultanee escluse", async () => {
  const offset = [], stati = [];
  let tentativo = 0;
  const pagine = creaPaginazione(async skip => {
    offset.push(skip);
    if (++tentativo === 2) throw new Error("offline");
    return { elementi: [tentativo], altri: tentativo < 3 };
  }, s => stati.push(s));
  await Promise.all([pagine.prossima(), pagine.prossima()]);
  await pagine.prossima();
  assert.deepEqual(stati.at(-1).elementi, [1]);
  assert.equal(stati.at(-1).errore, "offline");
  await pagine.prossima();
  await pagine.prossima();
  assert.deepEqual(offset, [0, 1, 1]);
  assert.deepEqual(stati.at(-1).elementi, [1, 3]);
});


test("righe ripetute tra pagine non si duplicano e offset segue le righe ricevute", async () => {
  const offset = [], stati = [];
  const pagine = creaPaginazione(async skip => {
    offset.push(skip);
    return { elementi: [{ pratica_id: 5 }], altri: skip < 2 };
  }, stato => stati.push(stato));
  await pagine.prossima(); await pagine.prossima(); await pagine.prossima();
  assert.deepEqual(offset, [0, 1, 2]);
  assert.deepEqual(stati.at(-1).elementi, [{ pratica_id: 5 }]);
});

test("paginazione condivisa riconosce anche le identita cliente, azienda e prodotto", async () => {
  for (const campo of ["cliente_id", "azienda_id", "listTesta_id"]) {
    const stati = [];
    const pagine = creaPaginazione(async skip => ({ elementi: [{ [campo]: 42 }], altri: skip === 0 }), s => stati.push(s));
    await pagine.prossima(); await pagine.prossima();
    assert.equal(stati.at(-1).elementi.length, 1, campo);
  }
});

const NAZIONALE_SENZA_FILTRI = { ricerca: "", numeroPratica: "", stato: "", universita: "" };

test("elenco del Nazionale: senza Bozze, ordinato per stato, stessi filtri per i conteggi", () => {
  const filtri = { ricerca: " Rossi ", numeroPratica: " MT0001 ", stato: "4", universita: "1" };
  const elenco = new URL(queryPraticheNazionale(filtri), "https://example.org");
  assert.equal(elenco.pathname, "/pratiche/");
  assert.equal(elenco.searchParams.get("escludi_bozze"), "true");
  assert.equal(elenco.searchParams.get("ordine"), "stato");
  assert.equal(elenco.searchParams.get("limit"), "40");
  assert.equal(elenco.searchParams.get("search"), "Rossi");
  assert.equal(elenco.searchParams.get("numero_pratica"), "MT0001");
  assert.equal(elenco.searchParams.get("pratica_stato_id"), "4");
  assert.equal(elenco.searchParams.get("nome_universita_id"), "1");

  const conteggi = new URL(queryConteggiNazionale(filtri), "https://example.org");
  assert.equal(conteggi.pathname, "/pratiche/conteggi/stati");
  for (const nome of ["escludi_bozze", "search", "numero_pratica", "pratica_stato_id", "nome_universita_id"]) {
    assert.equal(conteggi.searchParams.get(nome), elenco.searchParams.get(nome));
  }
  assert.equal(conteggi.searchParams.has("limit"), false);
  assert.equal(queryConteggiNazionale(NAZIONALE_SENZA_FILTRI), "/pratiche/conteggi/stati?escludi_bozze=true");
});

test("filtro Stato del Nazionale: ordine dei gruppi e niente Bozza", () => {
  const stati = [1, 2, 3, 4, 5, 6].map((id) => ({ id, label: `S${id}` }));
  assert.deepEqual(statiNazionale(stati).map((s) => s.id), [1, 4, 2, 3, 5]);
  assert.deepEqual(statiNazionale([]), []);
});

test("gruppi per stato consecutivi, con il totale di tutte le pagine", () => {
  const p = (id, stato) => ({ pratica_id: id, pratica_stato_id: stato, pratica_stato_descrizione: `Stato ${stato}` });
  const pratiche = [p(1, 1), p(2, 1), p(3, 4), p(4, 3)];
  const gruppi = raggruppaPerStato(pratiche, [{ pratica_stato_id: 1, totale: 7 }, { pratica_stato_id: 4, totale: 1 }]);
  assert.deepEqual(gruppi.map((g) => [g.statoId, g.titolo, g.totale, g.pratiche.map((x) => x.pratica_id)]), [
    [1, "Stato 1", 7, [1, 2]], [4, "Stato 4", 1, [3]], [3, "Stato 3", 0, [4]],
  ]);
  // Conteggi non ancora arrivati: i gruppi ci sono, senza numero.
  assert.deepEqual(raggruppaPerStato(pratiche, null).map((g) => g.totale), [null, null, null]);
  assert.deepEqual(raggruppaPerStato([], null), []);
});

test("senza filtri un solo gruppo, \"Tutte le pratiche\", con il totale di tutti gli stati", () => {
  const pratiche = [{ pratica_id: 1, pratica_stato_id: 1 }, { pratica_id: 2, pratica_stato_id: 4 }];
  const [tutte, ...altri] = gruppoUnico(pratiche, [{ pratica_stato_id: 1, totale: 18 }, { pratica_stato_id: 4, totale: 5 }]);
  assert.deepEqual(altri, []);
  assert.equal(tutte.titolo, "Tutte le pratiche");
  assert.equal(tutte.totale, 23);
  assert.deepEqual(tutte.pratiche, pratiche);
  assert.equal(gruppoUnico(pratiche, null)[0].totale, null);
  assert.deepEqual(gruppoUnico([], []), []);
});
