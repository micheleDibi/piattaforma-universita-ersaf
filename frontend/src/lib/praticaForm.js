import { idValido } from "../config/routes/percorsi.js";
import { CAMPI_RINNOVO, eGruppoLauree } from "../config/pratica.js";

// Whitelist PraticaUpdate: gli altri campi del modello non sono aggiornabili.
// pratica_numero, pratica_prezzo e pratica_dataCreazione non ci sono: sono
// sempre di sola lettura (vedi payloadPratica e DatiPratica.jsx).
// pratica_stato_id invece c'e': lo manda sempre chi compila il form, ma il
// server lo scrive solo se chi chiama e' Nazionale (vedi aggiorna_pratica in
// backend/src/pratiche/routers.py) - per tutti gli altri e' un valore
// invariato, non un tentativo di modifica.
// Il rinnovo si invia insieme, solo se visibile per il percorso Lauree.
const MODIFICABILI = ["pratica_annoAccademico", "pratica_sedeErogazione", "pratica_note", "pratica_stato_id"];

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

/** Un importo in euro come si legge in Italia: "2.520,00". Solo per
 * mostrarlo, mai per calcolare (vedi sommaPrezzi). */
export function formattaImporto(numero) {
  return Number(numero).toLocaleString("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** Somma Decimal(20,8) senza gli arrotondamenti binari di Number. */
export function sommaPrezzi(prezzi) {
  let totale = 0n;
  for (const prezzo of prezzi) {
    const testo = prezzoPerInput(prezzo);
    if (!/^\d{1,12}(\.\d{1,8})?$/.test(testo)) return "";
    const [interi, frazione = ""] = testo.split(".");
    totale += BigInt(interi) * 100000000n + BigInt(frazione.padEnd(8, "0"));
  }
  const frazione = (totale % 100000000n).toString().padStart(8, "0").replace(/0+$/, "");
  return `${totale / 100000000n}${frazione ? `.${frazione}` : ""}`;
}

export function praticaVuota(oggi = new Date()) {
  return { pratica_dataCreazione: oggiLocale(oggi), pratica_numero: "", pratica_annoAccademico: "",
    pratica_sedeErogazione: "", pratica_prezzo: "", pratica_stato_id: "", pratica_note: "",
    ...valoriRinnovo(null) };
}

/** I tre campi di rinnovo, mutuamente esclusivi: campoSelezionato va a -1, gli
 * altri due a 0; null (nessun anno scelto, o casella deselezionata) li
 * azzera tutti. Estratta da useSchedaPratica.js perche' sia testabile senza
 * un hook (stesso motivo di paginaPercorsi in lib/opzioniPratica.js). */
export function valoriRinnovo(campoSelezionato) {
  return Object.fromEntries(CAMPI_RINNOVO.map(({ nome }) => [nome, nome === campoSelezionato ? -1 : 0]));
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

export function payloadPratica(dati, { nuova, studente, percorso, prodotto, corsiSingoli, corsiSelezionati }) {
  const payload = Object.fromEntries(MODIFICABILI.map(nome => [nome, dati[nome] === "" ? null : dati[nome]]));
  if (eGruppoLauree(prodotto?.listino_tipoCorso_id)) {
    Object.assign(payload, Object.fromEntries(CAMPI_RINNOVO.map(({ nome }) => [nome, dati[nome]])));
  }
  // Dal <select> arriva una stringa: il server si aspetta un numero.
  if (payload.pratica_stato_id != null) payload.pratica_stato_id = Number(payload.pratica_stato_id);

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
    // Non si inviano: cliente_emittente_aderente_id (il server lo collega
    // all'utente corrente per le ACL chat) e pratica_numero (lo genera
    // il server al salvataggio, vedi backend/src/pratiche/codice.py).
    // In creazione lo stato e' sempre Bozza, stabilito dal server.
    delete payload.pratica_stato_id;
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
