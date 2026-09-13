/**
 * Varianti degli elenchi: la scheda che contiene barra strumenti e tabella,
 * le celle e lo stato vuoto.
 *
 * Struttura di un elenco:
 *
 *   <div className={schedaElenco()}>
 *     <BarraStrumenti>...ricerca e filtri...</BarraStrumenti>
 *     <div className={scorrimentoTabella()}>
 *       <table className={tabella()}>
 *         <thead className={intestazioneTabella()}>
 *           <tr><th className={cellaIntestazione()}>Nome</th></tr>
 *         </thead>
 *         <tbody>
 *           <tr className={rigaTabella()}><td className={cella("forte")}>...</td></tr>
 *         </tbody>
 *       </table>
 *     </div>
 *   </div>
 */

/** Scheda di un elenco: barra strumenti e tabella sulla stessa superficie. */
export function schedaElenco() {
  return "bg-superficie border border-bordo rounded-superficie shadow-xs overflow-hidden";
}

/** Barra degli strumenti in testa all'elenco: ricerca e filtri a sinistra. */
export function barraStrumenti() {
  return (
    "flex flex-col gap-3 border-b border-bordo p-4 " +
    "sm:flex-row sm:items-center sm:justify-between"
  );
}

/** Lo scorrimento orizzontale di una tabella larga resta qui dentro. */
export function scorrimentoTabella() {
  return "w-full overflow-x-auto";
}

export function tabella() {
  return "min-w-full text-left";
}

/**
 * Tabella a se' stante, fuori da una scheda di elenco, per esempio dentro una
 * finestra modale: porta con se' la propria superficie.
 */
export function contenitoreTabella() {
  return (
    "w-full overflow-x-auto bg-superficie border border-bordo " +
    "rounded-superficie shadow-xs"
  );
}

export function intestazioneTabella() {
  return "bg-superficie-tenue text-etichetta text-testo-tenue text-left";
}

/**
 * Cella di intestazione. Il peso e' dichiarato qui perche' il browser rende i
 * <th> in grassetto e batterebbe quello ereditato.
 */
export function cellaIntestazione(allineamento = "sinistra") {
  const lato = allineamento === "destra" ? "text-right" : "text-left";
  return (
    `px-4 py-3 ${lato} text-etichetta font-semibold uppercase tracking-wider ` +
    "text-testo-tenue whitespace-nowrap"
  );
}

export function rigaTabella() {
  return "border-t border-bordo transition-colors hover:bg-superficie-tenue";
}

const TONI_CELLA = {
  normale: "text-testo",
  forte: "font-medium text-testo-forte",
  tenue: "text-testo-tenue",
};

/** @param {"normale"|"forte"|"tenue"} tono */
export function cella(tono = "normale") {
  return `px-4 py-3.5 text-sm whitespace-nowrap ${TONI_CELLA[tono] ?? TONI_CELLA.normale}`;
}

/** Cella delle azioni di riga, allineata a destra. */
export function cellaAzioni() {
  return "px-4 py-2 text-right whitespace-nowrap";
}

/** Riga di stato vuoto o di caricamento dentro il corpo della tabella. */
export function statoVuoto() {
  return "px-4 py-12 text-center text-sm text-testo-tenue";
}
