import { dettaglioAttuale } from "./praticaForm.js";

export function opzioneStudente(cliente) {
  return { id: cliente.cliente_id,
    label: [cliente.cliente_nome, cliente.cliente_cognome].filter(Boolean).join(" "),
    dettaglio: cliente.cliente_codice || "" };
}
export const paginaStudenti = dati => ({ elementi: dati.map(opzioneStudente), altri: dati.length === 20 });

/** Un percorso formativo per il modale di selezione (ModaleSelezionePercorso):
 * prezzo e CFU vengono dal dettaglio del listino valido oggi, la stessa
 * regola di dettaglioAttuale usata per il prezzo della pratica. GET
 * /listini-testa/ con valido_oggi=true garantisce che ci sia sempre un
 * dettaglio, quindi qui non serve gestire il caso "nessun prezzo attivo". */
export function opzionePercorsoConDettaglio(prodotto, oggi) {
  const dettaglio = dettaglioAttuale(prodotto.dettagli, oggi);
  return { id: prodotto.listTesta_id, codice: prodotto.listTesta_codice || "",
    label: prodotto.listTesta_descrizione,
    prezzo: dettaglio?.listDettaglio_prezzo ?? null, cfu: dettaglio?.listDettaglio_CFU ?? null,
    corsoLaurea: prodotto.listino_corsoLaurea_descrizione || "" };
}

/** Un corso di una pratica Corsi Singoli gia' salvata (PraticaResponse.corsi)
 * nella stessa forma delle opzioni del modale, cosi' l'elenco dei corsi della
 * scheda li mostra allo stesso modo in creazione e in visualizzazione. */
export function opzioneCorsoPratica(corso) {
  return { id: corso.listTesta_id, codice: corso.codice || "", label: corso.descrizione || "",
    prezzo: corso.prezzo ?? null, cfu: corso.cfu ?? null, corsoLaurea: corso.corso_laurea || "" };
}
// ATTENZIONE: dati.map(opzionePercorsoConDettaglio) passerebbe anche l'indice
// come secondo argomento (oggi), rompendo il confronto fra date in
// dettaglioAttuale per ogni riga (stesso difetto di ["1","2"].map(parseInt)).
// La funzione sta qui, non dentro ModaleSelezionePercorso.jsx, cosi' un test
// la esercita davvero attraverso il map: e' li' che si era rotta la prima volta.
export const paginaPercorsi = dati => ({ elementi: dati.map((prodotto) => opzionePercorsoConDettaglio(prodotto)), altri: dati.length === 20 });
