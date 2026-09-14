import { ROTTE } from "../routes/rotte.js";

const ELENCHI = new Set([ROTTE.sottoscrittori, ROTTE.attuatori, ROTTE.aziende, ROTTE.pratiche, ROTTE.prodotti]);

// La variante dipende dalla rotta, non dagli stati transitori di caricamento.
export function movimentoPagina(percorso) {
  return ELENCHI.has(percorso) ? "movimento-pagina movimento-pagina--elenco" : "movimento-pagina";
}
