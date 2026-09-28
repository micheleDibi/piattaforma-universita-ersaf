// Pagina Pratiche senza ateneo: dai gruppi di GET /pratiche/conteggi alla
// striscia dei totali e alle tabelle degli atenei. I blocchi arrivano come
// parametro (BLOCCHI_PRATICHE in configPratiche.js, che importa i loghi).

// Colonne degli stati, nell'ordine del design. Gli id sono quelli di
// pratiche_stati (codici Bozza, InLavorazione, AttesaModifica, Conclusa,
// Caricata, Rifiutata); la chiave sceglie etichetta e colore.
export const STATI_PANNELLO = [
  { id: 6, chiave: "bozza" },
  { id: 4, chiave: "lavorazione" },
  { id: 2, chiave: "attesa" },
  { id: 3, chiave: "conclusa" },
  { id: 1, chiave: "caricata" },
  { id: 5, chiave: "rifiutata" },
];

// Ordine delle righe dentro ogni ateneo, per chiave del pulsante.
export const ORDINE_TIPOLOGIE = [
  "prevalutazione",
  "corso_laurea",
  "master",
  "corsi_perfezionamento",
  "alta_formazione_lauree",
  "formazione_alta_formazione",
  "corsi_singoli",
  "corsi_speciali",
];

/** Dove porta una riga: l'elenco filtrato, o la pagina delle prevalutazioni. */
export function percorsoTipologia(blocco, pulsante) {
  if (pulsante.tipo === "prevalutazione") {
    return `/prevalutazioni?universita=${blocco.nomeUniversitaId}`;
  }
  const params = new URLSearchParams();
  params.set("universita", blocco.nomeUniversitaId);
  pulsante.listinoTipoCorsoIds.forEach((idTipo) =>
    params.append("tipoCorso", idTipo),
  );
  if (pulsante.haFiltroInterno) params.set("filtroInterno", "1");
  return `/pratiche?${params.toString()}`;
}

function somma(valori) {
  return valori.reduce((totale, n) => totale + n, 0);
}

function chiaveGruppo(universita, tipoCorso, stato) {
  return `${universita}|${tipoCorso}|${stato}`;
}

/**
 * Tutti i numeri della pagina. Ogni totale e' la somma delle righe, come nel
 * design: le pratiche con un tipo di corso che nessuna riga raccoglie, o in
 * uno stato che non ha colonna, non si contano. La Prevalutazione non e' una
 * pratica e resta a zero.
 *
 * @param {Array} blocchi  BLOCCHI_PRATICHE
 * @param {Array<{nome_universita_id: number, listino_tipo_corso_id: number|null,
 *   pratica_stato_id: number, totale: number}>} conteggi  GET /pratiche/conteggi
 * @param {Record<string, boolean>} permessi  GET /clienti/permessi-pratiche
 */
export function costruisciPannello(blocchi, conteggi, permessi) {
  const gruppi = new Map(
    conteggi.map((g) => [
      chiaveGruppo(g.nome_universita_id, g.listino_tipo_corso_id, g.pratica_stato_id),
      g.totale,
    ]),
  );
  const totaliStati = STATI_PANNELLO.map(() => 0);

  const atenei = blocchi.map((blocco) => {
    const somme = STATI_PANNELLO.map(() => 0);
    const righe = [...blocco.pulsanti]
      .sort(
        (a, b) =>
          ORDINE_TIPOLOGIE.indexOf(a.chiave) - ORDINE_TIPOLOGIE.indexOf(b.chiave),
      )
      .map((pulsante) => {
        const celle = STATI_PANNELLO.map((stato, i) => {
          const n =
            pulsante.tipo === "prevalutazione"
              ? 0
              : somma(
                  pulsante.listinoTipoCorsoIds.map(
                    (tipo) =>
                      gruppi.get(chiaveGruppo(blocco.nomeUniversitaId, tipo, stato.id)) ?? 0,
                  ),
                );
          somme[i] += n;
          totaliStati[i] += n;
          return n;
        });
        return {
          chiave: pulsante.chiave,
          label: pulsante.label,
          celle,
          totale: somma(celle),
          percorso: percorsoTipologia(blocco, pulsante),
          bloccata: Boolean(pulsante.semprebloccato),
        };
      });
    return {
      chiave: blocco.chiave,
      titolo: blocco.titolo,
      logo: blocco.logo,
      abilitato: Boolean(permessi.abilPraticheUniv && permessi[blocco.flagPermesso]),
      righe,
      somme,
      totale: somma(somme),
    };
  });

  return {
    senzaAbilitazione: !permessi.abilPraticheUniv,
    totaliStati,
    totale: somma(totaliStati),
    atenei,
  };
}
