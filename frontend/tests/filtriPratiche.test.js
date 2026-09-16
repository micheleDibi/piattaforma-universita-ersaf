import test from "node:test";
import assert from "node:assert/strict";
import { queryPratiche } from "../src/lib/pratiche.js";
import { cambiaSelezione } from "../src/lib/selezioneRicercabile.js";
import { creaPaginazione } from "../src/lib/pagineRemote.js";

test("query conserva numero, stato, percorso e tutti gli ID cliente", () => {
  const query = new URL(queryPratiche({ ricerca: " A&B ", stato: "2", studenti: [{ id: 7 }, { id: 19 }], percorso: { id: 40 } }), "https://example.org");
  assert.equal(query.searchParams.get("search"), "A&B");
  assert.deepEqual(query.searchParams.getAll("studenti"), ["7", "19"]);
  assert.equal(query.searchParams.get("pratica_stato_id"), "2");
  assert.equal(query.searchParams.get("percorso_id"), "40");
  const vuota = queryPratiche({ ricerca: "", stato: "", studenti: [], percorso: null });
  assert.equal(vuota, "/pratiche/?limit=40");
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
