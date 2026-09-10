// La convenzione booleana della piattaforma Instant Developer, lato frontend.
//
// Nelle tabelle legacy il vero non e' 1: e' -1, tranne che su
// universita_immatricolato, che nasce da una tendina e usa 1. Il conteggio sui
// dati reali sta in backend/src/comune/flag_legacy.py.
//
// Serviva perche' la stessa casella veniva letta con due convenzioni diverse:
// ImmatricolazioniIscrizioni confrontava === -1 (giusto),
// AbilitazioniProfessionali === 1 (sbagliato), e le 234 righe storiche salvate
// a -1 apparivano non spuntate.
//
// Il backend canonicalizza in scrittura e in lettura, quindi qui basta
// riconoscere "qualunque valore diverso da zero".

/** True se il valore legacy rappresenta il vero, con qualunque convenzione. */
export function eVero(valore) {
  if (valore === true) return true;
  if (valore === false || valore === null || valore === undefined) return false;
  const numero = Number(valore);
  return Number.isFinite(numero) && numero !== 0;
}

/** Il valore da inviare per una casella spuntata o meno. */
export function daCasella(spuntata, vero = -1) {
  return spuntata ? vero : 0;
}
