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
    ? `${VOCE} bg-primario-tenue text-primario`
    : `${VOCE} text-testo-tenue hover:bg-superficie-alta hover:text-testo-forte`;
}

export function iconaNavigazione(attiva = false) {
  const colore = attiva
    ? "text-primario"
    : "text-testo-tenue group-hover:text-testo-forte";
  return `size-icona shrink-0 ${colore}`;
}

/** Voce di uscita: neutra a riposo, negativa al passaggio. */
export function voceUscita() {
  return `${VOCE} text-testo-tenue hover:bg-negativo-tenue hover:text-negativo`;
}

/**
 * Testata del menu con il nome dell'applicazione. Alta quanto la barra
 * superiore da mobile, cosi' le due restano allineate passando da una all'altra.
 */
export function testataMenu() {
  return "flex h-barra-superiore shrink-0 items-center gap-3 border-b border-bordo px-5";
}

export function nomeApplicazione() {
  return "truncate text-sm font-semibold text-testo-forte";
}
