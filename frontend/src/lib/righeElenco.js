import { TESTI_ELENCO } from "../config/testi/elenco.js";

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

// Unica fonte dei pallini dei clienti, nell'ordine in cui compaiono: la
// colonna e la legenda derivano entrambe da qui. Il diploma e' calcolato dal
// backend solo per i sottoscrittori.
const INDICATORI_CLIENTE = [
  { id: "email", campo: "email_verificata" },
  { id: "cellulare", campo: "cellulare_verificato" },
  { id: "diploma", campo: "diploma_completo", soloSottoscrittori: true },
];

const indicatoriCliente = (attuatori) =>
  INDICATORI_CLIENTE.filter(
    (indicatore) => !(attuatori && indicatore.soloSottoscrittori),
  );

/** Il campo dei pallini fra quelli di una vista, se c'e'. */
export const campoIndicatori = (campi) =>
  campi.find((campo) => campo.rilievo === "indicatori");

/** Id del testo che descrive i pallini di una riga, unico per vista grazie a
 * `base`; undefined se la riga non ne ha, cosi' `aria-describedby` non compare. */
export function idIndicatori(base, riga, campo) {
  return campo && riga.campi[campo.id]?.length
    ? `${base}-indicatori-${riga.id}`
    : undefined;
}

/** Verde solo per un `true` esplicito: assente o null vale grigio. */
function statoCliente(item, attuatori) {
  return indicatoriCliente(attuatori).map(({ id, campo }) => {
    const attivo = item[campo] === true;
    const testi = TESTI_ELENCO.indicatori[id];
    return { id, attivo, voce: testi.voce, etichetta: attivo ? testi.si : testi.no };
  });
}

export function rigaCliente(item, { attuatori, mostraAzienda }) {
  const [nome, cognome] = [item.cliente_nome, item.cliente_cognome].map(
    (parte) => String(parte ?? "").trim(),
  );
  // "Cognome Nome", come negli elenchi cartacei; le iniziali nello stesso ordine.
  const nominativo = [cognome, nome].filter(Boolean).join(" ") || "-";
  const iniziali = [cognome, nome]
    .map((parte) => parte.charAt(0))
    .join("")
    .toUpperCase();
  return {
    id: item.cliente_id,
    nomeAzione: nominativo,
    iniziali,
    campi: {
      nominativo,
      avviso: item.anomalie ?? [],
      verifiche: statoCliente(item, attuatori),
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
      dataCreazione: formattaData(item.pratica_dataCreazione),
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
