import { apiFetch, messaggioErrore } from "./api.js";
import { TESTI_FIRMA as testi } from "../config/testi/firma.js";

export async function leggiFirma(id, signal) {
  const risposta = await apiFetch(`/pratiche/${id}/firma`, { signal, cache: "no-store" });
  if (!risposta.ok) throw new Error(await messaggioErrore(risposta, testi.errore));
  return risposta.json();
}
export async function salvaFirma(id, immagine, versione) {
  const risposta = await apiFetch(`/pratiche/${id}/firma`, {
    method: "PUT", body: JSON.stringify({ immagine, versione }),
  });
  if (!risposta.ok) throw new Error(await messaggioErrore(risposta, testi.erroreSalvataggio));
  return risposta.json();
}
