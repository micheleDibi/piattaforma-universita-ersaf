// Percentuali di convenzione universitaria di un'azienda, condivise dalla
// scheda azienda e dalla scheda azienda dell'attuatore. Stanno fuori da un
// file di componente perche' un file di componente deve esportare solo
// componenti, o il fast refresh di Vite ricarica l'intera pagina.
export const CAMPI_PERCENTUALI = [
  ["universita_ecampus_lauree", "eCampus - Lauree"],
  ["universita_ecampus_master", "eCampus - Master"],
  ["universita_link_lauree", "Link - Lauree"],
  ["universita_link_master", "Link - Master"],
  ["universita_SSML_lauree", "SSML - Lauree"],
  ["universita_SSML_master", "SSML - Master"],
  ["universita_A4U_master", "A4U - Master"],
  ["universita_A4U_perfezionamenti", "A4U - Perfezionamenti"],
];

// Righe della tabella: ateneo e campo per Lauree, Master, Perfezionamenti
// (intestazioni in TESTI_AZIENDA.convenzioni.tipologie); null = la
// convenzione non prevede quella tipologia.
export const CONVENZIONI = [
  ["eCampus", "universita_ecampus_lauree", "universita_ecampus_master", null],
  ["Link", "universita_link_lauree", "universita_link_master", null],
  ["SSML", "universita_SSML_lauree", "universita_SSML_master", null],
  ["A4U", null, "universita_A4U_master", "universita_A4U_perfezionamenti"],
];
