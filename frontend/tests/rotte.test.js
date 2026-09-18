import { test } from "node:test";
import assert from "node:assert/strict";
import { matchRoutes } from "react-router";
import { PERCORSI, ROTTE, idValido } from "../src/config/routes/percorsi.js";
import { leggiQuery, aggiornaQuery } from "../src/lib/queryPagina.js";
import { QUERY_ANAGRAFICA, QUERY_PRATICHE, QUERY_PRODOTTI } from "../src/config/routes/query.js";
import { queryClienti, queryProdotti } from "../src/lib/queryElenchi.js";
import { queryPratiche } from "../src/lib/pratiche.js";

const registrate = [...Object.values(ROTTE).map(path => ({ path })),
  ...Object.values(PERCORSI).flatMap(r => [{ path: r.nuovo }, { path: r.modello }])];
test("ogni sezione ha elenco, creazione e dettaglio con un identificativo esplicito", () => {
  for (const r of Object.values(PERCORSI)) {
    assert.equal(matchRoutes(registrate, r.elenco)[0].route.path, r.elenco);
    assert.equal(matchRoutes(registrate, r.nuovo)[0].route.path, r.nuovo);
    assert.equal(matchRoutes(registrate, r.dettaglio(42))[0].params[r.parametro], "42");
  }
  assert.equal(PERCORSI.attuatori.dettaglio(42), "/attuatori/42");
  assert.equal(PERCORSI.sottoscrittori.dettaglio(42), "/sottoscrittori/42");
});
test("non esistono alias delle vecchie rotte o route utente con ID cliente", () => {
  for (const path of ["/nuovo", "/modifica/42", "/utente/42", "/nuova-azienda", "/modifica-azienda/42",
    "/inserimentoprodotto", "/inserimentoprodotto/42", "/nuova-pratica", "/modifica-pratica/42", "/home", "/elenco", "/prodotti-formativi", "/non-esiste"]) {
    assert.equal(matchRoutes(registrate, path), null, path);
  }
});
test("un ID malformato non costruisce un collegamento a un form", () => {
  for (const id of [undefined, null, "", 0, -1, "01", "1e2", "1/2", "abc", "2?tipo=attuatore", Number.MAX_SAFE_INTEGER + 1]) {
    assert.equal(idValido(id), false, String(id));
    assert.throws(() => PERCORSI.aziende.dettaglio(id), TypeError);
  }
});
test("le schede si riaprono dalla query, con fallback solo per valori non validi", () => {
  assert.equal(leggiQuery("?scheda=utente", QUERY_ANAGRAFICA).scheda, "utente");
  assert.equal(leggiQuery("?scheda=inesistente", QUERY_ANAGRAFICA).scheda, "dati-principali");
  assert.equal(aggiornaQuery("?scheda=utente", { scheda: "dati-principali" }, QUERY_ANAGRAFICA), "");
});
test("l'azzeramento prodotti elimina tutti i filtri in una transazione e conserva la ricerca", () => {
  const url = aggiornaQuery("?ricerca=corso&universita=Roma&tipo=Master&attivo=S%C3%AC", {
    universita: "Tutte le università", tipo: "Tutti i tipi", attivo: "Tutti",
  }, QUERY_PRODOTTI);
  assert.equal(url, "?ricerca=corso");
  assert.deepEqual(leggiQuery(url, QUERY_PRODOTTI), { ricerca: "corso", universita: "Tutte le università", tipo: "Tutti i tipi", attivo: "Tutti" });
});
test("Pratiche conserva ID multipli senza etichette, scarta invalidi e duplicati", () => {
  const filtri = { ricerca: "A&B", numeroPratica: "000045", stato: "2", studenti: [17, 23],
    universita: "5", tipoCorso: [3, 8], filtroInterno: "1", tipoSelezionato: "8" };
  const url = aggiornaQuery("", filtri, QUERY_PRATICHE);
  const q = leggiQuery(url, QUERY_PRATICHE);
  assert.deepEqual(q, filtri);
  const api = queryPratiche({ ...q, studenti: q.studenti.map(id => ({ id })) });
  assert.deepEqual(new URL(api, "http://locale").searchParams.getAll("studenti"), ["17", "23"]);
  assert.deepEqual(leggiQuery("?studenti=17&studenti=17&studenti=-1&studenti=x&stato=0", QUERY_PRATICHE).studenti, [17]);
  const invalidi = leggiQuery("?stato=abc&universita=0&tipoCorso=3&tipoCorso=3&tipoCorso=x&filtroInterno=2&tipoSelezionato=-4", QUERY_PRATICHE);
  assert.deepEqual([invalidi.stato, invalidi.universita, invalidi.filtroInterno, invalidi.tipoSelezionato], ["", "", "", ""]);
  assert.deepEqual(invalidi.tipoCorso, [3]);
});
test("le query frontend preservano i contratti API esistenti", () => {
  const clienti = new URL(queryClienti({ ricerca: "Rossi", ruolo: "Nazionale" }, { soloUtenti: true }), "http://locale");
  assert.equal(clienti.searchParams.get("ruolo_codice"), null);
  assert.equal(clienti.searchParams.get("solo_utenti"), "true");
  const prodotti = new URL(queryProdotti({ ricerca: "corso", universita: "Università A&B", tipo: "Master", attivo: "Sì" }), "http://locale");
  assert.equal(prodotti.searchParams.get("attivo"), "-1");
  assert.equal(prodotti.searchParams.get("tipo_corso"), "Master");
  assert.equal(prodotti.searchParams.get("universita"), "Università A&B");
});
