const nominativo = { id: "nominativo", etichetta: "Nominativo", rilievo: "principale" };
const ruolo = { id: "ruolo", etichetta: "Ruolo", icona: "ruolo" };
const azienda = { id: "azienda", etichetta: "Azienda", icona: "azienda" };
const sede = { id: "sede", etichetta: "Sede", icona: "sede" };
const numero = { id: "numero", etichetta: "Numero", rilievo: "principale" };
const cliente = { id: "cliente", etichetta: "Sottoscrittore", rilievo: "principale", icona: "cliente" };
const corso = { id: "corso", etichetta: "Corso", icona: "corso" };
const stato = { id: "stato", etichetta: "Stato", rilievo: "stato" };
const titolo = { id: "titolo", etichetta: "Titolo", rilievo: "principale" };
const codice = { id: "codice", etichetta: "Codice", rilievo: "codice" };
const universita = { id: "universita", etichetta: "Università", icona: "universita" };
const tipo = { id: "tipo", etichetta: "Tipo di corso", icona: "tipo" };

const colonna = (campo) => ({ id: campo.id, etichetta: campo.etichetta, campi: [campo] });

export function modelloClienti({ attuatori, mostraAzienda }) {
  const campi = [nominativo, ...(attuatori ? [ruolo] : []), ...(mostraAzienda ? [azienda] : [])];
  return {
    id: "clienti", etichetta: attuatori ? "Attuatori" : "Sottoscrittori",
    ampiezza: mostraAzienda ? "articolata" : "semplice",
    colonne: campi.map(colonna), mobile: campi,
  };
}

export const MODELLO_AZIENDE = {
  id: "aziende", etichetta: "Aziende", ampiezza: "semplice",
  colonne: [colonna({ ...azienda, etichetta: "Ragione sociale", rilievo: "principale" }), colonna(sede)],
  mobile: [{ ...azienda, etichetta: "Ragione sociale", rilievo: "principale" }, sede],
};

export const MODELLO_PRATICHE = {
  id: "pratiche", etichetta: "Pratiche", ampiezza: "articolata",
  colonne: [numero, cliente, corso, stato].map(colonna),
  mobile: [numero, stato, cliente, corso],
};

export const MODELLO_PRODOTTI = {
  id: "prodotti", etichetta: "Prodotti formativi", ampiezza: "articolata",
  colonne: [
    { id: "prodotto", etichetta: "Prodotto", campi: [titolo, codice] },
    colonna(universita),
    { id: "tipo", etichetta: "Tipo e stato", campi: [tipo, stato] },
  ],
  mobile: [titolo, universita, tipo, codice, stato],
};
