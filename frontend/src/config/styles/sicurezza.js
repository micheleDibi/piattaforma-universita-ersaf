import { campo, etichetta } from "./campo.js";
import { pulsante } from "./pulsante.js";
import { titoloSezione } from "./superficie.js";

// Sezione Sicurezza del profilo: elenco dei metodi, moduli inline di
// attivazione e disattivazione, riquadro del QR. Nessuno stile nei componenti.
export const STILI_SICUREZZA = {
  sezione: "min-w-0 space-y-6",
  titoloSezione: titoloSezione(),
  introduzione: "mt-1 text-sm leading-relaxed text-testo-tenue",
  proposto: "mt-3 text-sm font-medium text-testo-forte",
  elenco: "divide-y divide-bordo",
  riga: "flex flex-col gap-4 py-5 first:pt-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between",
  testata: "flex min-w-0 items-start gap-3",
  icona: "mt-0.5 size-icona shrink-0 text-testo-tenue",
  nome: "text-sm font-semibold text-testo-forte",
  descrizione: "mt-1 text-sm leading-relaxed text-testo-tenue",
  stato: "mt-2 text-sm text-testo",
  statoAttivo: "mt-2 text-sm font-medium text-positivo",
  azioni: "flex shrink-0 flex-wrap gap-2",
  azionePrimaria: pulsante("primario"),
  azioneSecondaria: pulsante("secondario"),
  azioneDiscreta: pulsante("discreto"),
  modulo: "w-full space-y-4 rounded-superficie border border-bordo bg-superficie-tenue p-4 sm:p-5",
  passi: "text-sm leading-relaxed text-testo",
  etichetta: etichetta(),
  campo: campo("comodo"),
  qr: "inline-block rounded-superficie border border-bordo bg-superficie p-3",
  qrImmagine: "block size-44",
  chiave: "mt-1 block font-mono text-sm tracking-wider text-testo-forte [overflow-wrap:anywhere]",
  elencoPasskey: "mt-3 space-y-2",
  passkey: "flex flex-wrap items-center justify-between gap-x-4 gap-y-2 rounded-controllo border border-bordo bg-superficie px-3 py-2",
  passkeyNome: "text-sm font-medium text-testo-forte",
  passkeyDettagli: "text-nota text-testo-tenue",
};
