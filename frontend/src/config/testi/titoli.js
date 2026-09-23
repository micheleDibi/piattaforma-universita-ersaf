/** Scheda dei titoli di studio del curriculum. */
export const TESTI_TITOLI = {
  // Gli anni del diploma e dell'anno integrativo sono testo libero: sia un
  // anno solo sia un anno scolastico.
  segnapostoAnno: "es. 2015 oppure 2014/2015",
  diploma: {
    etichetta: "Titolo principale",
    titolo: "Diploma di istruzione secondaria",
    descrizione: "Requisito di accesso ai corsi universitari.",
  },
  campoDiploma: "Diploma",
  istituto: "Istituto",
  anno: "Anno",
  via: "Indirizzo (via)",
  citta: "Città",
  provincia: "Prov.",
  voto: "Voto (ricevuto / massimo)",
  votoRicevuto: "Voto ricevuto",
  votoMassimo: "Voto massimo",
  separatoreVoto: "/",
  integrativo: "Anno integrativo (se previsto)",
  presso: "Presso",
  universitario: {
    etichetta: "Ultimo titolo",
    titolo: "Titolo universitario",
    descrizione: "Titolo di studio più recente conseguito.",
  },
  titolo: "Titolo",
  // [valore salvato, etichetta]
  titoliUniversitari: [
    ["laurea_1_livello", "Laurea (Laurea 1° Livello)"],
    ["laurea_magistrale", "Laurea Magistrale"],
    ["laurea_specialistica", "Laurea Specialistica"],
    ["diploma_universitario", "Diploma Universitario"],
    ["laurea_vecchio_ordinamento", "Laurea vecchio ordinamento"],
  ],
  dataConseguimento: "Data conseguimento",
  corso: "Corso di laurea",
  universita: "Università",
  altri: {
    titolo: "Altri titoli",
    descrizione: "Post-laurea e titoli aggiuntivi, facoltativi.",
  },
  data: "Data",
  // Righe della tabella "Altri titoli", per suffisso delle colonne.
  righe: {
    pl1: "Post-laurea (1)",
    pl2: "Post-laurea (2)",
    ats1: "Altro titolo (1)",
    ats2: "Altro titolo (2)",
  },
  /** Nome accessibile di un campo della tabella: "Istituto, Post-laurea (1)". */
  campoRiga: (colonna, riga) => `${colonna}, ${riga}`,
};
