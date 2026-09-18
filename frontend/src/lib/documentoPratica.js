import { apiFetch, leggiJson } from "./api.js";
import { descriviErrore, ErroreApi } from "./erroriApi.js";
import { TESTI_DOCUMENTO } from "../config/testi/documento.js";

// Il browser deve avere il tempo di avviare il download prima che l'URL del blob sparisca.
const ATTESA_REVOCA_MS = 60_000;

/** Se la pratica ha un modulo stampabile: il pulsante compare solo in quel caso. */
export async function documentoDisponibile(praticaId, signal) {
  const risposta = await apiFetch(`/pratiche/${praticaId}/documento/disponibile`, { cache: "no-store", signal });
  const dati = await leggiJson(risposta);
  if (!risposta.ok) {
    throw new ErroreApi(descriviErrore(risposta, dati, TESTI_DOCUMENTO.erroreVerifica), risposta.status);
  }
  return { disponibile: Boolean(dati?.disponibile), nomeFile: dati?.nome_file || null };
}

/** Il nome del file da Content-Disposition, nelle due forme (filename* e filename). */
export function nomeDaIntestazione(intestazione, ripiego) {
  const esteso = /filename\*\s*=\s*UTF-8''([^;]+)/i.exec(intestazione || "");
  if (esteso) {
    try { return decodeURIComponent(esteso[1].trim()); } catch { /* codifica non valida: si prova l'altra forma */ }
  }
  const semplice = /filename\s*=\s*"?([^";]+)"?/i.exec(intestazione || "");
  return semplice ? semplice[1].trim() : ripiego;
}

/**
 * Chiede il PDF con la sessione e lo salva con il nome indicato dal server.
 * `ambiente` permette ai test di sostituire document, URL e timer.
 */
export async function scaricaDocumento(praticaId, ambiente = globalThis) {
  const risposta = await apiFetch(`/pratiche/${praticaId}/documento`, { cache: "no-store" });
  if (!risposta.ok) {
    const dati = await leggiJson(risposta);
    throw new ErroreApi(descriviErrore(risposta, dati, TESTI_DOCUMENTO.erroreDownload), risposta.status);
  }
  const nome = nomeDaIntestazione(risposta.headers.get("Content-Disposition"), `pratica-${praticaId}.pdf`);
  const indirizzo = ambiente.URL.createObjectURL(await risposta.blob());
  const collegamento = ambiente.document.createElement("a");
  collegamento.href = indirizzo;
  collegamento.download = nome;
  ambiente.document.body.append(collegamento);
  collegamento.click();
  collegamento.remove();
  ambiente.setTimeout(() => ambiente.URL.revokeObjectURL(indirizzo), ATTESA_REVOCA_MS);
  return nome;
}
