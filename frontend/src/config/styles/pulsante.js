/**
 * Varianti dei pulsanti.
 *
 * Nessun wrapper cosmetico: il pulsante resta <button> nativo.
 *
 *   <button className={pulsante()}>Salva</button>
 *   <button className={pulsante("secondario", "piccolo")}>Modifica</button>
 *   <button className={pulsanteIcona()} aria-label="Apri il menu">...</button>
 *
 * L'anello di messa a fuoco compare solo da tastiera (focus-visible): chi usa
 * il mouse non lo vede dopo il clic, chi naviga con Tab sa sempre dove si trova.
 */

const BASE =
  "inline-flex items-center justify-center gap-2 font-medium whitespace-nowrap " +
  "rounded-controllo border transition-colors cursor-pointer " +
  "focus:outline-none focus-visible:ring-3 focus-visible:ring-fuoco/30 " +
  "disabled:opacity-50 disabled:cursor-not-allowed";

const SECONDARIO =
  "bg-superficie text-testo border-bordo-neutro shadow-xs " +
  "enabled:hover:border-bordo-controllo enabled:hover:text-testo-forte";

const VARIANTI = {
  primario: "border-transparent bg-primario text-su-primario shadow-xs hover:bg-primario-scuro",
  secondario: SECONDARIO,
  ausiliario: SECONDARIO,
  selezionato:
    "border-transparent bg-accento-tenue text-testo-forte shadow-xs " +
    "enabled:hover:bg-accento-tenue-hover",
  pericolo: "border-transparent bg-negativo text-su-primario shadow-xs hover:opacity-90",
  discreto: "border-transparent bg-transparent text-testo-tenue hover:bg-interazione-hover hover:text-testo-forte",
};

const DIMENSIONI = {
  normale: "px-4 py-2 text-sm",
  grande: "px-5 py-2.5 text-sm",
  piccolo: "px-3 py-1.5 text-xs",
};

/**
 * @param {"primario"|"secondario"|"ausiliario"|"selezionato"|"pericolo"|"discreto"} variante
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

/** Pulsante con sola icona su fondo trasparente: apertura e chiusura del menu. */
export function pulsanteIcona(variante = "neutro", dimensione = "normale") {
  const colore = variante === "pericolo"
    ? "text-negativo hover:bg-negativo-tenue hover:text-negativo-forte"
    : variante === "selezionato"
      ? "bg-interazione-selezionata text-primario hover:bg-interazione-selezionata-hover"
      : "text-testo-tenue hover:bg-interazione-hover hover:text-testo-forte";
  return (
    `inline-flex ${dimensione === "grande" ? "size-11" : "size-9"} shrink-0 items-center justify-center rounded-controllo ` +
    `${colore} transition-colors cursor-pointer ` +
    "focus:outline-none focus-visible:ring-3 focus-visible:ring-fuoco"
  );
}

/**
 * Azione di riga a sola icona, elevata: fondo bianco, bordo e ombra leggera.
 * Nelle tabelle segnala che la riga e' azionabile senza pesare come un pulsante
 * pieno; la riga stessa e' comunque cliccabile.
 */
export function pulsanteAzioneRiga(dimensione = "normale") {
  return (
    `inline-flex ${dimensione === "grande" ? "size-11" : "size-9"} shrink-0 items-center justify-center rounded-controllo ` +
    "border border-bordo bg-superficie text-testo-tenue shadow-sm " +
    "transition-colors cursor-pointer hover:bg-interazione-hover hover:border-bordo-forte hover:text-primario " +
    "focus:outline-none focus-visible:ring-3 focus-visible:ring-fuoco/30"
  );
}
