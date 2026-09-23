import { TESTI_ANOMALIE } from "../config/testi/anomalie.js";

/*
 * Note per campo ricavate dalle frasi di `anomalie` che il backend allega a
 * GET /clienti/{id} e GET /aziende/{id}. Le frasi nascono in:
 * - backend/src/clienti/schemas.py (codice fiscale ed email non validi);
 * - backend/src/clienti/anomalie.py (duplicati dei clienti);
 * - backend/src/aziende/routers.py (anomalie delle aziende).
 * tests/anomalieCampi.test.js controlla che quelle frasi esistano ancora. Una
 * frase non riconosciuta non produce note: resta soltanto nel banner.
 */

const conIniziale = (testo) => testo.charAt(0).toUpperCase() + testo.slice(1);

/** Etichette dei duplicati in clienti/anomalie.py: campo del modulo e genere. */
export const DUPLICATI_CLIENTE = {
  "Codice fiscale": { campo: "codiceFiscale", femminile: false },
  Email: { campo: "email", femminile: true },
  Telefono: { campo: "telefono", femminile: false },
  Cellulare: { campo: "cellulare", femminile: false },
  PEC: { campo: "pec", femminile: true },
  "Numero documento": { campo: "nDocumento", femminile: false },
};

// Ogni regola: espressione sulla frase intera e [campo, nota] dal risultato.
const REGOLE = {
  cliente: [
    [/^Codice fiscale non valido: (.+?)\.?$/, (m) => ["codiceFiscale", conIniziale(m[1])]],
    [/^Email non valida: (.+?)\.?$/, (m) => ["email", conIniziale(m[1])]],
    [
      /^(Codice fiscale|Email|Telefono|Cellulare|PEC|Numero documento) duplicato con: (.+)$/,
      (m) => {
        const { campo, femminile } = DUPLICATI_CLIENTE[m[1]];
        // Un nominativo per ogni anagrafica in conflitto: gli omonimi contano.
        return [campo, TESTI_ANOMALIE.duplicatoAnagrafica(femminile, m[2].split(", ").length)];
      },
    ],
  ],
  azienda: [
    [/^Codice Fiscale mancante$/, () => ["azienda_codiceFiscale", TESTI_ANOMALIE.daCompilare]],
    [
      /^Codice Fiscale duplicato con: (.+)$/,
      (m) => ["azienda_codiceFiscale", TESTI_ANOMALIE.duplicatoAzienda(m[1].includes(", "))],
    ],
    [/^Partita IVA mancante$/, () => ["azienda_partitaIVA", TESTI_ANOMALIE.daCompilare]],
    [/^Partita IVA non conforme/, () => ["azienda_partitaIVA", TESTI_ANOMALIE.pivaNonConforme]],
  ],
};

/**
 * @param {string[]|null|undefined} anomalie  frasi del backend
 * @param {"cliente"|"azienda"} entita
 * @returns {Record<string, string[]>}  campo del modulo -> note brevi, nell'ordine del backend
 */
export function anomaliePerCampo(anomalie, entita) {
  const regole = REGOLE[entita] ?? [];
  const note = {};
  for (const frase of Array.isArray(anomalie) ? anomalie : []) {
    if (typeof frase !== "string") continue;
    const testo = frase.trim();
    for (const [schema, nota] of regole) {
      const risultato = testo.match(schema);
      if (!risultato) continue;
      const [campo, voce] = nota(risultato);
      (note[campo] ??= []).push(voce);
      break;
    }
  }
  return note;
}

const pulito = (valore) => String(valore ?? "").trim();

/**
 * Tiene solo le note dei campi ancora uguali al valore salvato (confronto dopo
 * trim; un campo assente vale ""): appena si modifica il campo, la nota sparisce.
 * @param {Record<string, string[]>} note
 * @param {Record<string, unknown>} valori  valori correnti del modulo
 * @param {Record<string, unknown>} salvati  valori letti dal server
 * @returns {Record<string, string[]>}
 */
export function noteVisibili(note, valori, salvati) {
  return Object.fromEntries(
    Object.entries(note ?? {}).filter(
      ([campo]) => pulito(valori?.[campo]) === pulito(salvati?.[campo]),
    ),
  );
}
