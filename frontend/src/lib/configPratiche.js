// nome_universita_id: 1=eCampus, 2=LinkCampus, 3=SSML, 4=A4U
// listino_tipoCorso_id: 1=MASTER, 2=MASTER AREA SCUOLA, 3=MASTER CLASSI DI CONCORSO,
// 4=CORSI DI PERFEZIONAMENTO, 5=PERCORSO DOCENTI, 6=CORSI DI FORMAZIONE,
// 7=CORSI DI ALTA FORMAZIONE, 8=LAUREE, 9=CORSI SINGOLI, 10=CORSI SPECIALI

export const BLOCCHI_PRATICHE = [
  {
    chiave: "ecampus",
    flagPermesso: "ecampus",
    titolo: "Università Telematica eCampus",
    logo: "/loghi/ecampus.png",
    nomeUniversitaId: 1,
    pulsanti: [
      {
        chiave: "prevalutazione",
        label: "Prevalutazione",
        tipo: "prevalutazione",
      }, // niente listino_tipoCorso_id: e' un sottosistema a parte
      {
        chiave: "corso_laurea",
        label: "Corso di Laurea",
        tipo: "pratica",
        listinoTipoCorsoIds: [8],
      },
      {
        chiave: "corsi_singoli",
        label: "Corsi Singoli",
        tipo: "pratica",
        listinoTipoCorsoIds: [9],
      },
      {
        chiave: "formazione_alta_formazione",
        label: "Formazione ed Alta Formazione",
        tipo: "pratica",
        listinoTipoCorsoIds: [6, 7],
      }, // DA CONFERMARE
      {
        chiave: "master",
        label: "Master",
        tipo: "pratica",
        listinoTipoCorsoIds: [1, 2, 3],
      }, // DA CONFERMARE: solo 1, o tutta la famiglia?
      {
        chiave: "corsi_perfezionamento",
        label: "Corsi di Perfezionamento",
        tipo: "pratica",
        listinoTipoCorsoIds: [4],
      },
      {
        chiave: "30_cfu",
        label: "30 CFU",
        tipo: "pratica",
        listinoTipoCorsoIds: [],
        semprebloccato: true,
      },
    ],
  },
  {
    chiave: "link_campus",
    flagPermesso: "link_campus",
    titolo: "Link Campus University",
    logo: "/loghi/link.png",
    nomeUniversitaId: 2,
    pulsanti: [
      {
        chiave: "corsi_perfezionamento",
        label: "Corsi di Perfezionamento",
        tipo: "pratica",
        listinoTipoCorsoIds: [4],
      },
      {
        chiave: "corsi_singoli",
        label: "Corsi Singoli",
        tipo: "pratica",
        listinoTipoCorsoIds: [9],
      },
    ],
  },
  {
    chiave: "ssml",
    flagPermesso: "corsi_speciali",
    titolo: "SSML Lamezia Terme",
    logo: "/loghi/ssml.png",
    nomeUniversitaId: 3,
    pulsanti: [
      {
        chiave: "corsi_perfezionamento",
        label: "Corsi di Perfezionamento",
        tipo: "pratica",
        listinoTipoCorsoIds: [4],
      },
      {
        chiave: "alta_formazione_lauree",
        label: "Alta Formazione per Lauree",
        tipo: "pratica",
        listinoTipoCorsoIds: [7],
      }, // DA CONFERMARE
      {
        chiave: "corso_laurea",
        label: "Corso di Laurea",
        tipo: "pratica",
        listinoTipoCorsoIds: [8],
      },
      {
        chiave: "prevalutazione",
        label: "Prevalutazione",
        tipo: "prevalutazione",
      },
      {
        chiave: "master",
        label: "Master",
        tipo: "pratica",
        listinoTipoCorsoIds: [1, 2, 3],
      }, // DA CONFERMARE
      {
        chiave: "corsi_singoli",
        label: "Corsi Singoli",
        tipo: "pratica",
        listinoTipoCorsoIds: [9],
      },
      {
        chiave: "corsi_speciali",
        label: "Corsi Speciali",
        tipo: "pratica",
        listinoTipoCorsoIds: [10],
      },
    ],
  },
  {
    chiave: "a4u",
    flagPermesso: "a4u",
    titolo: "Avatar4University",
    logo: "/loghi/a4u.png",
    nomeUniversitaId: 4,
    pulsanti: [
      {
        chiave: "corsi_perfezionamento",
        label: "Corsi di Perfezionamento",
        tipo: "pratica",
        listinoTipoCorsoIds: [4],
      },
      {
        chiave: "master",
        label: "Master",
        tipo: "pratica",
        listinoTipoCorsoIds: [1, 2, 3],
      }, // DA CONFERMARE
    ],
  },
];
