import { idValido } from "../config/routes/percorsi.js";

// Whitelist PraticaUpdate: gli altri campi del modello non sono aggiornabili.
const MODIFICABILI = ["pratica_numero", "pratica_annoAccademico", "pratica_sedeErogazione",
  "pratica_prezzo", "pratica_stato_id", "pratica_note"];

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

export function praticaVuota(oggi = new Date()) {
  const locale = new Date(oggi.getTime() - oggi.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  return { pratica_dataCreazione: locale, pratica_numero: "", pratica_annoAccademico: "",
    pratica_sedeErogazione: "", pratica_prezzo: "", pratica_stato_id: "", pratica_note: "" };
}

export function payloadPratica(dati, { nuova, studente, percorso, emittente, prodotto }) {
  if (!dati.pratica_numero?.trim()) throw new Error("Inserisci il numero della pratica.");
  if (!idValido(dati.pratica_stato_id)) throw new Error("Seleziona lo stato della pratica.");
  const prezzo = String(dati.pratica_prezzo ?? "").trim();
  if (!/^\d{1,12}(\.\d{1,8})?$/.test(prezzo)) {
    throw new Error("Inserisci un prezzo valido, con al massimo otto decimali.");
  }
  const payload = Object.fromEntries(MODIFICABILI.map(nome => [nome, dati[nome] === "" ? null : dati[nome]]));
  payload.pratica_numero = dati.pratica_numero.trim();
  payload.pratica_prezzo = prezzo;
  payload.pratica_stato_id = Number(dati.pratica_stato_id);
  if (nuova) {
    if (!idValido(studente?.id)) throw new Error("Seleziona lo studente.");
    if (!idValido(emittente?.id)) throw new Error("Seleziona l’aderente emittente.");
    if (!idValido(percorso?.id) || prodotto?.listTesta_id !== percorso.id) throw new Error("Seleziona il percorso formativo.");
    if (!idValido(prodotto.nome_universita_id)) throw new Error("Il percorso deve avere un’università associata.");
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dati.pratica_dataCreazione || "")) throw new Error("Inserisci la data di creazione.");
    Object.assign(payload, { pratica_dataCreazione: dati.pratica_dataCreazione,
      cliente_id: studente.id, cliente_emittente_aderente_id: emittente.id,
      listTesta_id: percorso.id, nome_universita_id: prodotto.nome_universita_id,
      listino_tipo_corso_id: prodotto.listino_tipoCorso_id ?? null });
  }
  return payload;
}
