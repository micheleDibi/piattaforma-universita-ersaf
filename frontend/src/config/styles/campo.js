/**
 * Varianti dei controlli di immissione: input, select e textarea.
 *
 * Nessun componente: il controllo resta quello nativo e da qui arriva solo la
 * sua configurazione visuale, come chiede lo standard UI.
 *
 *   <label className={etichetta()}>Email</label>
 *   <input className={campo()} />
 *   <select className={campo("comodo")} />
 *
 * Aspetto: fondo bianco, bordo sottile e un'ombra appena percettibile; la
 * messa a fuoco usa la tinta dell'azione primaria. Le dimensioni differiscono
 * solo per la spaziatura interna: il raggio e' uno per tutti i controlli.
 */

const BASE =
  "w-full bg-superficie border rounded-controllo text-testo shadow-xs " +
  "placeholder:text-testo-tenue/70 transition-colors " +
  "focus:outline-none focus:ring-3 focus:ring-fuoco/15 focus:border-fuoco " +
  "disabled:bg-superficie-tenue disabled:text-testo-tenue";

const DIMENSIONI = {
  compatto: "px-3 py-2 text-sm",
  comodo: "px-4 py-2.5 text-sm",
  ampio: "min-h-12 px-4 py-2.5 text-base",
  minimo: "px-2 py-1.5 text-xs",
};

/**
 * @param {"compatto"|"comodo"|"ampio"|"minimo"} dimensione
 * @param {{ errore?: boolean }} opzioni  errore: il valore non ha superato la validazione
 */
export function campo(dimensione = "compatto", { errore = false } = {}) {
  const misura = DIMENSIONI[dimensione] ?? DIMENSIONI.compatto;
  const stato = errore
    ? "border-negativo focus:border-negativo focus:ring-negativo/15"
    : dimensione === "ampio" ? "border-bordo-controllo" : "border-bordo";
  return [BASE, misura, stato].filter(Boolean).join(" ");
}

/** Etichetta di un campo: maiuscoletto spaziato. */
export function etichetta(variante = "compatta") {
  if (variante === "leggibile") return "block text-sm font-medium text-testo-forte mb-2";
  return "block text-etichetta uppercase tracking-wider text-testo-tenue mb-1.5";
}

/** Messaggio di errore sotto un campo. */
export function erroreCampo() {
  return "mt-1.5 text-nota text-negativo";
}

/** Casella di spunta e pulsante di scelta. */
export function spunta() {
  return "w-4 h-4 rounded border-bordo-forte text-primario focus:ring-fuoco";
}
