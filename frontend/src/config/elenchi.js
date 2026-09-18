const nominativo = {
  id: "nominativo",
  etichetta: "Nominativo",
  rilievo: "principale",
};
const nome = { id: "nome", etichetta: "Nome", rilievo: "principale" };
const cognome = { id: "cognome", etichetta: "Cognome", rilievo: "principale" };
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
// Stesso id della colonna di pratiche e prodotti, e quindi stessa larghezza,
// ma i valori sono i pallini di rigaCliente e non un'etichetta.
const statoCliente = { id: "stato", etichetta: "Stato", rilievo: "indicatori" };
const titolo = { id: "titolo", etichetta: "Titolo", rilievo: "principale" };
const codice = { id: "codice", etichetta: "Codice", rilievo: "codice" };
const universita = {
  id: "universita",
  etichetta: "Università",
  icona: "universita",
};
const tipo = { id: "tipo", etichetta: "Tipo di corso", icona: "tipo" };

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

export function modelloClienti({ attuatori, mostraAzienda }) {
  const riferimenti = [
    ...(attuatori ? [ruolo] : []),
    ...(mostraAzienda ? [azienda] : []),
  ];
  return {
    id: "clienti",
    etichetta: attuatori ? "Attuatori" : "Sottoscrittori",
    ampiezza: mostraAzienda ? "articolata" : "semplice",
    avvisoDopo: "cognome",
    colonne: [nome, cognome, statoCliente, ...riferimenti].map(colonna),
    mobile: [nominativo, statoCliente, ...riferimenti],
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
  colonne: [numero, dataCreazione, cliente, corso, stato].map(colonna),
  mobile: [numero, dataCreazione, cliente, corso, stato],
};

export const MODELLO_PRODOTTI = {
  id: "prodotti",
  etichetta: "Prodotti formativi",
  ampiezza: "articolata",
  colonne: [titolo, codice, universita, tipo, stato].map(colonna),
  mobile: [titolo, universita, tipo, codice, stato],
};
