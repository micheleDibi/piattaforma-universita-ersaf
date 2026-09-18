import { test } from "node:test";
import assert from "node:assert/strict";
import { rigaCliente, rigaAzienda, rigaPratica, rigaProdotto, vociLegendaCliente, campoIndicatori, idIndicatori } from "../src/lib/righeElenco.js";
import { modelloClienti, MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI } from "../src/config/elenchi.js";
import { ICONE_CAMPI_ELENCO } from "../src/config/icone.js";

test("ogni icona indicata dai campi degli elenchi esiste nel catalogo", () => {
  const modelli = [MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI, modelloClienti({ attuatori: true, mostraAzienda: true })];
  for (const modello of modelli) {
    for (const campo of [...modello.mobile, ...modello.colonne.flatMap((c) => c.campi)]) {
      if (campo.icona) assert.ok(ICONE_CAMPI_ELENCO[campo.icona], `${modello.id}.${campo.id}: icona "${campo.icona}" assente`);
    }
  }
});

test("nome e cognome separati e nominativo mobile conservano ID cliente e campi parziali", () => {
  const item = { cliente_id: 14, utente_id: 9, cliente_nome: " Maria Alessandra ", cliente_cognome: "Della Valle" };
  const opzioni = { attuatori: false, mostraAzienda: false };
  assert.equal(rigaCliente(item, opzioni).id, 14);
  assert.equal(rigaCliente(item, opzioni).campi.nominativo, "Maria Alessandra Della Valle");
  assert.equal(rigaCliente(item, opzioni).campi.nome, "Maria Alessandra");
  assert.equal(rigaCliente(item, opzioni).campi.cognome, "Della Valle");
  assert.equal(rigaCliente({ cliente_cognome: "D'Amico" }, opzioni).campi.nominativo, "D'Amico");
  assert.equal(rigaCliente({ cliente_cognome: "D'Amico" }, opzioni).campi.nome, "-");
});

test("azienda e ruolo rispettano la visibilità anche nella presentazione mobile", () => {
  const item = { ruolo: { ruolo_codice: "Regionale" }, azienda: { azienda_ragione_sociale: "Centro test" } };
  for (const opzioni of [{ attuatori: true, mostraAzienda: true }, { attuatori: true, mostraAzienda: false }, { attuatori: false, mostraAzienda: false }]) {
    const riga = rigaCliente(item, opzioni);
    const modello = modelloClienti(opzioni);
    assert.equal(Object.hasOwn(riga.campi, "azienda"), opzioni.mostraAzienda);
    assert.equal(modello.mobile.some((campo) => campo.id === "azienda"), opzioni.mostraAzienda);
    assert.equal(Object.hasOwn(riga.campi, "ruolo"), opzioni.attuatori);
    const campiDesktop = modello.colonne.flatMap((c) => c.campi);
    assert.equal(campiDesktop.some((campo) => campo.id === "azienda"), opzioni.mostraAzienda);
    assert.equal(campiDesktop.some((campo) => campo.id === "ruolo"), opzioni.attuatori);
    assert.equal(modello.mobile.some((campo) => campo.id === "ruolo"), opzioni.attuatori);
  }
});

test("sede conserva CAP e civico alfanumerico, anche senza via o città", () => {
  assert.equal(rigaAzienda({ azienda_via: "Via delle Rose", azienda_civico: "12/A", azienda_CAP: "00100", azienda_citta: "Roma", azienda_provincia: "RM" }).campi.sede,
    "Via delle Rose 12/A, 00100 Roma (RM)");
  assert.equal(rigaAzienda({ azienda_CAP: "00100", azienda_provincia: "RM" }).campi.sede, "00100 (RM)");
  assert.equal(rigaAzienda({}).campi.sede, "-");
});

test("flag legacy prodotto: solo -1 significa attivo; codici e titoli non vengono troncati", () => {
  const titolo = "Percorso di formazione ".repeat(10);
  const codice = "CATALOGO0123456789".repeat(2);
  for (const valore of [-1, 0, 1, null, undefined]) {
    const riga = rigaProdotto({ listTesta_id: 22, listTesta_descrizione: titolo, listTesta_codice: codice, listino_attivoSN: valore });
    assert.equal(riga.id, 22);
    assert.equal(riga.campi.stato, valore === -1 ? "Attivo" : "Non attivo");
    assert.equal(riga.campi.titolo, titolo.trim());
    assert.equal(riga.campi.codice, codice);
  }
});

test("desktop e mobile espongono gli stessi campi per aziende, pratiche e prodotti", () => {
  for (const modello of [MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI]) {
    const desktop = modello.colonne.flatMap((c) => c.campi.map((campo) => campo.id)).sort();
    assert.deepEqual(desktop, modello.mobile.map((campo) => campo.id).sort());
  }
  const pratica = rigaPratica({ pratica_id: 83, cliente_id: 19, pratica_numero: "000045", cliente_nome_completo: "Maria Della Valle" });
  assert.equal(pratica.id, 83);
  assert.equal(pratica.campi.numero, "000045");
  assert.equal(rigaPratica({ pratica_id: 83 }).campi.numero, "-");
});

test("modello elenchi: codice e stato hanno rilievi dedicati e i campi secondari definiscono icone dal catalogo", () => {
  const prodottoCodice = MODELLO_PRODOTTI.mobile.find((c) => c.id === "codice");
  const prodottoStato = MODELLO_PRODOTTI.mobile.find((c) => c.id === "stato");
  const universita = MODELLO_PRODOTTI.mobile.find((c) => c.id === "universita");
  assert.equal(prodottoCodice.rilievo, "codice");
  assert.equal(prodottoStato.rilievo, "stato");
  assert.equal(universita.icona, "universita");
});

const ATTUATORI = { attuatori: true, mostraAzienda: false };
const SOTTOSCRITTORI = { attuatori: false, mostraAzienda: false };
const STATO_PIENO = { email_verificata: true, cellulare_verificato: true, diploma_completo: true };

test("stato cliente: due pallini per gli attuatori e tre per i sottoscrittori, sempre nello stesso ordine", () => {
  const ordine = (opzioni, item = STATO_PIENO) => rigaCliente(item, opzioni).campi.stato.map((i) => i.id);
  assert.deepEqual(ordine(ATTUATORI), ["email", "cellulare"]);
  assert.deepEqual(ordine({ ...ATTUATORI, mostraAzienda: true }), ["email", "cellulare"]);
  assert.deepEqual(ordine(SOTTOSCRITTORI), ["email", "cellulare", "diploma"]);
  // Il numero di pallini dipende dall'elenco, non dai campi presenti nella risposta.
  assert.deepEqual(ordine(SOTTOSCRITTORI, {}), ["email", "cellulare", "diploma"]);
  assert.deepEqual(ordine(ATTUATORI, { ...STATO_PIENO, diploma_completo: false }), ["email", "cellulare"]);
});

test("stato cliente: verde solo con true, grigio con false, null, assente o valori legacy", () => {
  for (const valore of [true, false, null, undefined, -1, 1, 0, "true", "1"]) {
    for (const campo of ["email_verificata", "cellulare_verificato", "diploma_completo"]) {
      const item = { ...STATO_PIENO, [campo]: valore };
      if (valore === undefined) delete item[campo];
      const stato = rigaCliente(item, SOTTOSCRITTORI).campi.stato;
      const indice = ["email_verificata", "cellulare_verificato", "diploma_completo"].indexOf(campo);
      stato.forEach((indicatore, i) => {
        assert.equal(indicatore.attivo, i === indice ? valore === true : true, `${campo}=${String(valore)}, pallino ${i}`);
      });
    }
  }
});

test("stato cliente: ogni pallino ha l'etichetta del proprio stato", () => {
  const etichette = (item, opzioni = SOTTOSCRITTORI) => rigaCliente(item, opzioni).campi.stato.map((i) => i.etichetta);
  assert.deepEqual(etichette(STATO_PIENO), ["Email verificata", "Cellulare verificato", "Dati diploma completi"]);
  assert.deepEqual(etichette({}), ["Email non verificata", "Cellulare non verificato", "Dati diploma incompleti"]);
  assert.deepEqual(etichette({ email_verificata: false, cellulare_verificato: true }, ATTUATORI),
    ["Email non verificata", "Cellulare verificato"]);
});

test("stato cliente: la colonna esiste su desktop e su mobile, con i pallini e non con il badge", () => {
  for (const opzioni of [ATTUATORI, SOTTOSCRITTORI, { attuatori: true, mostraAzienda: true }]) {
    const modello = modelloClienti(opzioni);
    const desktop = modello.colonne.flatMap((c) => c.campi).filter((campo) => campo.id === "stato");
    const mobile = modello.mobile.filter((campo) => campo.id === "stato");
    assert.equal(desktop.length, 1);
    assert.equal(mobile.length, 1);
    assert.equal(desktop[0].rilievo, "indicatori");
    assert.equal(mobile[0].rilievo, "indicatori");
    assert.deepEqual(modello.colonne.map((c) => c.id).slice(0, 3), ["nome", "cognome", "stato"]);
    assert.equal(modello.mobile[1].id, "stato");
    // Ogni campo del modello ha un valore nella riga.
    const riga = rigaCliente({}, opzioni);
    for (const campo of [...modello.mobile, ...modello.colonne.flatMap((c) => c.campi)]) {
      assert.ok(Object.hasOwn(riga.campi, campo.id), `${campo.id} assente nella riga`);
    }
  }
  // Pratiche e prodotti conservano il badge.
  assert.equal(MODELLO_PRATICHE.mobile.find((c) => c.id === "stato").rilievo, "stato");
  assert.equal(MODELLO_PRODOTTI.mobile.find((c) => c.id === "stato").rilievo, "stato");
});

test("legenda: stesse voci e stesso ordine dei pallini della pagina", () => {
  const voce = { email: "Email", cellulare: "Cellulare", diploma: "Diploma" };
  for (const opzioni of [ATTUATORI, SOTTOSCRITTORI]) {
    const pallini = rigaCliente(STATO_PIENO, opzioni).campi.stato.map((i) => voce[i.id]);
    assert.deepEqual(vociLegendaCliente(opzioni), pallini);
  }
  assert.deepEqual(vociLegendaCliente(ATTUATORI), ["Email", "Cellulare"]);
  assert.deepEqual(vociLegendaCliente(SOTTOSCRITTORI), ["Email", "Cellulare", "Diploma"]);
});

test("descrizione accessibile: solo le righe con pallini la ricevono, con id distinti per vista e per riga", () => {
  const modello = modelloClienti(SOTTOSCRITTORI);
  const desktop = campoIndicatori(modello.colonne.flatMap((c) => c.campi));
  const mobile = campoIndicatori(modello.mobile);
  assert.equal(desktop.id, "stato");
  assert.equal(mobile.id, "stato");
  const prima = rigaCliente({ cliente_id: 1 }, SOTTOSCRITTORI);
  const seconda = rigaCliente({ cliente_id: 2 }, SOTTOSCRITTORI);
  assert.notEqual(idIndicatori(":a:", prima, desktop), idIndicatori(":b:", prima, mobile));
  assert.notEqual(idIndicatori(":a:", prima, desktop), idIndicatori(":a:", seconda, desktop));
  assert.equal(idIndicatori(":a:", { id: 3, campi: { stato: [] } }, desktop), undefined);
  // Gli altri elenchi non hanno pallini: nessun aria-describedby.
  for (const altro of [MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI]) {
    const campo = campoIndicatori([...altro.mobile, ...altro.colonne.flatMap((c) => c.campi)]);
    assert.equal(campo, undefined);
    assert.equal(idIndicatori(":a:", rigaPratica({ pratica_id: 4 }), campo), undefined);
  }
});
