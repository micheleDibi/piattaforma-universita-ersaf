export function opzioneStudente(cliente) {
  return { id: cliente.cliente_id,
    label: [cliente.cliente_nome, cliente.cliente_cognome].filter(Boolean).join(" "),
    dettaglio: cliente.cliente_codice || "" };
}
export function opzionePercorso(prodotto) {
  return { id: prodotto.listTesta_id, label: prodotto.listTesta_descrizione,
    dettaglio: prodotto.listTesta_codice || "" };
}
export const paginaStudenti = dati => ({ elementi: dati.map(opzioneStudente), altri: dati.length === 20 });
export const paginaPercorsi = dati => ({ elementi: dati.map(opzionePercorso), altri: dati.length === 20 });
