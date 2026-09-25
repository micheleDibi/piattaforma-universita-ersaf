const ruolo = { id: "ruolo", etichetta: "Ruolo", icona: "ruolo" };
const azienda = { id: "azienda", etichetta: "Azienda", icona: "azienda" };
const sede = { id: "sede", etichetta: "Sede", icona: "sede" };
const numero = { id: "numero", etichetta: "Codice", rilievo: "principale" };
const cliente = {
  id: "cliente",
  etichetta: "Sottoscrittore",
  rilievo: "principale",
  icona: "cliente",
};
const corso = { id: "corso", etichetta: "Corso", icona: "corso" };
const stato = { id: "stato", etichetta: "Stato", rilievo: "stato" };
// Stato delle pratiche: come le verifiche di attuatori/sottoscrittori, senza
// il pallino e verde solo a conclusione (vedi tonoStato in rigaPratica).
const statoPratica = { ...stato, puntino: false };
// Nominativo dei clienti: iniziali, "Cognome Nome" e avviso delle anomalie.
// Il nome si ferma a due righe e il title lo mostra per intero.
const persona = { id: "nominativo", etichetta: "Nominativo", rilievo: "persona", righe: 2 };
// Azienda negli elenchi dei clienti: testo secondario (13px) su due righe al
// massimo, come nel design. Nell'elenco delle Aziende resta il campo principale.
const aziendaCliente = { ...azienda, rilievo: "secondario", righe: 2 };
const verifiche = { id: "verifiche", etichetta: "Verifiche", rilievo: "indicatori" };
const titolo = { id: "titolo", etichetta: "Titolo", rilievo: "principale" };
const codice = { id: "codice", etichetta: "Codice", rilievo: "codice" };
const universita = {
  id: "universita",
  etichetta: "Università",
  icona: "universita",
};
const tipo = { id: "tipo", etichetta: "Tipo di corso", icona: "tipo" };
// Corso delle pratiche: testo secondario su due righe al massimo, come
// l'azienda dei clienti; il title lo mostra per intero.
const corsoPratica = { ...corso, rilievo: "secondario", righe: 2 };

// NUOVE — servono solo a MODELLO_PRATICHE. Nomi distinti da "universita"/"tipo"
// sopra: quelle sono per MODELLO_PRODOTTI e usano id "universita"/"tipo" che
// puntano a campi diversi (nome_universita vs listino_tipoCorso_descrizione).
const dataCreazione = {
  id: "dataCreazione",
  etichetta: "Data di creazione",
  icona: "data",
};

const colonna = (campo) => ({
  id: campo.id,
  etichetta: campo.etichetta,
  campi: [campo],
});

// Valori del filtro Ruolo degli Attuatori: sono i codici che l'API accetta nel
// parametro `ruolo`, quindi stanno qui e non nei testi. La voce senza filtro
// e' TESTI_ELENCO.tuttiRuoli.
export const RUOLI_FILTRO = ["Aderente", "Provinciale", "Regionale", "Nazionale", "Operatore"];

/**
 * Colonne dei clienti. Le proporzioni del design (Nominativo 2.4, Ruolo 0.9,
 * Azienda 2, Verifiche 1.5, chevron 24px; 2 e 1.3 per i Sottoscrittori) stanno
 * in config/styles/righeElenco.css, legate agli id delle colonne.
 */
export function modelloClienti({ attuatori, mostraAzienda }) {
  const riferimenti = [
    ...(attuatori ? [ruolo] : []),
    ...(mostraAzienda ? [aziendaCliente] : []),
  ];
  return {
    id: "clienti",
    etichetta: attuatori ? "Attuatori" : "Sottoscrittori",
    ampiezza: mostraAzienda ? "articolata" : "semplice",
    colonne: [persona, ...riferimenti, verifiche].map(colonna),
    mobile: [persona, verifiche, ...riferimenti],
  };
}

export const MODELLO_AZIENDE = {
  id: "aziende",
  etichetta: "Aziende",
  ampiezza: "semplice",
  colonne: [
    colonna({
      ...azienda,
      etichetta: "Ragione sociale",
      rilievo: "principale",
    }),
    colonna(sede),
  ],
  mobile: [
    { ...azienda, etichetta: "Ragione sociale", rilievo: "principale" },
    sede,
  ],
  avvisoDopo: "azienda",
};

export const MODELLO_PRATICHE = {
  id: "pratiche",
  etichetta: "Pratiche",
  ampiezza: "articolata",
  colonne: [numero, dataCreazione, cliente, corsoPratica, statoPratica].map(colonna),
  mobile: [numero, dataCreazione, cliente, corsoPratica, statoPratica],
};

export const MODELLO_PRODOTTI = {
  id: "prodotti",
  etichetta: "Prodotti formativi",
  ampiezza: "articolata",
  colonne: [titolo, codice, universita, tipo, stato].map(colonna),
  mobile: [titolo, universita, tipo, codice, stato],
};
