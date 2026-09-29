// Testi della Dashboard: benvenuto e scorciatoie verso le sezioni del menu.
export const TESTI_DASHBOARD = {
  titolo: "Dashboard",
  saluto: "Buon lavoro.",
  salutoConNome: (nome) => `Buon lavoro, ${nome}.`,
  introduzione: "Da qui raggiungi le sezioni della piattaforma.",
  // Titolo della sezione delle scorciatoie, solo per i lettori di schermo.
  titoloScorciatoie: "Le tue sezioni",
  // Una descrizione per ogni voce di VOCI_MENU tranne la Dashboard, per
  // percorso (config/routes/percorsi.js); un test le confronta con il menu.
  scorciatoie: {
    "/sottoscrittori": "Le persone iscritte ai percorsi.",
    "/attuatori": "Gli operatori della rete.",
    "/aziende": "Aziende della rete e gerarchia.",
    "/pratiche": "Pratiche per ateneo e stato.",
    "/prodotti": "Listino dei percorsi e prezzi.",
    "/edunews24": "Notizie, interpelli e selezioni.",
  },
};
