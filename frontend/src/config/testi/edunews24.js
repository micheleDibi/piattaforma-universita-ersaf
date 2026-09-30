// Testi della sezione EduNews24: modulo in Dashboard e pagina /edunews24.
// "Carica altri", "Caricamento..." e la fine dell'elenco restano in TESTI_ELENCO.

const secondi = (n) => (n === 1 ? "1 secondo" : `${n} secondi`);
const minuti = (n) => (n === 1 ? "1 minuto" : `${n} minuti`);
// Attesa prima di riprovare: la pausa raddoppia fino a un'ora, quindi dai 90
// secondi si conta in minuti, arrotondati per eccesso.
const attesa = (n) => (n >= 90 ? minuti(Math.ceil(n / 60)) : secondi(n));

// Prima parte dell'errore del primo caricamento della pagina, con il genere
// della sezione.
const NON_CARICATE = {
  notizie: "Notizie non caricate",
  interpelli: "Interpelli non caricati",
  "selezione-personale": "Selezione del personale non caricata",
};

export const TESTI_EDUNEWS24 = {
  nome: "EduNews24",
  titoloPagina: "EduNews24",
  // Presentazione della testata; la seconda frase solo con la funzione attiva.
  presentazione: "Notizie, interpelli e selezioni del personale dalla redazione di EduNews24.",
  presentazioneTitoli: "Ogni titolo apre l'articolo su EduNews24.",
  fonte: "Fonte: EduNews24",
  nuovaScheda: "(si apre in una nuova scheda)",

  sezioni: { notizie: "Notizie", interpelli: "Interpelli", "selezione-personale": "Selezione personale" },
  sezioniBrevi: { notizie: "Notizie", interpelli: "Interpelli", "selezione-personale": "Selezione" },
  etichettaSezioni: "Sezioni di EduNews24",
  vediTutto: {
    notizie: "Tutte le notizie",
    interpelli: "Tutti gli interpelli",
    "selezione-personale": "Tutte le selezioni",
  },

  etichettaSocial: "EduNews24 sui social",
  social: {
    facebook: "EduNews24 su Facebook",
    instagram: "EduNews24 su Instagram",
    tiktok: "EduNews24 su TikTok",
  },
  socialBrevi: { facebook: "Facebook", instagram: "Instagram", tiktok: "TikTok" },

  // Folio: ora dell'ultimo aggiornamento, oppure della copia che si sta vedendo.
  aggiornatoAlle: (ora) => `Aggiornato alle ${ora}`,
  aggiornatoIl: (data, ora) => `Aggiornato il ${data} alle ${ora}`,
  nonAggiornatoDalle: (ora) => `Non aggiornato dalle ${ora}`,
  nonAggiornatoDal: (data, ora) => `Non aggiornato dal ${data} alle ${ora}`,
  // Copia stantia senza l'istante dell'ultimo aggiornamento.
  nonAggiornato: "Contenuti non aggiornati",
  stantioEsteso: "Contenuti non aggiornati: EduNews24 non risponde e stai vedendo l'ultima copia disponibile.",

  // Fascia delle miniature e tabellone del modulo.
  fascia: "Altre notizie di EduNews24",
  precedenti: "Notizie precedenti",
  successive: "Notizie successive",
  inEvidenza: (titolo) => `In evidenza: ${titolo}`,
  tabellone: { interpelli: "Altri interpelli", "selezione-personale": "Altre selezioni" },

  // Pagina: titolo della griglia sotto la prima pagina delle notizie.
  altreNotizie: "Altre notizie",

  // Timbro della voce principale e targa della pagina.
  scadeIl: "Scade il",
  pubblicatoIl: "Pubblicato il",
  senzaScadenza: "Senza scadenza",
  scadenzaNonIndicata: "Scadenza non indicata",
  scadenzaSr: (data) => `Scadenza: ${data}`,
  pubblicazioneSr: (data) => `Pubblicato il ${data}`,
  classe: (classe) => `Classe ${classe}`,
  classeSr: (classe) => `Classe di concorso ${classe}`,

  // Distintivi di stato della selezione del personale.
  stati: {
    scaduto: "Scaduto",
    chiuso: "Chiuso",
    scadeOggi: "Scade oggi",
    scadeDomani: "Scade domani",
    scadeTra: (n) => `Scade tra ${n} giorni`,
    aperto: "Aperto",
  },

  // Metadati.
  nazionale: "Nazionale",
  altreRegioni: (n) => `+${n}`,
  altreRegioniSr: (n, elenco) => `e altre ${n}: ${elenco}`,
  figura: (figura) => `Figura: ${figura}`,
  posti: (n) => `Posti: ${n}`,
  oggi: "Oggi",
  ieri: "Ieri",
  senzaData: "Senza data",

  // Video.
  guardaVideo: "Guarda il video",
  guardaVideoNome: (titolo) => `Guarda il video: ${titolo}`,
  durataEstesa: (m, s) => `durata ${[m ? minuti(m) : "", s ? secondi(s) : ""].filter(Boolean).join(" e ")}`,
  video: "Video",
  videoNonDisponibile: "Il video non si può riprodurre qui.",
  guardaSuEduNews24: "Guardalo su EduNews24",

  // Filtri della pagina.
  categorie: "Categorie",
  tutteLeCategorie: "Tutte",
  soloVideo: "Solo video",
  area: "Area",
  tutteLeAree: "Tutte le aree",
  tuttaItalia: "Tutta Italia",
  regioni: "Regioni",
  filtriAttivi: "Filtri attivi",
  filtroCategoria: (categoria) => `Categoria: ${categoria}`,
  filtroArea: (area) => `Area: ${area}`,
  rimuoviFiltro: (filtro) => `Rimuovi il filtro ${filtro}`,
  rimuoviFiltri: "Rimuovi filtri",
  rimuoviIlFiltro: "Rimuovi il filtro",
  rimuoviIFiltri: "Rimuovi i filtri",

  // Testo nascosto dello scheletro, in role="status".
  caricamento: {
    notizie: "Caricamento delle notizie di EduNews24",
    interpelli: "Caricamento degli interpelli di EduNews24",
    "selezione-personale": "Caricamento della selezione del personale di EduNews24",
  },

  // Stato vuoto del modulo: titolo e riga.
  vuotiModulo: {
    notizie: {
      titolo: "Nessuna notizia da mostrare per ora.",
      riga: "Le nuove notizie di EduNews24 compaiono qui.",
    },
    interpelli: {
      titolo: "Nessun interpello recente.",
      riga: "I nuovi interpelli compaiono qui.",
    },
    "selezione-personale": {
      titolo: "Nessuna selezione aperta in questo momento.",
      riga: "Quelle chiuse o scadute restano nella pagina EduNews24.",
    },
  },

  // Stato vuoto della pagina, senza e con filtri (lib/edunews24.js, testiVuotoPagina).
  vuotiPagina: {
    notizie: {
      titolo: "Nessuna notizia da mostrare per ora.",
      riga: "Le nuove notizie compariranno qui.",
      titoloFiltrato: "Nessuna notizia per questi filtri.",
      rigaFiltrata: "Prova un'altra categoria o rimuovi i filtri.",
      rigaFiltrataUno: "Prova un'altra categoria o rimuovi il filtro.",
    },
    interpelli: {
      titolo: "Nessun interpello da mostrare per ora.",
      titoloArea: (regione) => `Nessun interpello in ${regione}.`,
      rigaFiltrata: "Prova un'altra area o rimuovi il filtro.",
    },
    "selezione-personale": {
      titolo: "Nessuna selezione da mostrare per ora.",
      titoloNazionale: "Nessuna selezione nazionale.",
      titoloArea: (regione) => `Nessuna selezione in ${regione}.`,
      rigaFiltrata: "Prova un'altra area o rimuovi il filtro.",
    },
  },

  // Errori, composti secondo il contesto (lib/edunews24.js). riprovaTra e
  // riprovaPresto sono la nota accanto a "Riprova", nel modulo e al primo
  // caricamento della pagina; l'avviso della pagina non dice i secondi.
  erroreModulo: "EduNews24 non risponde in questo momento.",
  erroreModuloDettaglio: "Il resto della piattaforma funziona normalmente.",
  riprovaTra: (n) => `Puoi riprovare tra ${attesa(n)}.`,
  riprovaPresto: "Puoi riprovare tra qualche istante.",
  errorePagina: (sezione) =>
    `${NON_CARICATE[sezione] ?? NON_CARICATE.notizie}: EduNews24 non risponde in questo momento.`,
  erroreAltre: "Altre voci non caricate: EduNews24 non risponde.",
  filtroNonValido: "Questo filtro non è più disponibile.",
  ripartito: "L'elenco è stato aggiornato: riparte dalle voci più recenti.",
  // Prima pagina senza voci da mostrare ma con un seguito da caricare.
  vociSuccessive: "Nessuna voce da mostrare in questa parte dell'elenco: carica le successive.",
  cursore: "L'elenco di EduNews24 è cambiato mentre lo scorrevi. Ricaricalo dalla prima pagina.",
  riprova: "Riprova",

  // Funzione disattivata.
  disattivataTitolo: "EduNews24 non è attivo su questa piattaforma.",
  disattivata: "Quando verrà attivato, qui troverai notizie, interpelli e selezioni del personale.",

  // Annunci nascosti dopo un cambio chiesto dall'utente: filtri della pagina,
  // "Riprova" del modulo.
  annunci: { aggiornato: "Elenco aggiornato", vuoto: "Nessuna voce trovata" },
};
