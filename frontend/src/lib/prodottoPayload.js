// Converte una stringa numerica (con virgola o punto) in Number.
// Restituisce null se non è un numero valido.
export const parseNumeroItaliano = (valore) => {
  if (valore === "" || valore === null || valore === undefined) return null;
  const normalizzato = String(valore).replace(",", ".");
  const num = Number(normalizzato);
  return isNaN(num) ? null : num;
};

export function creaPayloadProdotto(formData, dettagliDaInviare) {
  return {
      ...formData,
      listTesta_livello:
        formData.listTesta_livello !== ""
          ? Number(formData.listTesta_livello)
          : null,
      listino_modalita_id:
        formData.listino_modalita_id !== ""
          ? Number(formData.listino_modalita_id)
          : null,
      listino_tipoCorso_id:
        formData.listino_tipoCorso_id !== ""
          ? Number(formData.listino_tipoCorso_id)
          : null,
      listino_durataLaurea_id:
        formData.listino_durataLaurea_id !== ""
          ? Number(formData.listino_durataLaurea_id)
          : null,
      listino_facolta_id:
        formData.listino_facolta_id !== ""
          ? Number(formData.listino_facolta_id)
          : null,
      listino_corsoLaurea_id:
        formData.listino_corsoLaurea_id !== ""
          ? Number(formData.listino_corsoLaurea_id)
          : null,
      nome_universita_id:
        formData.nome_universita_id !== ""
          ? Number(formData.nome_universita_id)
          : null,
      dettagli: dettagliDaInviare.map((d) => ({
        listDettaglio_dataInizioValidazione:
          d.listDettaglio_dataInizioValidazione || null,
        listDettaglio_dataFineValidazionoe:
          d.listDettaglio_dataFineValidazionoe || "9999-12-31",
        listDettaglio_prezzo: parseNumeroItaliano(d.listDettaglio_prezzo),
        listDettaglio_durata:
          d.listDettaglio_durata !== "" && d.listDettaglio_durata !== null
            ? parseInt(d.listDettaglio_durata, 10)
            : null,
        listDettaglio_CFU:
          d.listDettaglio_CFU !== "" && d.listDettaglio_CFU !== null
            ? parseInt(d.listDettaglio_CFU, 10)
            : null,
        listDettaglio_tasse: parseNumeroItaliano(d.listDettaglio_tasse),
      })),
    };

}

export function aggiungiDettaglio(prevDettagli, oggi, dataIeri) {
      const dettagliAggiornati = prevDettagli.map((det, index) => {
        if (index === prevDettagli.length - 1) {
          return {
            ...det,
            listDettaglio_dataFineValidazionoe: dataIeri,
          };
        }
        return det;
      });

      return [
        ...dettagliAggiornati,
        {
          listDettaglio_dataInizioValidazione: oggi,
          listDettaglio_dataFineValidazionoe: "9999-12-31",
          listDettaglio_prezzo: "",
          listDettaglio_durata: "",
          listDettaglio_CFU: "",
          listDettaglio_tasse: "",
          isNew: true,
        },
      ];
}
