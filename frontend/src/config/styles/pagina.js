/**
 * Varianti dell'impaginazione: contenitore del contenuto e intestazione di
 * pagina. Il componente IntestazionePagina le compone.
 */

/**
 * Contenitore del contenuto di una pagina dentro il guscio.
 * @param {"pagina"|"modulo"} larghezza  pagina: elenchi; modulo: dettagli con un modulo
 */
export function contenutoPagina(larghezza = "pagina") {
  const massimo = larghezza === "modulo" ? "max-w-modulo" : "max-w-pagina";
  return `mx-auto w-full ${massimo} px-4 py-6 sm:px-6 lg:px-8 lg:py-8`;
}

export function intestazionePagina() {
  return "mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between";
}

export function titoloPagina() {
  return "text-titolo-pagina text-testo-forte";
}

export function descrizionePagina() {
  return "mt-1 text-sm text-testo-tenue";
}

/** Collegamento di ritorno sopra il titolo delle pagine di dettaglio. */
export function collegamentoIndietro() {
  return (
    "mb-3 inline-flex items-center gap-1.5 text-sm font-medium text-testo-tenue " +
    "transition-colors hover:text-testo-forte"
  );
}
