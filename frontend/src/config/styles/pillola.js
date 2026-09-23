/**
 * Varianti delle pillole: stato dell'anagrafica ("Attivo"), contatto
 * verificato, etichetta di una sezione ("Titolo principale"). La spunta,
 * quando serve, e' l'icona Check del catalogo (size-3).
 *
 *   <span className={pillola("positivo")}>Attivo</span>
 *   <span className={pillola("primario", "etichetta")}>Titolo principale</span>
 */

const BASE = "inline-flex items-center gap-1 whitespace-nowrap rounded-full leading-[normal]";

const TONI = {
  positivo: "bg-positivo-tenue text-positivo",
  negativo: "bg-negativo-tenue text-negativo",
  primario: "bg-primario-tenue text-primario",
  neutro: "border border-bordo-controllo-tenue bg-superficie text-testo-attenuato",
};

const FORME = {
  // 12/600, 3/10: stato nella testata, contatto verificato.
  normale: "px-2.5 py-0.75 text-xs font-semibold",
  // 13/600, 5/12: stato dell'utente.
  grande: "px-3 py-1.25 text-dettaglio font-semibold",
  // 11/600 maiuscolo: etichetta di una sezione.
  etichetta: "px-2.5 py-0.75 text-etichetta uppercase tracking-wider",
};

/**
 * @param {"positivo"|"negativo"|"primario"|"neutro"} tono
 * @param {"normale"|"grande"|"etichetta"} forma
 */
export function pillola(tono = "neutro", forma = "normale") {
  return [BASE, TONI[tono] ?? TONI.neutro, FORME[forma] ?? FORME.normale].join(" ");
}
