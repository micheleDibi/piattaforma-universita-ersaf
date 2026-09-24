/**
 * Composizioni della scheda di sottoscrittori e attuatori, costruite sulle
 * varianti condivise (campo, pillola, superficie, tabella) e sui soli ruoli
 * del tema. Le misure sono quelle del design "Modifica sottoscrittore".
 */
import { campo, sceltaInLinea, sceltaRiquadro } from "./campo.js";
import { pillola } from "./pillola.js";
import { separatoreTratteggiato } from "./superficie.js";
import { statoVuoto } from "./tabella.js";

// Classi statiche: Tailwind non vede quelle composte a runtime. Stessa regola
// di CampoModulo, per i campi scritti a mano nella griglia di 6.
const COLONNE = {
  1: "col-span-6 sm:col-span-1",
  2: "col-span-6 sm:col-span-2",
  3: "col-span-6 sm:col-span-3",
  4: "col-span-6 sm:col-span-4",
  5: "col-span-6 sm:col-span-5",
  6: "col-span-6",
};

const GRIGLIA_AUTO =
  "grid grid-cols-[repeat(auto-fit,minmax(min(100%,15rem),1fr))]";

export const STILI_ANAGRAFICA = {
  // Testata: nome, codice fiscale in monospazio 13px, pillola dello stato.
  nomeTestata: "whitespace-nowrap font-medium text-testo",
  codiceTestata: "font-mono text-dettaglio",
  // Scheda senza dati ("Esami") e ripiego delle schede non previste.
  // Interlinea normale come nel design (text-sm porterebbe 20px).
  vuoto: `${statoVuoto()} leading-[normal]`,
  titoloVuoto: "mb-2 text-titolo-sezione text-testo",
  schedaCorrente: "font-medium text-primario capitalize",
  errore: "px-8 py-14 text-center text-sm text-negativo",
  // Griglia di 6 dentro una scheda evidenziata (diploma).
  grigliaCampi: "grid grid-cols-6 gap-x-5 gap-y-4.5",
  // Parte facoltativa sotto il tratteggio: anno integrativo.
  parteFacoltativa: `${separatoreTratteggiato()} flex flex-col gap-3.5`,
  grigliaSecondaria: "grid grid-cols-6 gap-x-4 gap-y-3.5",
  // Didascalia di un gruppo di campi: "Altri recapiti", "Anno integrativo".
  didascalia: "text-xs leading-[normal] font-medium text-testo-attenuato",
  // Voto ricevuto e massimo sulla stessa riga, separati da "/".
  voto: "flex items-center gap-2",
  separatoreVoto: "text-testo-attenuato",
  // Tabella "Altri titoli": nome della riga.
  titoloRiga: "text-dettaglio text-testo-secondario",
  // Contatti: colonna dei campi, schede di email e cellulare, altri recapiti.
  colonnaContatti: "flex flex-col gap-5",
  messaggiContatti: "flex flex-col gap-3 empty:hidden",
  messaggioAttivazione: "text-sm text-testo-tenue",
  grigliaRecapiti: `${GRIGLIA_AUTO} gap-4`,
  schedaRecapito:
    "flex min-w-0 flex-col gap-2.5 rounded-evidenza border border-evidenza-bordo bg-evidenza px-4.5 py-4",
  // Testata alta quanto la pillola "Verificata" (21px): il pulsante "Verifica"
  // (32px) sborda con un margine negativo, cosi' i campi di email e cellulare
  // restano alla stessa altezza qualunque sia lo stato della verifica.
  testataRecapito: "flex min-h-5.25 items-center justify-between gap-2",
  pulsanteRecapito: "-my-1.5",
  etichettaRecapito:
    "text-xs leading-[normal] font-semibold uppercase tracking-wider text-primario",
  spuntaRecapito: "size-3 shrink-0",
  altriRecapiti: "flex flex-col gap-3",
  grigliaAltriRecapiti: `${GRIGLIA_AUTO} gap-x-5 gap-y-4`,
  campoSecondario: "flex min-w-0 flex-col",
  // Curriculum: casella a tutta riga, caselle a scheda, suffisso "%".
  // Interlinea normale come nel design: la riga resta alta quanto la casella.
  sceltaIscrizione: `${sceltaInLinea()} col-span-6 leading-[normal]`,
  sceltaConvalida: `${sceltaRiquadro()} leading-[normal]`,
  grigliaConvalida: "grid grid-cols-[repeat(auto-fit,minmax(min(100%,10.625rem),1fr))] gap-3",
  conSuffisso: "relative",
  // Utente: stato cliccabile, riquadro del padre, azioni, cronologia.
  cellaStato: "flex h-controllo items-center",
  riquadroPadre:
    "flex h-controllo items-center justify-between gap-2.5 rounded-controllo border border-bordo " +
    "bg-superficie-tenue pr-1 pl-3.5",
  nomePadre: "truncate text-sm font-medium text-testo",
  azioniUtente: "col-span-6 flex flex-wrap items-center justify-end gap-3",
  avvisoUtente: "px-6 pt-6 sm:px-8",
  cronologia: "grid grid-cols-[repeat(auto-fit,minmax(min(100%,10rem),1fr))] gap-4",
  valoreCronologia: "text-sm leading-[normal] text-testo",
  // Abilitazioni dell'attuatore: righe a scheda con interruttore.
  abilitazioni: "flex flex-col gap-3",
  rigaAbilitazione: `${sceltaRiquadro()} justify-between`,
};

/** Cella di un campo scritto senza CampoModulo nella griglia di 6. */
export function colonnaCampo(colonne = 3) {
  return `flex min-w-0 flex-col ${COLONNE[colonne] ?? COLONNE[3]}`;
}

const TONI_NOTA = { neutra: "text-testo-tenue", avviso: "text-attenzione-nota" };

/**
 * Nota dentro la scheda di un recapito: lo spazio lo da' la scheda (gap 10),
 * l'interlinea e' quella del design (1,45).
 * @param {"neutra"|"avviso"} tono
 */
export function notaRecapito(tono = "neutra") {
  return `text-nota ${TONI_NOTA[tono] ?? TONI_NOTA.neutra}`;
}

/** Codice fiscale: campo del modulo in monospazio, ambra se ha un'anomalia. */
export function campoCodiceFiscale(avviso = false) {
  return `${campo("comodo", { avviso })} font-mono`;
}

/**
 * Data in evidenza ("Data conseguimento"): alta come il titolo accanto (46)
 * ma col testo dei campi normali (14/400), come nel design. La regola sulla
 * data vince sul corpo di `evidenziato` per specificita'.
 */
export function campoDataEvidenziata() {
  return `${campo("evidenziato")} [&[type=date]]:text-sm [&[type=date]]:font-normal`;
}

/**
 * Data in una colonna sola ("Abilitazioni"): rientro 6 e testo 13px per far
 * stare gg/mm/aaaa. `!` perche' la regola delle date di `campo()` ha una
 * specificita' maggiore.
 */
export function campoDataStretta() {
  return `${campo("comodo")} px-1.5! text-dettaglio!`;
}

/** Campo con l'unita' di misura dentro, a destra ("%"). */
export function campoConSuffisso() {
  return `${campo("comodo")} pr-7.5`;
}

/**
 * Stato dell'utente: pillola grande che si clicca per cambiarlo.
 * @param {boolean} attivo
 */
export function pillolaStato(attivo) {
  return (
    `${pillola(attivo ? "positivo" : "negativo", "grande")} cursor-pointer transition-colors ` +
    `${attivo ? "hover:bg-positivo-bordo" : "hover:bg-negativo-bordo"} ` +
    "focus:outline-none focus-visible:ring-3 focus-visible:ring-fuoco/30"
  );
}

/** Interruttore delle abilitazioni: binario primario se attivo. */
export function interruttore(attivo) {
  return (
    "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors cursor-pointer " +
    "focus:outline-none focus-visible:ring-3 focus-visible:ring-fuoco/30 motion-reduce:transition-none " +
    (attivo ? "bg-primario" : "bg-testo-spento")
  );
}

/** Levetta dell'interruttore. */
export function levettaInterruttore(attivo) {
  return (
    "inline-block size-4 rounded-full bg-superficie transition-transform motion-reduce:transition-none " +
    (attivo ? "translate-x-6" : "translate-x-1")
  );
}
