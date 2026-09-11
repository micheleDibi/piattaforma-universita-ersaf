/**
 * Varianti del pulsante nativo.
 *
 * Come per i campi non esiste nessun componente: resta `<button>` e da qui
 * arriva la configurazione visuale.
 *
 *   <button className={pulsante()}>Salva</button>
 *   <button className={pulsante("secondario")}>Annulla</button>
 *
 * Perche' esiste: lo stesso ruolo, l'azione primaria, era dipinto con quattro
 * colori diversi nelle varie pagine, indigo e blue in due tonalita' ciascuno.
 *
 * REGOLA DI QUESTO CATALOGO: riproduce l'aspetto attuale. L'unica scelta che
 * comporta una differenza visibile e' il colore dell'azione primaria, che qui
 * diventa uno solo: convertendo un pulsante oggi blu lo si vede diventare
 * indaco. Per questo la conversione va fatta a vista, una pagina alla volta, e
 * non con una sostituzione automatica.
 */

const BASE =
  "inline-flex items-center justify-center gap-2 font-medium " +
  // Il bordo trasparente tiene la stessa altezza fra primario e secondario, ed
  // e' anche la misura che i pulsanti avevano prima della centralizzazione.
  "rounded-controllo border border-transparent transition-colors cursor-pointer " +
  "focus:outline-none focus:ring-2 focus:ring-offset-2 " +
  "disabled:opacity-50";

const VARIANTI = {
  primario:
    "bg-primario text-su-primario shadow-sm hover:bg-primario-scuro focus:ring-primario",
  secondario:
    "bg-superficie text-testo border-bordo-forte hover:bg-superficie-tenue focus:ring-fuoco",
  pericolo: "bg-negativo text-su-primario shadow-sm hover:opacity-90 focus:ring-negativo",
  discreto: "bg-transparent text-testo-tenue hover:bg-superficie-tenue focus:ring-fuoco",
};

const DIMENSIONI = {
  normale: "px-4 py-2 text-sm",
  grande: "px-6 py-2.5 text-sm",
  piccolo: "px-3 py-1.5 text-xs",
};

/**
 * @param {"primario"|"secondario"|"pericolo"|"discreto"} variante
 * @param {"normale"|"grande"|"piccolo"} dimensione
 * @param {{ larghezzaPiena?: boolean }} opzioni
 */
export function pulsante(
  variante = "primario",
  dimensione = "normale",
  { larghezzaPiena = false } = {},
) {
  return [
    BASE,
    VARIANTI[variante] ?? VARIANTI.primario,
    DIMENSIONI[dimensione] ?? DIMENSIONI.normale,
    larghezzaPiena ? "w-full" : "",
  ]
    .filter(Boolean)
    .join(" ");
}
