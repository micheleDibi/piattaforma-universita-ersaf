export const LIMITE_PRATICHE = 40;
export function queryPratiche({
  ricerca,
  numeroPratica,
  stato,
  studenti,
  universita,
  tipoCorso,
  tipoSelezionato,
}) {
  const query = new URLSearchParams({ limit: LIMITE_PRATICHE });
  if (ricerca.trim()) query.set("search", ricerca.trim());
  if (numeroPratica.trim()) query.set("numero_pratica", numeroPratica.trim());
  if (stato) query.set("pratica_stato_id", stato);
  studenti.forEach(({ id }) => query.append("studenti", id));
  if (universita) query.set("nome_universita_id", universita);
  const tipiDaUsare = tipoSelezionato ? [tipoSelezionato] : tipoCorso;
  tipiDaUsare.forEach((idTipo) =>
    query.append("listino_tipo_corso_id", idTipo),
  );
  return `/pratiche/?${query}`;
}

export function paginaPratiche(dati) {
  return { elementi: dati, altri: dati.length === LIMITE_PRATICHE };
}

// Elenco del Nazionale (ElencoPraticheNazionale.jsx): tutte le pratiche tranne
// le Bozze, raggruppate per stato. L'ordine dei gruppi lo decide il server
// (ORDINE_STATI in backend/src/pratiche/filtri.py), cosi' una pagina caricata
// dopo continua il gruppo invece di ricominciarlo: qui lo stesso ordine serve
// solo alle voci del filtro Stato.
export const ORDINE_STATI_NAZIONALE = [1, 4, 2, 3, 5];

function filtriNazionale({ ricerca, numeroPratica, stato, universita }) {
  const query = new URLSearchParams({ escludi_bozze: "true" });
  if (ricerca.trim()) query.set("search", ricerca.trim());
  if (numeroPratica.trim()) query.set("numero_pratica", numeroPratica.trim());
  if (stato) query.set("pratica_stato_id", stato);
  if (universita) query.set("nome_universita_id", universita);
  return query;
}

export function queryPraticheNazionale(filtri) {
  const query = filtriNazionale(filtri);
  query.set("ordine", "stato");
  query.set("limit", LIMITE_PRATICHE);
  return `/pratiche/?${query}`;
}

/** Quante pratiche per stato con gli stessi filtri: i numeri dei gruppi. */
export function queryConteggiNazionale(filtri) {
  return `/pratiche/conteggi/stati?${filtriNazionale(filtri)}`;
}

/** Le voci del filtro Stato, nell'ordine dei gruppi e senza Bozza. */
export function statiNazionale(stati) {
  return ORDINE_STATI_NAZIONALE.map((id) => stati.find((stato) => stato.id === id)).filter(Boolean);
}

/** Senza ricerca ne' filtri l'elenco ha un solo gruppo, "Tutte le pratiche",
 * con il totale di tutti gli stati; resta ordinato per stato. Nessun gruppo se
 * non ci sono pratiche. */
export function gruppoUnico(pratiche, conteggi) {
  if (pratiche.length === 0) return [];
  return [{
    statoId: "tutte",
    titolo: "Tutte le pratiche",
    totale: conteggi ? conteggi.reduce((somma, c) => somma + c.totale, 0) : null,
    pratiche,
  }];
}

/**
 * Le pratiche caricate divise in gruppi di stato consecutivi, nell'ordine in
 * cui arrivano dal server. `totale` e' il numero di pratiche dello stato con i
 * filtri attivi, anche quelle non ancora caricate; null finche' i conteggi
 * non sono arrivati.
 *
 * @param {Array} pratiche  elementi dell'elenco, gia' ordinati per stato
 * @param {Array<{pratica_stato_id: number, totale: number}>|null} conteggi
 */
export function raggruppaPerStato(pratiche, conteggi) {
  const totali = new Map((conteggi ?? []).map((c) => [c.pratica_stato_id, c.totale]));
  const gruppi = [];
  for (const pratica of pratiche) {
    const ultimo = gruppi.at(-1);
    if (ultimo && ultimo.statoId === pratica.pratica_stato_id) {
      ultimo.pratiche.push(pratica);
      continue;
    }
    gruppi.push({
      statoId: pratica.pratica_stato_id,
      titolo: pratica.pratica_stato_descrizione || "Stato non indicato",
      totale: conteggi ? totali.get(pratica.pratica_stato_id) ?? 0 : null,
      pratiche: [pratica],
    });
  }
  return gruppi;
}
