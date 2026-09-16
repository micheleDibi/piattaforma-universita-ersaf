/**
 * Varianti del menu di navigazione: voci, icone e marchio dell'applicazione.
 *
 * La voce attiva e' tinta, non piena: lo sfondo tenue con il testo nella tinta
 * primaria segnala la posizione senza pesare quanto un pulsante.
 */

const VOCE =
  "group flex w-full items-center gap-3 rounded-controllo px-3 py-2 " +
  "text-sm font-medium transition-colors cursor-pointer " +
  "focus:outline-none focus-visible:ring-3 focus-visible:ring-fuoco/30";

export function voceNavigazione(attiva = false) {
  return attiva
    ? `${VOCE} bg-interazione-selezionata text-primario shadow-selezione hover:bg-interazione-selezionata-hover`
    : `${VOCE} text-testo-tenue hover:bg-interazione-hover hover:text-testo-forte`;
}

export function iconaNavigazione(attiva = false) {
  const colore = attiva
    ? "text-primario"
    : "text-testo-tenue group-hover:text-testo-forte";
  return `size-icona shrink-0 ${colore}`;
}

/** L'uscita condivide il feedback delle altre voci del menu. */
export function voceUscita() {
  return `${VOCE} text-testo-tenue hover:bg-interazione-hover hover:text-testo-forte`;
}

/** Versione e data dell'ultimo aggiornamento, sotto "Esci": discreta, allineata al testo delle voci. */
export function notaVersione() {
  return "mt-2 px-3 text-nota leading-relaxed text-testo-tenue";
}

/**
 * Testata del menu con il logo dell'applicazione. Alta quanto la barra
 * superiore da mobile, cosi' le due restano allineate passando da una all'altra.
 */
export function testataMenu() {
  return "flex h-barra-superiore shrink-0 items-center gap-3 border-b border-bordo px-5";
}

