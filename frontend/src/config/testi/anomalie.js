// Note brevi accanto ai campi, ricavate dalle anomalie dell'anagrafica (vedi
// lib/anomalieCampi.js). Il testo completo resta nel banner in cima alla pagina.
//
// I duplicati dei clienti sono cercati fra tutte le anagrafiche visibili,
// sottoscrittori e attuatori insieme: per questo la nota dice "anagrafiche" e
// non "sottoscrittori".
export const TESTI_ANOMALIE = {
  daCompilare: "Da compilare",
  pivaNonConforme: "Deve contenere 11 cifre numeriche",
  /** @param {boolean} femminile  Email e PEC; @param {number} quante  anagrafiche in conflitto */
  duplicatoAnagrafica: (femminile, quante) => {
    const participio = femminile ? "Duplicata" : "Duplicato";
    return quante === 1
      ? `${participio} con un'altra anagrafica`
      : `${participio} con ${quante} anagrafiche`;
  },
  // Per le aziende non si conta: una ragione sociale puo' contenere una virgola.
  duplicatoAzienda: (altre) =>
    altre ? "Duplicato con altre aziende" : "Duplicato con un'altra azienda",
};
