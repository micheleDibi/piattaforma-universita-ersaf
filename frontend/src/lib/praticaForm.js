import { idValido } from "../config/routes/percorsi.js";

// Whitelist PraticaUpdate: gli altri campi del modello non sono aggiornabili.
// pratica_numero, pratica_prezzo, pratica_stato_id e pratica_dataCreazione
// non ci sono: sono sempre di sola lettura (vedi payloadPratica e
// DatiPratica.jsx).
const MODIFICABILI = ["pratica_annoAccademico", "pratica_sedeErogazione", "pratica_note"];

/** Decimal(20,8) puo arrivare come "0E-8": espansione testuale senza arrotondare. */
export function prezzoPerInput(valore) {
  const testo = String(valore ?? "");
  const parti = testo.match(/^(\d+)(?:\.(\d+))?[eE]([+-]?\d+)$/);
  if (!parti) return testo;
  const [, interi, decimali = "", esponente] = parti;
  const posizione = interi.length + Number(esponente);
  const cifre = interi + decimali;
  if (posizione <= 0) return `0.${"0".repeat(-posizione)}${cifre}`;
  if (posizione >= cifre.length) return cifre + "0".repeat(posizione - cifre.length);
  return `${cifre.slice(0, posizione)}.${cifre.slice(posizione)}`;
}

function oggiLocale(oggi = new Date()) {
  return new Date(oggi.getTime() - oggi.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

export function praticaVuota(oggi = new Date()) {
  return { pratica_dataCreazione: oggiLocale(oggi), pratica_numero: "", pratica_annoAccademico: "",
    pratica_sedeErogazione: "", pratica_prezzo: "", pratica_stato_id: "", pratica_note: "" };
}

/** Il dettaglio del percorso formativo valido oggi (prezzo, ma anche durata,
 * CFU e tasse: vedi CaratteristichePercorso.jsx), o null se il listino non
 * ne ha uno attivo. Fra i dettagli validi oggi (data inizio non successiva,
 * data fine non precedente: "9999-12-31" di default vuol dire "ancora
 * valido") sceglie quello con la data di inizio piu' recente. */
export function dettaglioAttuale(dettagli, oggi = oggiLocale()) {
  if (!dettagli?.length) return null;
  const validi = dettagli.filter((d) =>
    (!d.listDettaglio_dataInizioValidazione || d.listDettaglio_dataInizioValidazione <= oggi) &&
    (!d.listDettaglio_dataFineValidazionoe || d.listDettaglio_dataFineValidazionoe >= oggi));
  if (!validi.length) return null;
  return validi.reduce((piuRecente, corrente) =>
    (corrente.listDettaglio_dataInizioValidazione ?? "") > (piuRecente.listDettaglio_dataInizioValidazione ?? "")
      ? corrente : piuRecente);
}

/** Il prezzo del percorso formativo valido oggi, o null se il listino non ne
 * ha uno attivo. */
export function prezzoAttuale(dettagli, oggi = oggiLocale()) {
  return dettaglioAttuale(dettagli, oggi)?.listDettaglio_prezzo ?? null;
}

export function payloadPratica(dati, { nuova, studente, percorso, prodotto, statoIniziale, corsiSingoli, corsiSelezionati }) {
  const payload = Object.fromEntries(MODIFICABILI.map(nome => [nome, dati[nome] === "" ? null : dati[nome]]));

  if (nuova) {
    // Il prezzo non si digita: arriva dal percorso formativo, o dalla somma
    // dei corsi scelti per Corsi Singoli (vedi useSchedaPratica.js). Il
    // controllo di formato resta come rete di sicurezza, non come messaggio
    // per chi compila la scheda.
    const prezzo = String(dati.pratica_prezzo ?? "").trim();
    if (!/^\d{1,12}(\.\d{1,8})?$/.test(prezzo)) {
      throw new Error("Il percorso formativo scelto non ha un prezzo attivo.");
    }
    if (!idValido(studente?.id)) throw new Error("Seleziona lo studente.");
    if (!idValido(percorso?.id) || prodotto?.listTesta_id !== percorso.id) throw new Error("Seleziona il percorso formativo.");
    if (!idValido(prodotto.nome_universita_id)) throw new Error("Il percorso deve avere un’università associata.");
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dati.pratica_dataCreazione || "")) throw new Error("Inserisci la data di creazione.");
    Object.assign(payload, { pratica_dataCreazione: dati.pratica_dataCreazione, pratica_prezzo: prezzo,
      cliente_id: studente.id,
      listTesta_id: percorso.id, nome_universita_id: prodotto.nome_universita_id,
      listino_tipo_corso_id: prodotto.listino_tipoCorso_id ?? null });
    // Non si inviano: cliente_emittente_aderente_id (colonna deprecata, il
    // database applica da solo il suo default) e pratica_numero (lo genera
    // il server al salvataggio, vedi backend/src/pratiche/codice.py).
    if (statoIniziale) payload.pratica_stato_id = statoIniziale.id;
    // Corsi Singoli: ogni corso scelto (compreso il primo, gia' in
    // listTesta_id sopra) diventa una riga in pratiche_listini lato server
    // (vedi crea_pratica in backend/src/pratiche/routers.py).
    if (corsiSingoli) {
      payload.corsi_singoli = corsiSelezionati.map(corso =>
        ({ listTesta_id: corso.id, prezzo: corso.prezzo == null ? null : String(corso.prezzo) }));
    }
  }
  return payload;
}
