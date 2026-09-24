import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { rigaCliente, rigaAzienda, rigaPratica, rigaProdotto, campoIndicatori, idIndicatori } from "../src/lib/righeElenco.js";
import { modelloClienti, MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI, RUOLI_FILTRO } from "../src/config/elenchi.js";
import { ICONE_CAMPI_ELENCO } from "../src/config/icone.js";
import { TESTI_ELENCO } from "../src/config/testi/elenco.js";

test("ogni icona indicata dai campi degli elenchi esiste nel catalogo", () => {
  const modelli = [MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI, modelloClienti({ attuatori: true, mostraAzienda: true })];
  for (const modello of modelli) {
    for (const campo of [...modello.mobile, ...modello.colonne.flatMap((c) => c.campi)]) {
      if (campo.icona) assert.ok(ICONE_CAMPI_ELENCO[campo.icona], `${modello.id}.${campo.id}: icona "${campo.icona}" assente`);
    }
  }
});

test("nominativo \"Cognome Nome\" con iniziali, anche con campi parziali", () => {
  const item = { cliente_id: 14, utente_id: 9, cliente_nome: " Maria Alessandra ", cliente_cognome: "Della Valle" };
  const opzioni = { attuatori: false, mostraAzienda: false };
  assert.equal(rigaCliente(item, opzioni).id, 14);
  assert.equal(rigaCliente(item, opzioni).campi.nominativo, "Della Valle Maria Alessandra");
  assert.equal(rigaCliente(item, opzioni).iniziali, "DM");
  assert.equal(rigaCliente({ cliente_cognome: "D'Amico" }, opzioni).campi.nominativo, "D'Amico");
  assert.equal(rigaCliente({ cliente_cognome: "d'amico" }, opzioni).iniziali, "D");
  assert.equal(rigaCliente({}, opzioni).campi.nominativo, "-");
  assert.equal(rigaCliente({}, opzioni).iniziali, "");
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

test("verifiche cliente: due etichette per gli attuatori e tre per i sottoscrittori, sempre nello stesso ordine", () => {
  const ordine = (opzioni, item = STATO_PIENO) => rigaCliente(item, opzioni).campi.verifiche.map((i) => i.id);
  assert.deepEqual(ordine(ATTUATORI), ["email", "cellulare"]);
  assert.deepEqual(ordine({ ...ATTUATORI, mostraAzienda: true }), ["email", "cellulare"]);
  assert.deepEqual(ordine(SOTTOSCRITTORI), ["email", "cellulare", "diploma"]);
  // Il numero di pallini dipende dall'elenco, non dai campi presenti nella risposta.
  assert.deepEqual(ordine(SOTTOSCRITTORI, {}), ["email", "cellulare", "diploma"]);
  assert.deepEqual(ordine(ATTUATORI, { ...STATO_PIENO, diploma_completo: false }), ["email", "cellulare"]);
});

test("verifiche cliente: verde solo con true, grigio con false, null, assente o valori legacy", () => {
  for (const valore of [true, false, null, undefined, -1, 1, 0, "true", "1"]) {
    for (const campo of ["email_verificata", "cellulare_verificato", "diploma_completo"]) {
      const item = { ...STATO_PIENO, [campo]: valore };
      if (valore === undefined) delete item[campo];
      const stato = rigaCliente(item, SOTTOSCRITTORI).campi.verifiche;
      const indice = ["email_verificata", "cellulare_verificato", "diploma_completo"].indexOf(campo);
      stato.forEach((indicatore, i) => {
        assert.equal(indicatore.attivo, i === indice ? valore === true : true, `${campo}=${String(valore)}, pallino ${i}`);
      });
    }
  }
});

test("verifiche cliente: ogni etichetta ha l'etichetta del proprio stato", () => {
  const etichette = (item, opzioni = SOTTOSCRITTORI) => rigaCliente(item, opzioni).campi.verifiche.map((i) => i.etichetta);
  assert.deepEqual(etichette(STATO_PIENO), ["Email verificata", "Cellulare verificato", "Dati diploma completi"]);
  assert.deepEqual(etichette({}), ["Email non verificata", "Cellulare non verificato", "Dati diploma incompleti"]);
  assert.deepEqual(etichette({ email_verificata: false, cellulare_verificato: true }, ATTUATORI),
    ["Email non verificata", "Cellulare verificato"]);
});

test("verifiche cliente: la colonna esiste su desktop e su mobile, con le etichette e non con il badge", () => {
  for (const opzioni of [ATTUATORI, SOTTOSCRITTORI, { attuatori: true, mostraAzienda: true }]) {
    const modello = modelloClienti(opzioni);
    const desktop = modello.colonne.flatMap((c) => c.campi).filter((campo) => campo.id === "verifiche");
    const mobile = modello.mobile.filter((campo) => campo.id === "verifiche");
    assert.equal(desktop.length, 1);
    assert.equal(mobile.length, 1);
    assert.equal(desktop[0].rilievo, "indicatori");
    assert.equal(mobile[0].rilievo, "indicatori");
    // Nominativo per primo, verifiche per ultime, come nel design.
    const colonne = modello.colonne.map((c) => c.id);
    assert.equal(colonne[0], "nominativo");
    assert.equal(colonne.at(-1), "verifiche");
    assert.equal(modello.colonne[0].campi[0].rilievo, "persona");
    assert.equal(modello.mobile[1].id, "verifiche");
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

test("verifiche: ogni etichetta ha il testo visibile della propria voce", () => {
  const voci = (opzioni) => rigaCliente(STATO_PIENO, opzioni).campi.verifiche.map((i) => i.voce);
  assert.deepEqual(voci(ATTUATORI), ["Email", "Cellulare"]);
  assert.deepEqual(voci(SOTTOSCRITTORI), ["Email", "Cellulare", "Diploma"]);
});

test("descrizione accessibile: solo le righe con pallini la ricevono, con id distinti per vista e per riga", () => {
  const modello = modelloClienti(SOTTOSCRITTORI);
  const desktop = campoIndicatori(modello.colonne.flatMap((c) => c.campi));
  const mobile = campoIndicatori(modello.mobile);
  assert.equal(desktop.id, "verifiche");
  assert.equal(mobile.id, "verifiche");
  const prima = rigaCliente({ cliente_id: 1 }, SOTTOSCRITTORI);
  const seconda = rigaCliente({ cliente_id: 2 }, SOTTOSCRITTORI);
  assert.notEqual(idIndicatori(":a:", prima, desktop), idIndicatori(":b:", prima, mobile));
  assert.notEqual(idIndicatori(":a:", prima, desktop), idIndicatori(":a:", seconda, desktop));
  assert.equal(idIndicatori(":a:", { id: 3, campi: { verifiche: [] } }, desktop), undefined);
  // Gli altri elenchi non hanno pallini: nessun aria-describedby.
  for (const altro of [MODELLO_AZIENDE, MODELLO_PRATICHE, MODELLO_PRODOTTI]) {
    const campo = campoIndicatori([...altro.mobile, ...altro.colonne.flatMap((c) => c.campi)]);
    assert.equal(campo, undefined);
    assert.equal(idIndicatori(":a:", rigaPratica({ pratica_id: 4 }), campo), undefined);
  }
});

const NAZIONALE = { attuatori: true, mostraAzienda: true };

test("clienti: il nome e l'azienda si fermano a due righe, l'azienda come testo secondario solo dove si vede", () => {
  for (const opzioni of [NAZIONALE, ATTUATORI, SOTTOSCRITTORI]) {
    const modello = modelloClienti(opzioni);
    const campi = [...modello.mobile, ...modello.colonne.flatMap((c) => c.campi)];
    for (const campo of campi.filter((c) => c.id === "nominativo")) assert.equal(campo.righe, 2);
    const aziende = campi.filter((c) => c.id === "azienda");
    assert.equal(aziende.length, opzioni.mostraAzienda ? 2 : 0);
    for (const campo of aziende) {
      assert.equal(campo.rilievo, "secondario");
      assert.equal(campo.righe, 2);
    }
  }
  // L'elenco delle Aziende non cambia: la ragione sociale resta il campo principale.
  const ragioneSociale = MODELLO_AZIENDE.colonne[0].campi[0];
  assert.equal(ragioneSociale.rilievo, "principale");
  assert.equal(ragioneSociale.righe, undefined);
});

test("filtro Ruolo degli Attuatori: i valori dell'API, più la voce senza filtro nei testi", () => {
  assert.deepEqual(RUOLI_FILTRO, ["Aderente", "Provinciale", "Regionale", "Nazionale", "Operatore"]);
  assert.equal(TESTI_ELENCO.tuttiRuoli, "Tutti i ruoli");
  for (const elenco of ["attuatori", "sottoscrittori"]) {
    for (const chiave of ["titolo", "nuovo", "nuovoEsteso", "segnaposto", "vuoto"]) {
      assert.ok(TESTI_ELENCO.clienti[elenco][chiave], `${elenco}.${chiave} assente`);
    }
  }
});

// Proporzioni delle colonne dei clienti. Il design dispone ogni riga su una
// griglia (padding 0 24, gap 16, chevron 24px); l'app usa una <table> a layout
// fisso, con le larghezze delle <col> in percentuale in righeElenco.css. Qui si
// ricavano le percentuali dalla griglia del design, sulla tabella da 1118px
// (card da 1120 meno i bordi), e si confrontano con il foglio di stile.
const GRIGLIE_DESIGN = [
  { opzioni: NAZIONALE, fr: [2.4, 0.9, 2, 1.5] },
  { opzioni: ATTUATORI, fr: [2.4, 0.9, 1.5] },
  { opzioni: SOTTOSCRITTORI, fr: [2, 1.3] },
];
const TABELLA = 1118;
const [BORDO, SPAZIO, CHEVRON] = [24, 16, 24];

function larghezzeDesign(fr) {
  const tracce = fr.length + 1;
  const unita = (TABELLA - 2 * BORDO - SPAZIO * (tracce - 1) - CHEVRON) / fr.reduce((a, b) => a + b);
  // Nella tabella ogni cella ha 8px per lato (16 fra due celle) e 24 ai bordi.
  return fr.map((valore) => valore * unita + SPAZIO);
}

// Regole `.elenco-adattivo[data-modello="clienti"]<condizioni> col[data-colonna="x"] { width: … }`.
const foglio = readFileSync(new URL("../src/config/styles/righeElenco.css", import.meta.url), "utf8");
const regole = [...foglio.matchAll(
  /^\.elenco-adattivo\[data-modello="clienti"\](\S*) col\[data-colonna="(\w+)"\] \{ width: ([\d.]+)(%|rem); \}$/gm,
)].map(([, condizioni, colonna, valore, unita]) => ({
  condizioni: [...condizioni.matchAll(/:(not\(:)?has\(col\[data-colonna="(\w+)"\]\)/g)]
    .map(([, negata, id]) => ({ negata: Boolean(negata), id })),
  colonna,
  larghezza: unita === "rem" ? Number(valore) * 16 : (Number(valore) / 100) * TABELLA,
}));

test("clienti: le larghezze delle colonne riproducono le proporzioni della griglia del design", () => {
  assert.ok(regole.length >= 7, "regole delle colonne dei clienti non trovate in righeElenco.css");
  for (const { opzioni, fr } of GRIGLIE_DESIGN) {
    const colonne = modelloClienti(opzioni).colonne.map((c) => c.id);
    assert.equal(colonne.length, fr.length, `${colonne}: una proporzione per colonna`);
    const valide = regole.filter((regola) =>
      regola.condizioni.every(({ negata, id }) => colonne.includes(id) !== negata));
    const larghezza = (id) => {
      const trovate = valide.filter((regola) => regola.colonna === id);
      assert.equal(trovate.length, 1, `${colonne}: una sola larghezza per ${id}`);
      return trovate[0].larghezza;
    };
    // Il chevron: 24 della griglia, 8 di rientro e 24 di bordo.
    assert.equal(larghezza("azioni"), CHEVRON + 8 + BORDO);
    const attese = larghezzeDesign(fr);
    colonne.slice(1).forEach((id, indice) => {
      assert.ok(Math.abs(larghezza(id) - attese[indice + 1]) < 0.01, `${id}: ${larghezza(id)} invece di ${attese[indice + 1]}`);
    });
    // La prima colonna prende il resto: 24 di bordo a sinistra invece di 8.
    const resto = TABELLA - larghezza("azioni") - colonne.slice(1).reduce((somma, id) => somma + larghezza(id), 0);
    const primaAttesa = attese[0] + BORDO - 8;
    assert.ok(Math.abs(resto - primaAttesa) < 0.05, `${colonne[0]}: ${resto} invece di ${primaAttesa}`);
  }
});
