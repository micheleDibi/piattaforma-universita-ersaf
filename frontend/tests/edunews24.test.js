import { test } from "node:test";
import assert from "node:assert/strict";
import process from "node:process";
import { existsSync, readFileSync } from "node:fs";
import {
  AREE_EDUNEWS24,
  FILTRI_PER_SEZIONE,
  PENDENZA_BORDATO,
  PENDENZA_PIENO,
  PERCORSO_SEGNAPOSTO,
  REGIONI_EDUNEWS24,
  RETI_SOCIALI,
  SEZIONI_EDUNEWS24,
  SOCIAL_EDUNEWS24,
  TIPI_VOCE,
} from "../src/config/edunews24.js";
import { TESTI_EDUNEWS24 as testi } from "../src/config/testi/edunews24.js";
import { TESTI_DASHBOARD } from "../src/config/testi/dashboard.js";
import { QUERY_EDUNEWS24 } from "../src/config/routes/query.js";
import { aggiornaQuery, leggiQuery } from "../src/lib/queryPagina.js";
import {
  annuncioEsitoModulo,
  azzeramentoFiltri,
  bandeGriglia,
  chiaveVoce,
  conCursore,
  copertinaVideo,
  dataVoce,
  deduplicaVoci,
  descriviArea,
  descriviAggiornamento,
  descriviDurata,
  erroreEduNews24,
  etichettaGiorno,
  filtriAmmessi,
  filtriAttivi,
  formaVocePagina,
  formattaData,
  formattaDurata,
  formattaGiorno,
  formattaOra,
  giorniAllaScadenza,
  giornoRoma,
  immagineUtilizzabile,
  leggiRispostaCategorie,
  leggiRispostaElenco,
  messaggioErroreAltre,
  messaggioErrorePagina,
  modificheCambioScheda,
  motivoRipiego,
  nomeGuardaVideo,
  notaRiprova,
  numeroGiorno,
  osservaAltezzaFiltri,
  partiGiorno,
  percorsoCategorie,
  percorsoPaginaEduNews24,
  percorsoSezione,
  raggruppaPerGiorno,
  statoOpportunita,
  testiVuotoPagina,
  testoArea,
  testoAreaAccessibile,
  titoloModulo,
  tonoTarga,
  urlHttps,
  varianteRipiego,
  vociModulo,
  voceChiusaOScaduta,
  voceInEvidenza,
} from "../src/lib/edunews24.js";

const SITO = "https://edunews24.invalid";
const MEDIA = "https://media.edunews24.invalid";
const ms = (iso) => Date.parse(iso);

const notizia = (id, extra = {}) => ({
  tipo: "notizia", id, titolo: `Titolo della notizia ${id}`, titolo_breve: null, sintesi: null,
  url: `${SITO}/articoli/${id}`, pubblicato_il: "2026-09-28T08:00:00+02:00",
  categoria: { slug: "scuola", nome: "Scuola" }, immagine: null, video: null, ha_video: false, ...extra,
});
const selezione = (id, extra = {}) => ({
  tipo: "selezione-personale", id, titolo: `Selezione ${id}`, sintesi: null, url: `${SITO}/selezione/${id}`,
  ente: "Comune di Esempio", sede: null, regioni: [], nazionale: false, pubblicato_il: "2026-09-28T08:00:00+02:00",
  scadenza: null, stato: null, classe_concorso: null, figura: null, posti: null, ...extra,
});
const interpello = (id, extra = {}) => ({ ...selezione(id), tipo: "interpello", titolo: `Interpello ${id}`, ...extra });
const regioni = (...slug) => slug.map((s) => ({ slug: s, nome: REGIONI_EDUNEWS24.find((r) => r.slug === s)?.nome ?? s }));

// --- date di Roma e cambi d'ora -------------------------------------------------

// Ottobre 2026: si torna all'ora solare il 25; marzo 2027: all'ora legale il 28.
// Alle 23:30 e alle 00:30 di Roma il giorno cambia ma l'UTC no, o viceversa.
const CAMBI_ORA = [
  // adesso (UTC), giorno e ora di Roma, scadenza (e giorno di pubblicazione), stato atteso,
  // data della voce pubblicata quel giorno, intestazione del gruppo di quel giorno
  ["2026-10-24T21:30:00Z", "2026-10-24", "23:30", "2026-10-25", "scade-domani", "25/10/2026", "Domenica 25 ottobre"],
  ["2026-10-24T22:30:00Z", "2026-10-25", "00:30", "2026-10-25", "scade-oggi", "Oggi", "Oggi"],
  ["2026-10-25T22:30:00Z", "2026-10-25", "23:30", "2026-10-25", "scade-oggi", "Oggi", "Oggi"],
  ["2026-10-25T23:30:00Z", "2026-10-26", "00:30", "2026-10-25", "scaduto", "Ieri", "Ieri"],
  ["2027-03-27T22:30:00Z", "2027-03-27", "23:30", "2027-03-28", "scade-domani", "28/03/2027", "Domenica 28 marzo"],
  ["2027-03-27T23:30:00Z", "2027-03-28", "00:30", "2027-03-28", "scade-oggi", "Oggi", "Oggi"],
  ["2027-03-28T21:30:00Z", "2027-03-28", "23:30", "2027-03-28", "scade-oggi", "Oggi", "Oggi"],
  ["2027-03-28T22:30:00Z", "2027-03-29", "00:30", "2027-03-28", "scaduto", "Ieri", "Ieri"],
];

function verificaCambiOra(fuso) {
  for (const [adesso, giorno, ora, scadenza, chiave, data, etichetta] of CAMBI_ORA) {
    const contesto = `${adesso} con TZ=${fuso}`;
    assert.equal(giornoRoma(adesso), giorno, contesto);
    assert.equal(giornoRoma(ms(adesso)), giorno, contesto);
    assert.equal(formattaOra(adesso), ora, contesto);
    assert.equal(formattaData(adesso), formattaGiorno(giorno), contesto);
    const voce = selezione(1, { stato: "aperto", scadenza });
    assert.equal(statoOpportunita(voce, ms(adesso)).chiave, chiave, contesto);
    const pubblicata = { pubblicato_il: `${scadenza}T10:00:00${scadenza.startsWith("2026") ? "+01:00" : "+02:00"}` };
    assert.equal(dataVoce(pubblicata, ms(adesso)).testo, data, contesto);
    assert.equal(etichettaGiorno(scadenza, giornoRoma(adesso)), etichetta, contesto);
  }
  // Una voce pubblicata alle 23:00 di Roma del 24 e' "Ieri" alle 00:30 del 25.
  assert.equal(dataVoce({ pubblicato_il: "2026-10-24T21:00:00Z" }, ms("2026-10-24T22:30:00Z")).testo, "Ieri");
  assert.equal(formattaData("2026-10-24T22:30:00Z"), "25/10/2026");
}

test("scadenze, Oggi, Ieri e date seguono il giorno di Roma ai cambi d'ora", () => {
  verificaCambiOra(process.env.TZ ?? "locale");
});

test("le date restano quelle di Roma con ogni fuso del dispositivo", () => {
  const originale = process.env.TZ;
  try {
    for (const fuso of ["UTC", "America/Los_Angeles", "Pacific/Kiritimati"]) {
      process.env.TZ = fuso;
      verificaCambiOra(fuso);
    }
  } finally {
    if (originale === undefined) delete process.env.TZ;
    else process.env.TZ = originale;
  }
});

test("numeroGiorno rifiuta date inesistenti o fuori forma", () => {
  for (const valore of ["2026-02-30", "2026-9-1", "2026-13-01", "26-09-01", "", null, undefined, 20260901, "2026-09-01T00:00:00Z"]) {
    assert.equal(numeroGiorno(valore), null, String(valore));
  }
  assert.equal(numeroGiorno("2026-09-29") - numeroGiorno("2026-09-28"), 1);
  assert.equal(numeroGiorno("2028-02-29") - numeroGiorno("2028-02-28"), 1);
  assert.equal(giorniAllaScadenza("2026-10-05", ms("2026-09-28T10:00:00Z")), 7);
  assert.equal(giorniAllaScadenza("non-una-data", ms("2026-09-28T10:00:00Z")), null);
  assert.equal(giornoRoma("ieri"), null);
  assert.equal(formattaOra(null), null);
});

test("etichettaGiorno: Oggi, Ieri, giorno della settimana e anno solo se diverso", () => {
  assert.equal(etichettaGiorno("2026-09-28", "2026-09-28"), "Oggi");
  assert.equal(etichettaGiorno("2026-09-27", "2026-09-28"), "Ieri");
  assert.equal(etichettaGiorno("2026-09-25", "2026-09-28"), "Venerdì 25 settembre");
  assert.equal(etichettaGiorno("2025-12-31", "2026-01-01"), "Ieri");
  assert.equal(etichettaGiorno("2025-12-30", "2026-01-01"), "Martedì 30 dicembre 2025");
  // Un giorno futuro non e' mai "Domani": e' una data.
  assert.equal(etichettaGiorno("2026-09-29", "2026-09-28"), "Martedì 29 settembre");
  assert.equal(etichettaGiorno(null, "2026-09-28"), "Senza data");
  assert.equal(dataVoce({ pubblicato_il: "2026-09-29T10:00:00+02:00" }, ms("2026-09-28T10:00:00Z")).testo, "29/09/2026");
  assert.equal(dataVoce({ pubblicato_il: "non valida" }, ms("2026-09-28T10:00:00Z")), null);
  assert.deepEqual(partiGiorno("2026-10-15"), {
    giorno: "15", mese: "ott", meseEsteso: "ottobre", anno: "2026", estesoSenzaAnno: "15 ottobre", esteso: "15 ottobre 2026",
  });
  assert.equal(partiGiorno("2026-02-30"), null);
});

test("il folio dice l'ora dell'aggiornamento, o da quando la copia non e' aggiornata", () => {
  const adesso = ms("2026-09-28T09:00:00Z");
  assert.deepEqual(descriviAggiornamento("2026-09-28T08:32:00Z", false, adesso),
    { iso: "2026-09-28T08:32:00.000Z", testo: "Aggiornato alle 10:32", esteso: null });
  assert.deepEqual(descriviAggiornamento("2026-09-28T08:32:00.123456Z", true, adesso), {
    iso: "2026-09-28T08:32:00.123Z", testo: "Non aggiornato dalle 10:32", esteso: testi.stantioEsteso,
  });
  assert.equal(descriviAggiornamento("2026-09-27T16:40:00Z", true, adesso).testo, "Non aggiornato dal 27/09 alle 18:40");
  assert.equal(descriviAggiornamento("2026-09-27T16:40:00Z", false, adesso).testo, "Aggiornato il 27/09 alle 18:40");
  assert.equal(descriviAggiornamento("2025-12-31T22:30:00Z", true, ms("2026-01-01T08:00:00Z")).testo,
    "Non aggiornato dal 31/12/2025 alle 23:30");
  assert.deepEqual(descriviAggiornamento(null, true, adesso), { iso: null, testo: "Contenuti non aggiornati", esteso: testi.stantioEsteso });
  assert.equal(descriviAggiornamento(null, false, adesso), null);
  // Primo caricamento fallito senza copia: il folio non resta vuoto, senza
  // frase estesa (spiega l'avviso d'errore).
  assert.deepEqual(descriviAggiornamento(null, false, adesso, true), { iso: null, testo: "Contenuti non aggiornati", esteso: null });
  // Con un istante noto l'errore non cambia nulla.
  assert.equal(descriviAggiornamento("2026-09-28T08:32:00Z", false, adesso, true).testo, "Aggiornato alle 10:32");
});

// --- stato della selezione -------------------------------------------------------

test("statoOpportunita copre ogni ramo, con la soglia di attenzione a 7 giorni", () => {
  const adesso = ms("2026-09-28T10:00:00Z");
  const stato = (extra) => statoOpportunita(selezione(1, extra), adesso);
  assert.equal(stato({ stato: "aperto", scadenza: "2026-09-27" }).chiave, "scaduto");
  assert.equal(stato({ stato: "aperto", scadenza: "2026-09-27" }).tono, "neutro");
  assert.equal(stato({ stato: "chiuso", scadenza: "2026-09-20" }).chiave, "scaduto");
  assert.equal(stato({ stato: null, scadenza: "2026-09-20" }).chiave, "scaduto");
  assert.deepEqual(stato({ stato: "chiuso", scadenza: "2026-10-20" }), { chiave: "chiuso", testo: "Chiuso", tono: "neutro", giorni: 22 });
  assert.equal(stato({ stato: "chiuso" }).chiave, "chiuso");
  assert.deepEqual(stato({ stato: "aperto", scadenza: "2026-09-28" }), { chiave: "scade-oggi", testo: "Scade oggi", tono: "attenzione", giorni: 0 });
  assert.deepEqual(stato({ stato: "aperto", scadenza: "2026-09-29" }), { chiave: "scade-domani", testo: "Scade domani", tono: "attenzione", giorni: 1 });
  assert.deepEqual(stato({ stato: "aperto", scadenza: "2026-10-05" }), { chiave: "scade-tra", testo: "Scade tra 7 giorni", tono: "attenzione", giorni: 7 });
  assert.deepEqual(stato({ stato: "aperto", scadenza: "2026-10-06" }), { chiave: "scade-tra", testo: "Scade tra 8 giorni", tono: "aperto", giorni: 8 });
  assert.deepEqual(stato({ stato: "aperto", scadenza: null }), { chiave: "aperto", testo: "Aperto", tono: "aperto", giorni: null });
  assert.equal(stato({ stato: "altro", scadenza: "2026-10-06" }), null);
  assert.equal(stato({ stato: null, scadenza: "2026-10-06" }), null);
  assert.equal(stato({ stato: null, scadenza: null }), null);
  assert.equal(statoOpportunita(interpello(2, { stato: "aperto", scadenza: "2026-09-20" }), adesso), null);
  assert.equal(statoOpportunita(notizia(3), adesso), null);
  assert.equal(tonoTarga(stato({ stato: "aperto", scadenza: "2026-09-29" })), "attenzione");
  assert.equal(tonoTarga(stato({ stato: "chiuso" })), "neutro");
  assert.equal(tonoTarga(stato({ stato: "aperto", scadenza: "2026-10-20" })), "normale");
  assert.equal(tonoTarga(null), "normale");
  assert.equal(voceChiusaOScaduta(selezione(1, { stato: "chiuso" }), adesso), true);
  assert.equal(voceChiusaOScaduta(selezione(1, { stato: "aperto", scadenza: "2026-09-27" }), adesso), true);
  assert.equal(voceChiusaOScaduta(selezione(1, { stato: null, scadenza: null }), adesso), false);
});

// --- aree e gruppi --------------------------------------------------------------

test("descriviArea e testoArea: nazionale, poche e molte regioni, slug ignoti", () => {
  assert.deepEqual(descriviArea(selezione(1, { nazionale: true, regioni: regioni("lazio") }), 3),
    { nazionale: true, visibili: ["Nazionale"], altre: [], tutte: ["Nazionale"] });
  const due = descriviArea(selezione(1, { regioni: regioni("lombardia", "veneto") }), 3);
  assert.equal(testoArea(due), "Lombardia, Veneto");
  assert.equal(testoAreaAccessibile(due), "Lombardia, Veneto");
  const cinque = selezione(1, { regioni: regioni("lombardia", "veneto", "lazio", "liguria", "piemonte") });
  assert.equal(testoArea(descriviArea(cinque, 3)), "Lombardia, Veneto, Lazio +2");
  assert.equal(testoAreaAccessibile(descriviArea(cinque, 3)), "Lombardia, Veneto, Lazio e altre 2: Liguria, Piemonte");
  assert.equal(testoArea(descriviArea(cinque, 2)), "Lombardia, Veneto +3");
  assert.deepEqual(descriviArea(cinque, 2).tutte, ["Lombardia", "Veneto", "Lazio", "Liguria", "Piemonte"]);
  const ignoto = selezione(1, { regioni: [{ slug: "atlantide", nome: "Atlantide" }, ...regioni("lazio", "lazio")] });
  assert.deepEqual(descriviArea(ignoto, 3).tutte, ["Lazio"]);
  assert.equal(descriviArea(selezione(1, { regioni: [] }), 3), null);
  assert.equal(descriviArea(selezione(1, { regioni: [{ slug: "atlantide", nome: "Atlantide" }] }), 3), null);
  assert.equal(testoArea(null), "");
  assert.throws(() => descriviArea(cinque, 0), TypeError);
});

test("raggruppaPerGiorno continua i gruppi dopo Carica altri senza ripetere le intestazioni", () => {
  const adesso = ms("2026-09-28T10:00:00Z");
  const prima = [
    selezione(1, { pubblicato_il: "2026-09-28T10:00:00+02:00" }),
    selezione(2, { pubblicato_il: "2026-09-28T08:00:00+02:00" }),
    selezione(3, { pubblicato_il: "2026-09-27T18:00:00+02:00" }),
    selezione(4, { pubblicato_il: "non valida" }),
  ];
  const seconda = [
    selezione(5, { pubblicato_il: "2026-09-27T09:00:00+02:00" }),
    selezione(6, { pubblicato_il: "2026-09-25T09:00:00+02:00" }),
    selezione(7, { pubblicato_il: null }),
  ];
  const solo = raggruppaPerGiorno(prima, adesso);
  assert.deepEqual(solo.map((g) => [g.giorno, g.etichetta, g.voci.map((v) => v.id)]), [
    ["2026-09-28", "Oggi", [1, 2]], ["2026-09-27", "Ieri", [3]], [null, "Senza data", [4]],
  ]);
  const tutte = raggruppaPerGiorno([...prima, ...seconda], adesso);
  assert.deepEqual(tutte.map((g) => [g.etichetta, g.dataEstesa, g.voci.map((v) => v.id)]), [
    ["Oggi", "28 settembre", [1, 2]],
    ["Ieri", "27 settembre", [3, 5]],
    ["Venerdì 25 settembre", null, [6]],
    ["Senza data", null, [4, 7]],
  ]);
  assert.equal(new Set(tutte.map((g) => g.etichetta)).size, tutte.length);
});

// --- query e filtri della pagina -----------------------------------------------

test("QUERY_EDUNEWS24 accetta solo schede, aree, categorie e video validi", () => {
  const leggi = (search) => leggiQuery(search, QUERY_EDUNEWS24);
  assert.deepEqual(leggi(""), { scheda: "notizie", area: "", categoria: "", video: "" });
  assert.equal(leggi("?scheda=bandi").scheda, "notizie");
  assert.equal(leggi("?scheda=selezione-personale").scheda, "selezione-personale");
  assert.equal(leggi("?categoria=Scuola").categoria, "");
  assert.equal(leggi(`?categoria=${"a".repeat(65)}`).categoria, "");
  assert.equal(leggi(`?categoria=${"a".repeat(64)}`).categoria, "a".repeat(64));
  assert.equal(leggi("?categoria=scuola&categoria=universita").categoria, "scuola");
  assert.equal(leggi("?categoria=scuola--media").categoria, "");
  assert.equal(leggi("?video=true").video, "");
  assert.equal(leggi("?video=1").video, "1");
  assert.equal(leggi("?area=milano").area, "");
  assert.equal(leggi("?area=lombardia").area, "lombardia");
  assert.equal(leggi("?area=nazionale").area, "nazionale");
});

test("filtriAmmessi azzera i filtri che la scheda non ammette", () => {
  const valori = { categoria: "scuola", video: "1", area: "nazionale" };
  assert.deepEqual(filtriAmmessi("notizie", valori), { categoria: "scuola", video: "1", area: "" });
  assert.deepEqual(filtriAmmessi("interpelli", valori), { categoria: "", video: "", area: "" });
  assert.deepEqual(filtriAmmessi("interpelli", { area: "lazio" }), { categoria: "", video: "", area: "lazio" });
  assert.deepEqual(filtriAmmessi("selezione-personale", valori), { categoria: "", video: "", area: "nazionale" });
  assert.deepEqual(filtriAmmessi("bandi", valori), azzeramentoFiltri());
  assert.deepEqual(filtriAmmessi("notizie", { categoria: "Scuola", video: "si" }), azzeramentoFiltri());
});

test("il cambio di scheda toglie i filtri non ammessi e conserva l'area fra le opportunita'", () => {
  const cambia = (search, a) => {
    const valori = leggiQuery(search, QUERY_EDUNEWS24);
    return aggiornaQuery(search, modificheCambioScheda(valori.scheda, a, valori), QUERY_EDUNEWS24);
  };
  assert.equal(cambia("?categoria=scuola&video=1", "interpelli"), "?scheda=interpelli");
  assert.equal(cambia("?scheda=selezione-personale&area=nazionale", "interpelli"), "?scheda=interpelli");
  assert.equal(cambia("?scheda=selezione-personale&area=lombardia", "interpelli"), "?scheda=interpelli&area=lombardia");
  assert.equal(cambia("?scheda=interpelli&area=lombardia", "notizie"), "");
  assert.deepEqual(Object.keys(modificheCambioScheda("notizie", "interpelli", {})).sort(), ["area", "categoria", "scheda", "video"]);
});

test("altezza della barra dei filtri sulla radice, tolta alla pulizia", () => {
  const proprieta = new Map();
  const radice = {
    style: {
      setProperty: (nome, valore) => proprieta.set(nome, valore),
      removeProperty: (nome) => proprieta.delete(nome),
    },
  };
  let altezza = 116.4;
  const barra = { getBoundingClientRect: () => ({ height: altezza }) };
  const osservatori = [];
  const originale = globalThis.ResizeObserver;
  globalThis.ResizeObserver = class {
    constructor(richiamo) {
      this.richiamo = richiamo;
      this.osservati = [];
      this.chiuso = false;
      osservatori.push(this);
    }
    observe(elemento) { this.osservati.push(elemento); }
    disconnect() { this.chiuso = true; }
  };
  try {
    const pulizia = osservaAltezzaFiltri(barra, radice);
    // Misura subito, arrotondata per eccesso, e segue i cambi d'altezza.
    assert.equal(proprieta.get("--edunews24-altezza-filtri"), "117px");
    assert.deepEqual(osservatori[0].osservati, [barra]);
    altezza = 167;
    osservatori[0].richiamo();
    assert.equal(proprieta.get("--edunews24-altezza-filtri"), "167px");
    pulizia();
    assert.equal(osservatori[0].chiuso, true);
    assert.equal(proprieta.has("--edunews24-altezza-filtri"), false);
  } finally {
    if (originale === undefined) delete globalThis.ResizeObserver;
    else globalThis.ResizeObserver = originale;
  }
  // Senza barra, senza radice o senza ResizeObserver non fa nulla.
  assert.doesNotThrow(() => osservaAltezzaFiltri(null, radice)());
  assert.doesNotThrow(() => osservaAltezzaFiltri(barra, null)());
});

test("filtri attivi, stato vuoto e percorso della pagina per scheda", () => {
  const categorie = [{ slug: "scuola", nome: "Scuola" }];
  assert.deepEqual(filtriAttivi("notizie", { categoria: "scuola", video: "1" }, categorie), [
    { chiave: "categoria", etichetta: "Categoria: Scuola", nome: "Rimuovi il filtro Categoria: Scuola" },
    { chiave: "video", etichetta: "Solo video", nome: "Rimuovi il filtro Solo video" },
  ]);
  assert.equal(filtriAttivi("notizie", { categoria: "concorsi" }, categorie)[0].etichetta, "Categoria: concorsi");
  assert.deepEqual(filtriAttivi("selezione-personale", { area: "nazionale" }).map((f) => f.etichetta), ["Area: Nazionale"]);
  assert.deepEqual(filtriAttivi("interpelli", { area: "nazionale" }), []);

  assert.deepEqual(testiVuotoPagina("notizie", {}), {
    titolo: "Nessuna notizia da mostrare per ora.", riga: "Le nuove notizie compariranno qui.", rimuovi: null,
  });
  assert.deepEqual(testiVuotoPagina("notizie", { categoria: "scuola" }), {
    titolo: "Nessuna notizia per questi filtri.", riga: "Prova un'altra categoria o rimuovi il filtro.", rimuovi: "Rimuovi il filtro",
  });
  assert.deepEqual(testiVuotoPagina("notizie", { categoria: "scuola", video: "1" }), {
    titolo: "Nessuna notizia per questi filtri.", riga: "Prova un'altra categoria o rimuovi i filtri.", rimuovi: "Rimuovi i filtri",
  });
  assert.deepEqual(testiVuotoPagina("interpelli", {}), { titolo: "Nessun interpello da mostrare per ora.", riga: null, rimuovi: null });
  assert.equal(testiVuotoPagina("interpelli", { area: "lombardia" }).titolo, "Nessun interpello in Lombardia.");
  assert.equal(testiVuotoPagina("interpelli", { area: "nazionale" }).rimuovi, null);
  assert.equal(testiVuotoPagina("selezione-personale", { area: "nazionale" }).titolo, "Nessuna selezione nazionale.");
  assert.equal(testiVuotoPagina("selezione-personale", { area: "valle-d-aosta" }).titolo, "Nessuna selezione in Valle d'Aosta.");

  assert.equal(percorsoPaginaEduNews24("notizie"), "/edunews24");
  assert.equal(percorsoPaginaEduNews24("interpelli"), "/edunews24?scheda=interpelli");
  assert.equal(percorsoPaginaEduNews24("selezione-personale"), "/edunews24?scheda=selezione-personale");
  assert.throws(() => percorsoPaginaEduNews24("bandi"), TypeError);
});

// --- percorsi dell'API ed errori ---------------------------------------------------

test("percorsoSezione ha un ordine fisso e manda solo_video=si", () => {
  assert.equal(percorsoSezione("notizie"), "/edunews24/notizie");
  assert.equal(percorsoSezione("notizie", { video: "1", categoria: "scuola" }), "/edunews24/notizie?categoria=scuola&solo_video=si");
  assert.equal(percorsoSezione("notizie", { area: "lazio" }), "/edunews24/notizie");
  assert.equal(percorsoSezione("interpelli", { area: "lazio", categoria: "scuola" }), "/edunews24/interpelli?area=lazio");
  assert.equal(percorsoSezione("interpelli", { area: "nazionale" }), "/edunews24/interpelli");
  assert.equal(percorsoSezione("selezione-personale", { area: "nazionale" }), "/edunews24/selezione-personale?area=nazionale");
  for (const sezione of ["bandi", "", undefined, "toString", "__proto__"]) {
    assert.throws(() => percorsoSezione(sezione), TypeError, String(sezione));
  }
  assert.equal(percorsoCategorie(), "/edunews24/categorie");
  assert.equal(conCursore("/edunews24/notizie", "m20-abcdef12"), "/edunews24/notizie?cursore=m20-abcdef12");
  assert.equal(conCursore("/edunews24/notizie?categoria=scuola", "abc_DEF-1"), "/edunews24/notizie?categoria=scuola&cursore=abc_DEF-1");
  for (const cursore of [null, "", "con spazio", "a&b=c", "x".repeat(301), 42]) {
    assert.equal(conCursore("/edunews24/notizie", cursore), "/edunews24/notizie", String(cursore));
  }
});

test("erroreEduNews24 da' tipo e secondi di attesa, mai un testo", () => {
  assert.deepEqual(erroreEduNews24(400), { tipo: "richiesta", attesaSecondi: 0 });
  assert.deepEqual(erroreEduNews24(422), { tipo: "richiesta", attesaSecondi: 0 });
  assert.deepEqual(erroreEduNews24(409), { tipo: "cursore", attesaSecondi: 0 });
  assert.deepEqual(erroreEduNews24(429, "12"), { tipo: "servizio", attesaSecondi: 12 });
  assert.deepEqual(erroreEduNews24(500, null), { tipo: "servizio", attesaSecondi: 0 });
  assert.deepEqual(erroreEduNews24(503, "30"), { tipo: "servizio", attesaSecondi: 30 });
  assert.deepEqual(erroreEduNews24(503, null), { tipo: "servizio", attesaSecondi: 0 });
  assert.deepEqual(erroreEduNews24(503, new Date(Date.now() + 10 * 86_400_000).toUTCString()), { tipo: "servizio", attesaSecondi: 3600 });
  // secondiAttesa("0") vale 1: un Retry-After a zero non sblocca subito.
  assert.deepEqual(erroreEduNews24(503, "0"), { tipo: "servizio", attesaSecondi: 1 });
  assert.deepEqual(erroreEduNews24(0), { tipo: "rete", attesaSecondi: 0 });
  assert.deepEqual(erroreEduNews24(418), { tipo: "generico", attesaSecondi: 0 });
});

test("i testi d'errore si compongono secondo il contesto", () => {
  assert.equal(notaRiprova(30), "Puoi riprovare tra 30 secondi.");
  assert.equal(notaRiprova(1), "Puoi riprovare tra 1 secondo.");
  assert.equal(notaRiprova(0), "Puoi riprovare tra qualche istante.");
  // La pausa raddoppia fino a un'ora: dai 90 secondi l'attesa e' in minuti,
  // arrotondati per eccesso.
  assert.equal(notaRiprova(89), "Puoi riprovare tra 89 secondi.");
  assert.equal(notaRiprova(90), "Puoi riprovare tra 2 minuti.");
  assert.equal(notaRiprova(240), "Puoi riprovare tra 4 minuti.");
  assert.equal(notaRiprova(3600), "Puoi riprovare tra 60 minuti.");
  // Pagina: i secondi stanno nella nota accanto a "Riprova" finche' e'
  // bloccato; allo sblocco la nota sparisce e il testo dell'avviso non cambia.
  assert.deepEqual(messaggioErrorePagina("interpelli", 503, 30, true), {
    testo: "Interpelli non caricati: EduNews24 non risponde in questo momento.",
    azione: "riprova",
    nota: "Puoi riprovare tra 30 secondi.",
  });
  assert.deepEqual(messaggioErrorePagina("interpelli", 503, 30, false), {
    testo: "Interpelli non caricati: EduNews24 non risponde in questo momento.",
    azione: "riprova",
    nota: null,
  });
  assert.deepEqual(messaggioErrorePagina("notizie", 0), {
    testo: "Notizie non caricate: EduNews24 non risponde in questo momento.",
    azione: "riprova",
    nota: "Puoi riprovare tra qualche istante.",
  });
  assert.equal(messaggioErrorePagina("selezione-personale", 503, 5, true).testo,
    "Selezione del personale non caricata: EduNews24 non risponde in questo momento.");
  assert.equal(messaggioErrorePagina("selezione-personale", 503, 5, true).nota, "Puoi riprovare tra 5 secondi.");
  assert.equal(messaggioErrorePagina("notizie", 503, 1, true).nota, "Puoi riprovare tra 1 secondo.");
  for (const bloccato of [true, false]) {
    assert.doesNotMatch(messaggioErrorePagina("notizie", 503, 30, bloccato).testo, /secondi|istante/);
  }
  assert.deepEqual(messaggioErrorePagina("notizie", 400), { testo: "Questo filtro non è più disponibile.", azione: "rimuovi-filtri", nota: null });
  assert.deepEqual(messaggioErrorePagina("notizie", 422), { testo: "Questo filtro non è più disponibile.", azione: "rimuovi-filtri", nota: null });
  assert.deepEqual(messaggioErrorePagina("notizie", 409), { testo: testi.cursore, azione: "riprova", nota: null });
  assert.equal(messaggioErroreAltre(503), "Altre voci non caricate: EduNews24 non risponde.");
  assert.equal(messaggioErroreAltre(409), testi.cursore);
});

test("annuncioEsitoModulo dice l'esito di Riprova solo quando arriva", () => {
  assert.equal(annuncioEsitoModulo("pronto", "notizie"), "Elenco aggiornato");
  assert.equal(annuncioEsitoModulo("vuoto", "interpelli"), "Nessun interpello recente.");
  assert.equal(annuncioEsitoModulo("vuoto", "selezione-personale"), "Nessuna selezione aperta in questo momento.");
  assert.equal(annuncioEsitoModulo("vuoto", "sconosciuta"), testi.vuotiModulo.notizie.titolo);
  assert.equal(annuncioEsitoModulo("errore", "notizie"), "EduNews24 non risponde in questo momento.");
  assert.equal(annuncioEsitoModulo("scheletro", "notizie"), "");
  assert.equal(annuncioEsitoModulo("nascosto", "notizie"), "");
});

// --- voci -----------------------------------------------------------------------

test("deduplicaVoci, durate e URL", () => {
  const unite = deduplicaVoci([notizia(1), notizia(2)], [notizia(2), notizia(3), notizia(3), selezione(3)]);
  assert.deepEqual(unite.map(chiaveVoce), ["notizia:1", "notizia:2", "notizia:3", "selezione-personale:3"]);
  assert.equal(formattaDurata(65), "1:05");
  assert.equal(formattaDurata(5), "0:05");
  assert.equal(formattaDurata(3605), "1:00:05");
  for (const valore of [0, -3, 1.5, "65", null, true]) assert.equal(formattaDurata(valore), null, String(valore));
  assert.equal(descriviDurata(65), "durata 1 minuto e 5 secondi");
  assert.equal(descriviDurata(134), "durata 2 minuti e 14 secondi");
  assert.equal(descriviDurata(60), "durata 1 minuto");
  assert.equal(descriviDurata(1), "durata 1 secondo");
  assert.equal(descriviDurata(0), null);
  assert.equal(urlHttps("https://[x"), null);
  assert.equal(urlHttps("http://edunews24.invalid/a"), null);
  assert.equal(urlHttps("https://utente:segreto@edunews24.invalid/a"), null);
  assert.equal(urlHttps(`${SITO}/articoli/1`).hostname, "edunews24.invalid");
  assert.equal(immagineUtilizzabile(`${MEDIA}/foto.jpg`), true);
  assert.equal(immagineUtilizzabile(`${MEDIA}/edunews24_immagine_da_sostituire.png`), false);
  assert.equal(immagineUtilizzabile("https://terzi.example.org/edunews24_immagine_da_sostituire.png"), false);
  assert.equal(immagineUtilizzabile("javascript:alert(1)"), false);
  assert.equal(immagineUtilizzabile("/foto.jpg"), false);
  assert.equal(immagineUtilizzabile(null), false);
});

test("leggiRispostaElenco legge meta, scarta le voci non valide e azzera i media non utilizzabili", () => {
  assert.deepEqual(leggiRispostaElenco({ attiva: false, elementi: [], meta: null }),
    { attiva: false, elementi: [], cursore: null, stantio: false, aggiornatoIl: null });
  for (const dati of [null, "testo", {}, { attiva: "si", elementi: [] }, { attiva: true, elementi: {} }, { attiva: true }]) {
    assert.throws(() => leggiRispostaElenco(dati), TypeError, JSON.stringify(dati));
  }
  const video = { url: `${MEDIA}/video.mp4`, tipo_mime: "video/mp4", copertina: `${MEDIA}/edunews24_immagine_da_sostituire.png`, durata_secondi: 65 };
  const letta = leggiRispostaElenco({
    attiva: true,
    elementi: [
      notizia(1, { titolo_breve: "Breve", immagine: `${MEDIA}/foto.jpg`, video, ha_video: true }),
      notizia(2, { video: { ...video, tipo_mime: "video/quicktime" }, ha_video: true, immagine: `${MEDIA}/edunews24_immagine_da_sostituire.png` }),
      notizia(3, { video: { ...video, url: "http://media.edunews24.invalid/video.mp4" }, titolo_breve: "  ", immagine: "http://media.edunews24.invalid/foto.jpg" }),
      notizia(4, { video: { ...video, durata_secondi: 0 } }),
      notizia(0), notizia(5, { id: "5" }), notizia(6, { id: 6.5 }), notizia(7, { url: "http://edunews24.invalid/a" }),
      notizia(8, { url: "javascript:alert(1)" }), notizia(9, { titolo: "   " }), notizia(10, { tipo: "bando" }), null, "voce",
      notizia(1),
    ],
    meta: { cursore_successivo: "m20-abcdef12", aggiornato_il: "2026-09-28T16:06:12.740456Z", stantio: true },
  });
  assert.equal(letta.cursore, "m20-abcdef12");
  assert.equal(letta.aggiornatoIl, "2026-09-28T16:06:12.740456Z");
  assert.equal(letta.stantio, true);
  assert.deepEqual(letta.elementi.map((v) => v.id), [1, 2, 3, 4]);
  const [prima, seconda, terza, quarta] = letta.elementi;
  assert.equal(prima.titolo_breve, "Breve");
  assert.equal(prima.immagine, `${MEDIA}/foto.jpg`);
  assert.deepEqual(prima.video, { ...video, copertina: null });
  assert.equal(copertinaVideo(prima), `${MEDIA}/foto.jpg`);
  assert.equal(seconda.video, null);
  assert.equal(seconda.ha_video, true);
  assert.equal(seconda.immagine, null);
  assert.equal(terza.video, null);
  assert.equal(terza.ha_video, false);
  assert.equal(terza.titolo_breve, null);
  assert.equal(terza.immagine, null);
  assert.equal(quarta.video.durata_secondi, null);
  assert.equal(quarta.ha_video, true);

  for (const meta of [null, undefined, { cursore_successivo: "", stantio: "si", aggiornato_il: "ieri" }, { cursore_successivo: "con spazio" }]) {
    const senza = leggiRispostaElenco({ attiva: true, elementi: [], meta });
    assert.deepEqual([senza.cursore, senza.stantio, senza.aggiornatoIl], [null, false, null], JSON.stringify(meta));
  }
});

test("leggiRispostaElenco tiene i campi delle opportunita' solo per il loro tipo", () => {
  const { elementi } = leggiRispostaElenco({
    attiva: true,
    elementi: [
      interpello(1, { classe_concorso: "A022", figura: "Istruttore", posti: 3, sintesi: "Sintesi" }),
      selezione(2, {
        classe_concorso: "A022", figura: "Istruttore amministrativo", posti: 3, stato: "aperto", scadenza: "2026-10-15",
        regioni: [...regioni("lombardia"), { slug: 4 }, null], nazionale: "si",
      }),
      selezione(3, { posti: 0, stato: "upcoming", scadenza: "2026-02-30", ente: "", figura: "" }),
      selezione(4, { posti: true }),
    ],
    meta: null,
  });
  assert.deepEqual(elementi.map((v) => [v.classe_concorso, v.figura, v.posti]), [
    ["A022", null, null], [null, "Istruttore amministrativo", 3], [null, null, null], [null, null, null],
  ]);
  assert.equal(elementi[0].sintesi, "Sintesi");
  assert.deepEqual(elementi[1].regioni, [{ slug: "lombardia", nome: "Lombardia" }]);
  assert.equal(elementi[1].nazionale, false);
  assert.deepEqual([elementi[1].stato, elementi[1].scadenza], ["aperto", "2026-10-15"]);
  assert.deepEqual([elementi[2].stato, elementi[2].scadenza, elementi[2].ente], [null, null, null]);
});

test("leggiRispostaCategorie legge gli elementi con uno slug valido", () => {
  assert.deepEqual(leggiRispostaCategorie({
    attiva: true,
    elementi: [{ slug: "scuola", nome: "Scuola" }, { slug: "Non valida", nome: "X" }, { slug: "scuola", nome: "Doppia" }, { slug: "vuota", nome: "" }],
    meta: { cursore_successivo: null, aggiornato_il: null, stantio: true },
  }), { attiva: true, categorie: [{ slug: "scuola", nome: "Scuola" }], stantio: true });
  assert.deepEqual(leggiRispostaCategorie({ attiva: false, elementi: [], meta: null }), { attiva: false, categorie: [], stantio: false });
  assert.throws(() => leggiRispostaCategorie({ attiva: true, elementi: null }), TypeError);
  assert.throws(() => leggiRispostaCategorie(null), TypeError);
});

test("vociModulo: la selezione esclude chiuse e scadute secondo il giorno di Roma (00:30)", () => {
  const adesso = ms("2026-10-24T22:30:00Z"); // 00:30 del 25 ottobre a Roma
  const voci = [
    selezione(1, { stato: "aperto", scadenza: "2026-10-24" }),
    selezione(2, { stato: "aperto", scadenza: "2026-10-25" }),
    selezione(3, { stato: "chiuso", scadenza: null }),
    selezione(4, { stato: null, scadenza: null }),
    selezione(5, { stato: "altro", scadenza: "2026-11-01" }),
    selezione(6, { stato: "aperto", scadenza: null }),
    selezione(7, { stato: "aperto", scadenza: "2026-12-01" }),
  ];
  assert.deepEqual(vociModulo("selezione-personale", voci, adesso).map((v) => v.id), [2, 4, 5, 6]);
  assert.deepEqual(vociModulo("interpelli", [1, 2, 3, 4, 5, 6].map((id) => interpello(id)), adesso).map((v) => v.id), [1, 2, 3, 4]);
  assert.equal(vociModulo("notizie", Array.from({ length: 20 }, (_, i) => notizia(i + 1)), adesso).length, 20);
  assert.deepEqual(vociModulo("bandi", voci, adesso), []);
  const notizie = [notizia(1), notizia(2)];
  assert.equal(voceInEvidenza(notizie, "notizia:2").id, 2);
  assert.equal(voceInEvidenza(notizie, "notizia:9").id, 1);
  assert.equal(voceInEvidenza([], "notizia:1"), null);
});

test("nel modulo il titolo breve e' visibile e all'inizio del nome, il titolo completo lo segue se diverso", () => {
  // Senza titolo breve (o vuoto) il titolo, senza aggiunte.
  for (const titoloBreve of [null, undefined, "", "   "]) {
    assert.deepEqual(titoloModulo(notizia(1, { titolo_breve: titoloBreve })),
      { visibile: "Titolo della notizia 1", aggiunta: "", nome: "Titolo della notizia 1" }, String(titoloBreve));
  }
  // Titolo breve uguale al titolo: nessuna ripetizione.
  assert.deepEqual(titoloModulo(notizia(1, { titolo_breve: " Titolo della notizia 1 " })).aggiunta, "");
  // Titolo breve diverso, piu' corto o piu' lungo: visibile, poi ": {titolo}".
  for (const titoloBreve of ["Breve", "Titolo breve piu' lungo del titolo della notizia 1"]) {
    const titolo = titoloModulo(notizia(1, { titolo_breve: titoloBreve }));
    assert.deepEqual(titolo, {
      visibile: titoloBreve, aggiunta: ": Titolo della notizia 1", nome: `${titoloBreve}: Titolo della notizia 1`,
    });
    assert.ok(titolo.nome.startsWith(titolo.visibile));
  }
  const video = { url: `${MEDIA}/v.mp4`, tipo_mime: "video/mp4", copertina: null, durata_secondi: 65 };
  const conVideo = titoloModulo(notizia(1, { titolo_breve: "Breve", video, ha_video: true }), { conVideo: true });
  assert.deepEqual(conVideo, {
    visibile: "Breve",
    aggiunta: ": Titolo della notizia 1, Video, durata 1 minuto e 5 secondi",
    nome: "Breve: Titolo della notizia 1, Video, durata 1 minuto e 5 secondi",
  });
  assert.equal(titoloModulo(notizia(1, { video, ha_video: true }), { conVideo: true }).nome,
    "Titolo della notizia 1, Video, durata 1 minuto e 5 secondi");
  assert.equal(titoloModulo(notizia(1, { ha_video: true }), { conVideo: true }).nome, "Titolo della notizia 1, Video");
  // Senza conVideo (apertura: il player ha il suo nome) niente video nel titolo.
  assert.equal(titoloModulo(notizia(1, { titolo_breve: "Breve", video, ha_video: true })).nome, "Breve: Titolo della notizia 1");
  assert.equal(titoloModulo(notizia(1, { video, ha_video: true })).nome, "Titolo della notizia 1");
  assert.deepEqual(nomeGuardaVideo(notizia(1, { titolo_breve: "Breve", video: { ...video, durata_secondi: 134 } })), {
    visibile: "Guarda il video", aggiunta: ": Titolo della notizia 1, durata 2 minuti e 14 secondi",
    nome: "Guarda il video: Titolo della notizia 1, durata 2 minuti e 14 secondi",
  });
  assert.equal(nomeGuardaVideo(notizia(1, { video: { ...video, durata_secondi: null } })).nome, "Guarda il video: Titolo della notizia 1");
});

// --- bande della griglia ------------------------------------------------------

const idPagine = (lunghezze) => {
  let prossimo = 1;
  return lunghezze.map((n) => Array.from({ length: n }, () => prossimo++));
};
// Voci con l'immagine, salvo gli id in `senzaImmagine` (true: nessuna voce ce l'ha).
const vociDa = (pagine, senzaImmagine = []) => pagine.flat().map((id) => (
  senzaImmagine === true || senzaImmagine.includes(id) ? notizia(id) : notizia(id, { immagine: `${MEDIA}/foto-${id}.jpg` })
));
const schemi = (bande) => bande.map((b) => `${b.schema}:${b.voci.length}`);
// Coppia e specchio: "grande|colonna B" con gli id, per esempio "4|5+6".
const colonne = (bande) => bande.filter((b) => b.colonnaB).map((b) => {
  const grande = b.voci.filter((v) => !b.colonnaB.includes(v)).map((v) => v.id);
  return `${grande.join("+")}|${b.colonnaB.map((v) => v.id).join("+")}`;
});

function nessunaBandaAttraversa(lunghezze, senzaImmagine = []) {
  const pagine = idPagine(lunghezze);
  const paginaDi = new Map(pagine.flatMap((ids, indice) => ids.map((id) => [id, indice])));
  const { bande } = bandeGriglia(lunghezze, vociDa(pagine, senzaImmagine));
  for (const banda of bande) {
    assert.equal(new Set(banda.voci.map((v) => paginaDi.get(v.id))).size, 1, `${banda.schema} ${banda.chiave}`);
  }
  // Ogni voce dopo apertura e secondarie sta in una sola banda, nell'ordine.
  const inCima = new Set((pagine.find((ids) => ids.length > 0) ?? []).slice(0, 3));
  assert.deepEqual(bande.flatMap((b) => b.voci.map((v) => v.id)), pagine.flat().filter((id) => !inCima.has(id)));
  return bande;
}

test("bandeGriglia: apertura e secondarie dalla prima pagina, bande che non attraversano le pagine", () => {
  const pagine = idPagine([20, 20]);
  const { apertura, secondarie, bande } = bandeGriglia([20, 20], vociDa(pagine));
  assert.equal(apertura.id, 1);
  assert.deepEqual(secondarie.map((v) => v.id), [2, 3]);
  assert.deepEqual(schemi(bande), [
    // prima pagina: 17 voci
    "coppia:2", "terzina:3", "fascia:1", "trio:3", "coppia-specchio:2", "coppia:2", "terzina:3", "fascia:1",
    // seconda pagina: la fase riprende dal trio, l'ultima banda incompleta e' la coda
    "trio:3", "coppia-specchio:2", "coppia:2", "terzina:3", "fascia:1", "trio:3", "coppia-specchio:2", "coppia:2", "coda:2",
  ]);
  // Con le immagini la colonna B ha solo la voce B: nella coppia la seconda, nello specchio la prima.
  assert.deepEqual(colonne(bande).slice(0, 3), ["4|5", "14|13", "15|16"]);
  assert.ok(bande.every((b) => (b.colonnaB ? b.colonnaB.length === 1 : !["coppia", "coppia-specchio"].includes(b.schema))));
  assert.equal(bande[0].chiave, "notizia:4");
  assert.equal(bande.flatMap((b) => b.voci).length, 37);
  nessunaBandaAttraversa([20, 20]);
  nessunaBandaAttraversa([20, 15, 20, 1]);
});

test("bandeGriglia: con le immagini nei posti B le bande non cambiano, qualunque altra voce ne sia senza", () => {
  const pagine = idPagine([20, 20]);
  const tutte = bandeGriglia([20, 20], vociDa(pagine)).bande;
  // Senza immagine: A della coppia (4, 15), terzina (6), fascia (9), trio (10), grande dello specchio (14).
  const alcune = bandeGriglia([20, 20], vociDa(pagine, [4, 6, 9, 10, 14, 15])).bande;
  assert.deepEqual(schemi(alcune), schemi(tutte));
  assert.deepEqual(colonne(alcune), colonne(tutte));
});

test("bandeGriglia: coppia con la voce B senza immagine, 3 voci con B e la successiva nella colonna B", () => {
  const pagine = idPagine([20]);
  const bande = nessunaBandaAttraversa([20], [5]);
  assert.deepEqual(schemi(bande), ["coppia:3", "terzina:3", "fascia:1", "trio:3", "coppia-specchio:2", "coppia:2", "terzina:3"]);
  // La voce dopo B va nella colonna anche se ha l'immagine: la colonna e' di due voci di testo.
  assert.deepEqual(colonne(bande), ["4|5+6", "15|14", "16|17"]);
  assert.deepEqual(bande[0].voci.map((v) => v.id), [4, 5, 6]);
  assert.equal(bande[0].chiave, "notizia:4");
  // Conta solo la voce B: la A senza immagine tiene il ripiego e la banda resta di 2.
  assert.deepEqual(colonne(bandeGriglia([20], vociDa(pagine, [4])).bande)[0], "4|5");
});

test("bandeGriglia: specchio con la voce B senza immagine, B e la successiva nella colonna, la grande in fondo", () => {
  const pagine = idPagine([20]);
  const bande = nessunaBandaAttraversa([20], [13]);
  assert.deepEqual(schemi(bande), ["coppia:2", "terzina:3", "fascia:1", "trio:3", "coppia-specchio:3", "coppia:2", "terzina:3"]);
  assert.deepEqual(colonne(bande), ["4|5", "15|13+14", "16|17"]);
  assert.deepEqual(bande[4].voci.map((v) => v.id), [13, 14, 15]);
  // Solo la grande dello specchio senza immagine: niente colonna doppia.
  assert.deepEqual(colonne(bandeGriglia([20], vociDa(pagine, [14])).bande)[1], "14|13");
});

test("bandeGriglia: senza immagini la colonna B raddoppia in ogni coppia e specchio, e la fase prosegue fra le pagine", () => {
  const bande = nessunaBandaAttraversa([20, 20], true);
  assert.deepEqual(schemi(bande), [
    // prima pagina: 17 voci; dopo la seconda coppia ne resta una, la coda
    "coppia:3", "terzina:3", "fascia:1", "trio:3", "coppia-specchio:3", "coppia:3", "coda:1",
    // seconda pagina: la coda non completa la coppia, si riparte dalla terzina
    "terzina:3", "fascia:1", "trio:3", "coppia-specchio:3", "coppia:3", "terzina:3", "fascia:1", "trio:3",
  ]);
  assert.deepEqual(colonne(bande), ["4|5+6", "16|14+15", "17|18+19", "30|28+29", "31|32+33"]);
  assert.ok(bande.filter((b) => b.colonnaB).every((b) => b.colonnaB.length === 2));
});

test("bandeGriglia: al confine di pagina la coppia senza una terza voce tiene la colonna B con una voce sola", () => {
  // Prima pagina di 5: resta la coppia 4|5, che non prende la voce 6 della pagina dopo.
  assert.deepEqual(schemi(nessunaBandaAttraversa([5, 5], true)), ["coppia:2", "terzina:3", "fascia:1", "coda:1"]);
  assert.deepEqual(colonne(bandeGriglia([5, 5], vociDa(idPagine([5, 5]), true)).bande), ["4|5"]);
  // Lo specchio in fondo alla seconda pagina con 2 voci; la terza pagina riparte dalla coppia.
  const bande = nessunaBandaAttraversa([20, 9, 5], true);
  assert.deepEqual(schemi(bande).slice(7), ["terzina:3", "fascia:1", "trio:3", "coppia-specchio:2", "coppia:3", "coda:2"]);
  assert.deepEqual(colonne(bande).slice(3), ["29|28", "30|31+32"]);
});

test("bandeGriglia: Carica altri non ricompone le bande gia' viste", () => {
  const pagine = idPagine([20, 20]);
  for (const senzaImmagine of [[], true, [5, 13, 25]]) {
    const prima = bandeGriglia([20], vociDa([pagine[0]], senzaImmagine)).bande;
    const dopo = bandeGriglia([20, 20], vociDa(pagine, senzaImmagine)).bande;
    assert.deepEqual(dopo.slice(0, prima.length), prima, String(senzaImmagine));
  }
});

test("bandeGriglia: senza immagini, coda con 1 e con 2 voci e pagina accorciata dalla deduplica", () => {
  const senza = (lunghezze) => schemi(bandeGriglia(lunghezze, vociDa(idPagine(lunghezze), true)).bande);
  assert.deepEqual(senza([4]), ["coda:1"]);
  assert.deepEqual(senza([5]), ["coppia:2"]);
  assert.deepEqual(senza([6]), ["coppia:3"]);
  assert.deepEqual(senza([7]), ["coppia:3", "coda:1"]);
  assert.deepEqual(senza([8]), ["coppia:3", "coda:2"]);
  // La coda non completa la banda: la pagina dopo riparte dalla terzina.
  assert.deepEqual(senza([7, 3]), ["coppia:3", "coda:1", "terzina:3"]);
  // Seconda pagina ridotta a 15 voci dopo la deduplica.
  const bande = nessunaBandaAttraversa([20, 15], true);
  assert.deepEqual(schemi(bande).slice(7), ["terzina:3", "fascia:1", "trio:3", "coppia-specchio:3", "coppia:3", "coda:2"]);
  nessunaBandaAttraversa([20, 15, 20, 1], true);
  nessunaBandaAttraversa([20, 15, 20, 1], [5, 16, 17, 30, 44]);
});

test("bandeGriglia: coda con 1 e con 2 voci, fase che prosegue e pagina accorciata dalla deduplica", () => {
  assert.deepEqual(schemi(bandeGriglia([4], vociDa(idPagine([4]))).bande), ["coda:1"]);
  assert.deepEqual(schemi(bandeGriglia([5], vociDa(idPagine([5]))).bande), ["coppia:2"]);
  assert.deepEqual(schemi(bandeGriglia([7], vociDa(idPagine([7]))).bande), ["coppia:2", "coda:2"]);
  // La coda non completa la banda: la pagina dopo riparte dalla terzina.
  assert.deepEqual(schemi(bandeGriglia([7, 3], vociDa(idPagine([7, 3]))).bande), ["coppia:2", "coda:2", "terzina:3"]);
  // Prima pagina completa fino al fascia: la seconda comincia dal trio.
  assert.deepEqual(schemi(bandeGriglia([20, 3], vociDa(idPagine([20, 3]))).bande).slice(-1), ["trio:3"]);
  // Seconda pagina ridotta a 15 voci dopo la deduplica.
  const bande = nessunaBandaAttraversa([20, 15]);
  assert.deepEqual(schemi(bande).slice(8), ["trio:3", "coppia-specchio:2", "coppia:2", "terzina:3", "fascia:1", "trio:3", "coda:1"]);
});

test("bandeGriglia: prima pagina corta o vuota", () => {
  const corta = bandeGriglia([2], vociDa(idPagine([2])));
  assert.deepEqual([corta.apertura.id, corta.secondarie.map((v) => v.id), corta.bande], [1, [2], []]);
  const vuota = bandeGriglia([0, 5], vociDa(idPagine([0, 5])));
  assert.deepEqual([vuota.apertura.id, vuota.secondarie.map((v) => v.id), schemi(vuota.bande)], [1, [2, 3], ["coppia:2"]]);
  assert.deepEqual(bandeGriglia([], []), { apertura: null, secondarie: [], bande: [] });
});

test("motivoRipiego: tre varianti con le pendenze del logo, dentro il riquadro", () => {
  const punti = (tracciato) => tracciato.split(" ").map((p) => p.split(",").map(Number));
  const pendenza = (tracciato) => {
    const [[xa, ya], , , [xd, yd]] = punti(tracciato);
    return (xa - xd) / (yd - ya);
  };
  // Tratto del riquadro di ingombro che cade dentro 0..massimo (viewBox 0 0 160 90).
  const dentro = (valori, massimo) => Math.min(Math.max(...valori), massimo) - Math.max(Math.min(...valori), 0);
  const varianti = [0, 1, 2].map(motivoRipiego);
  assert.equal(new Set(varianti.map((v) => v.pieno)).size, 3);
  for (const { pieno, bordato } of varianti) {
    assert.equal(punti(pieno).length, 4);
    assert.equal(punti(bordato).length, 4);
    assert.ok(Math.abs(pendenza(pieno) - PENDENZA_PIENO) < 0.001, pieno);
    assert.ok(Math.abs(pendenza(bordato) - PENDENZA_BORDATO) < 0.001, bordato);
  }
  // Entrambe le sagome della coppia si vedono in ogni variante: almeno 10 unita' in x e in y.
  for (const [indice, variante] of varianti.entries()) {
    for (const [sagoma, tracciato] of Object.entries(variante)) {
      const xs = punti(tracciato).map(([x]) => x);
      const ys = punti(tracciato).map(([, y]) => y);
      assert.ok(dentro(xs, 160) >= 10 && dentro(ys, 90) >= 10, `variante ${indice}, ${sagoma}: ${tracciato}`);
    }
  }
  assert.deepEqual(motivoRipiego(3), varianti[0]);
  assert.deepEqual(motivoRipiego(-1), varianti[0]);
  assert.deepEqual(motivoRipiego(undefined), varianti[0]);
  assert.deepEqual([varianteRipiego(7), varianteRipiego(9), varianteRipiego(-1), varianteRipiego("4")], [1, 0, 0, 0]);
});

test("formaVocePagina: nei posti piccoli senza immagine la voce e' di solo testo, le grandi tengono il ripiego", () => {
  const conImmagine = notizia(1, { immagine: `${MEDIA}/foto.jpg` });
  const senza = [
    notizia(2),
    notizia(3, { immagine: undefined }),
    // Forme che leggiRispostaElenco scarterebbe comunque: segnaposto, http, testo qualsiasi.
    notizia(4, { immagine: `${MEDIA}${PERCORSO_SEGNAPOSTO}` }),
    notizia(5, { immagine: "http://media.edunews24.invalid/foto.jpg" }),
    notizia(6, { immagine: "foto.jpg" }),
    // Con il video ma senza immagine: il distintivo va nei metadati.
    notizia(7, { ha_video: true, video: { url: `${MEDIA}/v.mp4`, tipo_mime: "video/mp4", copertina: `${MEDIA}/c.jpg`, durata_secondi: 65 } }),
  ];
  assert.equal(formaVocePagina("compatta", conImmagine), "compatta");
  for (const voce of senza) assert.equal(formaVocePagina("compatta", voce), "testo", String(voce.immagine));
  for (const forma of ["scheda", "fascia", "testo"]) {
    assert.equal(formaVocePagina(forma, conImmagine), forma);
    assert.equal(formaVocePagina(forma, notizia(2)), forma);
  }
});

// --- configurazione ----------------------------------------------------------

test("regioni e aree: 20 regioni con slug unici, in ordine alfabetico", () => {
  assert.equal(REGIONI_EDUNEWS24.length, 20);
  assert.equal(new Set(REGIONI_EDUNEWS24.map((r) => r.slug)).size, 20);
  for (let i = 1; i < REGIONI_EDUNEWS24.length; i += 1) {
    assert.ok(REGIONI_EDUNEWS24[i - 1].nome.localeCompare(REGIONI_EDUNEWS24[i].nome, "it") < 0, REGIONI_EDUNEWS24[i].nome);
  }
  assert.deepEqual(AREE_EDUNEWS24, ["nazionale", ...REGIONI_EDUNEWS24.map((r) => r.slug)]);
});

test("ogni sezione ha i suoi testi, filtri e tipo di voce", () => {
  const ordinate = (oggetto) => Object.keys(oggetto).sort();
  const attese = [...SEZIONI_EDUNEWS24].sort();
  for (const [nome, oggetto] of Object.entries({
    sezioni: testi.sezioni, sezioniBrevi: testi.sezioniBrevi, vediTutto: testi.vediTutto, caricamento: testi.caricamento,
    vuotiModulo: testi.vuotiModulo, vuotiPagina: testi.vuotiPagina, TIPI_VOCE, FILTRI_PER_SEZIONE,
  })) {
    assert.deepEqual(ordinate(oggetto), attese, nome);
  }
  assert.deepEqual(ordinate(testi.tabellone), ["interpelli", "selezione-personale"]);
});

// Che gli indirizzi stiano solo in config/edunews24.js lo verifica
// edunews24Sorgenti.test.js.
test("social: URL https e testi per ogni rete", () => {
  assert.ok(SOCIAL_EDUNEWS24.length > 0);
  assert.equal(new Set(SOCIAL_EDUNEWS24.map((s) => s.rete)).size, SOCIAL_EDUNEWS24.length);
  for (const { rete, url } of SOCIAL_EDUNEWS24) {
    assert.ok(RETI_SOCIALI.includes(rete), rete);
    assert.ok(urlHttps(url), rete);
  }
  for (const rete of RETI_SOCIALI) {
    assert.ok(testi.social[rete], rete);
    assert.ok(testi.socialBrevi[rete], rete);
  }
});

const ICONE_SOCIAL = new URL("../src/assets/edunews24/", import.meta.url);
const STILI = new URL("../src/config/styles/edunews24.css", import.meta.url);
const TOKEN = new URL("../src/config/tokens/edunews24.css", import.meta.url);

test("ogni rete social ha il suo SVG e la sua maschera CSS", () => {
  const css = readFileSync(STILI, "utf8");
  for (const rete of RETI_SOCIALI) {
    assert.ok(existsSync(new URL(`${rete}.svg`, ICONE_SOCIAL)), `${rete}.svg`);
    assert.ok(css.includes(`.edunews24-social__icona--${rete}`), rete);
    // La maschera punta al suo SVG, con e senza prefisso (Safari).
    const maschera = `url("../../assets/edunews24/${rete}.svg")`;
    assert.ok(css.includes(`-webkit-mask-image: ${maschera}`), `${rete}: -webkit-mask-image`);
    assert.ok(css.includes(`  mask-image: ${maschera}`), `${rete}: mask-image`);
  }
});

test("le pendenze del JavaScript sono quelle dei token CSS", () => {
  const css = readFileSync(TOKEN, "utf8");
  const valore = (nome) => Number(css.match(new RegExp(`--edunews24-pendenza-${nome}:\\s*([0-9.]+)`))?.[1]);
  assert.equal(valore("pieno"), PENDENZA_PIENO);
  assert.equal(valore("bordato"), PENDENZA_BORDATO);
});

test("nessun testo usa glifi al posto delle parole o dei separatori", () => {
  const raccolti = [];
  const raccogli = (valore) => {
    if (typeof valore === "string") raccolti.push(valore);
    else if (typeof valore === "function") raccogli(valore("notizie", 3, 4));
    else if (valore && typeof valore === "object") Object.values(valore).forEach(raccogli);
  };
  raccogli(testi);
  raccogli(TESTI_DASHBOARD);
  assert.ok(raccolti.length > 50);
  for (const testo of raccolti) assert.doesNotMatch(testo, /[→›•×·▶]/, testo);
});
