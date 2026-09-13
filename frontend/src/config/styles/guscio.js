/**
 * Varianti del guscio dell'applicazione: barra laterale, barra superiore da
 * mobile, cassetto del menu e area del contenuto.
 *
 * Soglia: da lg in su la barra laterale e' fissa; sotto, il menu si apre da un
 * pulsante nella barra superiore.
 */

export function barraLaterale() {
  return (
    "fixed inset-y-0 left-0 z-30 hidden w-barra-laterale " +
    "border-r border-bordo bg-superficie lg:block"
  );
}

export function barraSuperiore() {
  return (
    "sticky top-0 z-20 flex h-barra-superiore items-center gap-3 " +
    "border-b border-bordo bg-superficie/90 px-4 backdrop-blur lg:hidden"
  );
}

export function veloCassetto() {
  return "fixed inset-0 z-40 bg-testo-forte/30 backdrop-blur-xs";
}

/** Il cassetto non supera l'85% dello schermo: resta visibile il velo da toccare. */
export function cassettoMenu() {
  return (
    "fixed inset-y-0 left-0 z-50 flex w-barra-laterale max-w-[85vw] flex-col " +
    "bg-superficie shadow-xl"
  );
}

/**
 * Area del contenuto. min-w-0 e' essenziale: senza, una tabella larga allarga
 * l'intera pagina invece di scorrere nel proprio contenitore.
 */
export function areaContenuto() {
  return "min-w-0 lg:pl-barra-laterale";
}
