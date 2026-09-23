/**
 * Varianti delle superfici: pagine centrate, velo delle modali, schede e
 * titoli di sezione. Le varianti degli elenchi stanno in tabella.js.
 */

/**
 * Pagina che centra una scheda: accesso, recupero password, conferma.
 * Sono pagine normali su fondo chiaro, non finestre modali sopra un velo.
 */
export function paginaCentrata() {
  return "min-h-screen flex items-center justify-center bg-tela px-4";
}

/** Scheda principale di una pagina o di una sezione di modulo. */
export function scheda() {
  return "bg-superficie border border-bordo rounded-superficie shadow-xs";
}

/** Riquadro interno a una scheda: raggruppa campi affini. */
export function riquadro() {
  return "bg-superficie-tenue border border-bordo rounded-superficie p-4";
}

/**
 * Titolo di sezione. Con `separato` la riga sotto il titolo usa il colore dei
 * bordi, come ogni altra separazione dell'interfaccia.
 */
export function titoloSezione(variante = "semplice") {
  const base = "text-titolo-sezione text-testo-forte";
  return variante === "separato"
    ? `${base} border-b border-bordo pb-3 mb-6`
    : `${base} mb-4`;
}

/**
 * Sezione di un modulo lungo: titolo e descrizione a sinistra, campi a
 * destra. Le sezioni consecutive sono separate da una riga.
 */
export function sezioneModulo() {
  return "flex flex-wrap gap-x-10 gap-y-6 px-6 py-7 sm:px-8 border-b border-bordo last:border-b-0";
}

/** Colonna con titolo e descrizione di una sezione di modulo. */
export function introSezioneModulo() {
  return "flex flex-[1_1_200px] flex-col gap-1.5";
}

/** Colonna dei campi di una sezione di modulo, su una griglia di 6. */
export function campiSezioneModulo() {
  return "grid flex-[3_1_520px] grid-cols-6 gap-x-5 gap-y-4";
}
