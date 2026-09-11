/**
 * Varianti dei controlli di immissione: input, select e textarea.
 *
 * Lo standard UI vieta i wrapper cosmetici, quindi qui non c'e' nessun
 * componente: il controllo resta quello nativo e da qui arriva solo la sua
 * configurazione visuale.
 *
 *   <label className={etichetta()}>Email</label>
 *   <input className={campo()} />
 *   <select className={campo("comodo")} />
 *
 * Perche' esiste: la stessa riga di classi era ripetuta 35 volte in una
 * variante, 27 in un'altra e 15 in una terza. Cambiare il colore della messa a
 * fuoco significava passare a mano su ottanta punti.
 *
 * Criterio: aspetto sobrio e coerente. Le due dimensioni differiscono solo per
 * la spaziatura interna, non per forma: il raggio e' uno solo per tutti i
 * controlli dell'applicazione.
 */

const BASE =
  "w-full bg-superficie-tenue border border-bordo rounded-controllo text-testo " +
  "focus:outline-none focus:ring-2 focus:ring-fuoco/20 focus:border-fuoco";

const DIMENSIONI = {
  compatto: "px-3 py-2 text-sm",
  comodo: "px-4 py-3 text-sm",
  minimo: "px-2 py-1.5 text-xs",
};

/**
 * @param {"compatto"|"comodo"|"minimo"} dimensione
 * @param {{ errore?: boolean }} opzioni  errore: il valore non ha superato la validazione
 */
export function campo(dimensione = "compatto", { errore = false } = {}) {
  const misura = DIMENSIONI[dimensione] ?? DIMENSIONI.compatto;
  const stato = errore
    ? "border-negativo focus:border-negativo focus:ring-negativo/20"
    : "";
  return [BASE, misura, stato].filter(Boolean).join(" ");
}

/**
 * Etichetta di un campo: maiuscoletto spaziato, come gia' in tutta
 * l'applicazione (84 occorrenze su due varianti che differivano di 2 pixel).
 */
export function etichetta() {
  return "block text-etichetta uppercase tracking-wider text-testo-tenue mb-1";
}

/** Messaggio di errore sotto un campo. */
export function erroreCampo() {
  return "mt-1 text-nota text-negativo";
}

/** Casella di spunta e pulsante di scelta. */
export function spunta() {
  return "w-4 h-4 rounded border-bordo-forte text-primario focus:ring-fuoco";
}
