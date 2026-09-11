/**
 * Varianti delle superfici che contengono i controlli: schede, riquadri,
 * intestazioni di sezione e tabelle.
 *
 *   <section className={scheda()}>
 *     <h2 className={titoloSezione()}>Dati anagrafici</h2>
 *   </section>
 *
 * Perche' esiste: le stesse combinazioni di sfondo, bordo, ombra e raggio
 * comparivano a mano in ogni pagina, con raggi diversi per lo stesso ruolo.
 */

/**
 * Pagina che centra una scheda: accesso, recupero password, conferma.
 *
 * Queste schermate erano costruite come finestre modali sopra un velo nero, ma
 * dietro non c'e' nessuna pagina: il velo copriva il vuoto e il risultato era
 * uno sfondo scuro. Qui sono pagine normali su fondo chiaro.
 */
export function paginaCentrata() {
  return "min-h-screen flex items-center justify-center bg-superficie-tenue px-4";
}

/** Velo di una finestra modale vera, sopra il contenuto della pagina. */
export function velo() {
  return (
    "fixed inset-0 z-50 flex items-center justify-center " +
    "bg-testo-forte/40 backdrop-blur-sm px-4"
  );
}

/** Scheda principale di una pagina o di una sezione di form. */
export function scheda() {
  return "bg-superficie border border-bordo rounded-superficie shadow-sm";
}

/** Riquadro interno a una scheda: raggruppa campi affini. */
export function riquadro() {
  return "bg-superficie-tenue border border-bordo rounded-superficie p-4";
}

/**
 * Titolo di sezione. Con `separato` la riga sotto il titolo: oggi quella riga
 * eredita il colore del testo, quindi e' quasi nera e pesa troppo. Qui usa il
 * colore dei bordi, come ogni altra separazione dell'interfaccia.
 */
export function titoloSezione(variante = "semplice") {
  const base = "text-titolo-sezione text-testo";
  return variante === "separato"
    ? `${base} border-b border-bordo pb-2 mb-6`
    : `${base} mb-4`;
}

/** Contenitore di una tabella larga: lo scorrimento resta dentro il riquadro. */
export function contenitoreTabella() {
  return (
    "w-full overflow-x-auto bg-superficie border border-bordo " +
    "rounded-superficie shadow-sm"
  );
}

/** Intestazione di tabella. */
export function intestazioneTabella() {
  return "bg-superficie-tenue text-etichetta text-testo-tenue text-left";
}

/** Riga di tabella cliccabile. */
export function rigaTabella() {
  return "border-t border-bordo hover:bg-superficie-tenue transition-colors";
}
