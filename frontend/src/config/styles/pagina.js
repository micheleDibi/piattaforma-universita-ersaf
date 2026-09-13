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

/**
 * Titolo e azioni sulla stessa riga a ogni larghezza: da schermo stretto
 * l'azione resta accanto al titolo invece di finire su una riga propria.
 * Le azioni accorciano la loro etichetta, non cambiano posto.
 */
export function intestazionePagina() {
  return "mb-6 flex flex-row items-center justify-between gap-3";
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
