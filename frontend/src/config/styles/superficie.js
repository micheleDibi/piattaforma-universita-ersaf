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
