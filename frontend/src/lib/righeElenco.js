const testo = (valore) => String(valore ?? "").trim() || "-";

function formattaData(valore) {
  if (!valore) return "-";
  const data = new Date(valore);
  if (Number.isNaN(data.getTime())) return "-";
  const giorno = String(data.getDate()).padStart(2, "0");
  const mese = String(data.getMonth() + 1).padStart(2, "0");
  const anno = data.getFullYear();
  return `${giorno}-${mese}-${anno}`;
}

export function rigaCliente(item, { attuatori, mostraAzienda }) {
  const nominativo =
    [item.cliente_nome, item.cliente_cognome]
      .map((parte) => String(parte ?? "").trim())
      .filter(Boolean)
      .join(" ") || "-";
  return {
    id: item.cliente_id,
    nomeAzione: nominativo,
    campi: {
      nominativo,
      nome: testo(item.cliente_nome),
      cognome: testo(item.cliente_cognome),
      ...(attuatori ? { ruolo: testo(item.ruolo?.ruolo_codice) } : {}),
      ...(mostraAzienda
        ? { azienda: testo(item.azienda?.azienda_ragione_sociale) }
        : {}),
    },
  };
}

export function rigaAzienda(item) {
  const via = [item.azienda_via, item.azienda_civico].filter(Boolean).join(" ");
  const localita = [
    item.azienda_CAP,
    item.azienda_citta,
    item.azienda_provincia ? `(${item.azienda_provincia})` : null,
  ]
    .filter(Boolean)
    .join(" ");
  const azienda = testo(item.azienda_ragione_sociale);
  return {
    id: item.azienda_id,
    nomeAzione: azienda,
    campi: {
      azienda,
      sede: [via, localita].filter(Boolean).join(", ") || "-",
      avviso: item.anomalie ?? [],
    },
  };
}

export function rigaPratica(item) {
  const numero = testo(item.pratica_numero);
  return {
    id: item.pratica_id,
    nomeAzione: numero !== "-" ? numero : testo(item.cliente_nome_completo),
    campi: {
      numero,
      cliente: testo(item.cliente_nome_completo),
      corso: testo(item.listTesta_descrizione),
      dataCreazione: formattaData(item.pratica_dataCreazione), // MODIFICATO
      stato: testo(item.pratica_stato_descrizione),
    },
  };
}

export function rigaProdotto(item) {
  const titolo = testo(item.listTesta_descrizione);
  const attivo = item.listino_attivoSN === -1;
  return {
    id: item.listTesta_id,
    nomeAzione: titolo,
    tonoStato: attivo ? "positivo" : "neutro",
    campi: {
      titolo,
      codice: testo(item.listTesta_codice),
      universita: testo(item.nome_universita),
      tipo: testo(item.listino_tipoCorso_descrizione),
      stato: attivo ? "Attivo" : "Non attivo",
    },
  };
}
