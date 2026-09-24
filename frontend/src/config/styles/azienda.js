/**
 * Composizioni della scheda azienda ("Modifica azienda", "Nuova azienda"),
 * della finestra "cambia padre" e della scheda Azienda di un attuatore. Usano
 * solo i ruoli e le varianti condivise: qui si fissa come si combinano.
 */
import { campo, etichetta } from "./campo.js";
import { riquadro, scheda } from "./superficie.js";
import { cellaNonApplicabile } from "./tabella.js";

// Asterisco dei campi obbligatori a 600, il peso dell'etichetta: nel design
// della scheda azienda e' uno span che lo eredita. CampoModulo, condiviso, lo
// rende a 700 (`font-bold`) come nel design del sottoscrittore, dove e' un <b>.
const ASTERISCO_AZIENDA = "[&_label>b]:font-semibold";

export const STILI_AZIENDA = {
  // Codici da leggere carattere per carattere: IBAN, BIC, codice nazionale.
  monospazio: "font-mono",
  // Riquadro con le sezioni della scheda.
  schedaModulo: `${scheda()} ${ASTERISCO_AZIENDA}`,
  // Finestra di creazione rapida: la griglia di 6 colonne di SezioneModulo,
  // con due campi per riga da sm in su.
  grigliaFinestra: `grid grid-cols-6 gap-x-5 gap-y-4.5 ${ASTERISCO_AZIENDA}`,

  // Gerarchia: riquadro con l'azienda padre e "Cambia padre" a destra.
  riquadroPadre: riquadro(),
  rigaPadre: "flex items-center justify-between gap-4",
  testoPadre: "flex min-w-0 flex-col gap-1",
  // L'etichetta dei campi senza il margine sotto: qui lo spazio e' il gap.
  etichettaPadre: "text-etichetta uppercase tracking-wider text-testo-tenue",
  // 15/500, come nel design.
  nomePadre: "text-evidenziato text-testo",

  // Conferma dell'azzeramento: il messaggio e, accanto, Conferma e Annulla.
  conferma: "flex flex-wrap items-center gap-3",
  messaggioConferma: "min-w-0 flex-[1_1_16rem]",
  pulsantiConferma: "flex shrink-0 gap-3",

  // Convenzioni: tabella, poi "Salva percentuali" a destra, 16px sotto.
  convenzioni: "flex flex-col gap-4",
  titoloConvenzioni: "text-titolo-sezione text-testo",
  azioniConvenzioni: "flex justify-end",
  ateneo: "text-sm font-semibold text-testo",
  cellaPercentuale: "relative flex items-center",
  // Combinazione non prevista: il trattino. Posizionata perche' il testo per
  // i lettori di schermo (sr-only, assoluto) resti dentro il contenitore che
  // scorre: senza, esce dalla tabella e fa scorrere in orizzontale la pagina.
  cellaNonPrevista: `${cellaNonApplicabile()} relative`,
  // 38px allineato a destra, con lo spazio per il "%" (30px).
  percentuale: `${campo("tabella")} pr-7.5 text-right`,
  // Sola lettura (scheda dell'attuatore): stessa geometria del campo.
  percentualeLettura: "flex h-9.5 w-full items-center justify-end pr-7.5 text-sm text-testo",

  // Scheda Azienda di un attuatore, dentro il pannello della scheda.
  attuatore: "flex flex-col gap-8",
  ricerca: "flex max-w-sm flex-col gap-4",
  azioniRicerca: "flex flex-wrap gap-3",
  testataAttuatore: "flex flex-wrap items-center justify-between gap-4",
  titoloAttuatore: "text-titolo-evidenziato text-testo",
  azioniAttuatore: "flex flex-wrap gap-3",
  datiAttuatore: "grid grid-cols-1 gap-x-5 gap-y-4.5 sm:grid-cols-2",
  etichettaDato: etichetta(),
  valoreDato: "text-sm text-testo break-words",
  separatore: "border-divisore",

  // Finestra di creazione rapida, in un portale sopra un velo come i dialoghi.
  velo: "fixed inset-0 z-50 flex items-center justify-center bg-testo-forte/30 p-4 backdrop-blur-xs",
  finestra: `${scheda()} w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 shadow-xl sm:p-8`,
  titoloFinestra: "text-lg font-semibold text-testo",
  descrizioneFinestra: "mt-1 text-sm text-testo-tenue",
  corpoFinestra: "my-6 flex flex-col gap-6",

  // Finestra "cambia padre".
  intestazioneFinestra: "mb-4 flex items-center justify-between border-b border-divisore pb-2.5",
  ricercaFinestra: "mb-4 flex gap-3",
  elencoFinestra: "h-[350px] overflow-y-auto rounded-riquadro border border-bordo bg-superficie",
  tabellaFinestra: "w-full border-collapse text-left",
  cellaFinestra: "px-4 py-2.5 text-sm text-testo",
  aggiornamentoFinestra: "mt-2 text-center text-nota text-testo-tenue",
};
