import { campiPercorsoVisibili, ETICHETTE_CAMPI_PERCORSO } from "../../config/pratica.js";
import { dettaglioAttuale } from "../../lib/praticaForm.js";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";
import { etichetta } from "../../config/styles/campo.js";

const testo = (valore) => (valore === null || valore === undefined || valore === "" ? "-" : String(valore));

/** I valori delle caratteristiche del percorso: quattro vengono dalla testa
 * del listino (gia' tradotte in descrizione leggibile dal backend, vedi
 * ListinoTesta.extract_relations), tre dal suo dettaglio valido oggi. */
function valoriPercorso(prodotto) {
  const dettaglio = dettaglioAttuale(prodotto.dettagli);
  return {
    modalita: prodotto.listino_modalita_descrizione,
    facolta: prodotto.listino_facolta_descrizione,
    durata: dettaglio?.listDettaglio_durata != null ? `${dettaglio.listDettaglio_durata} mesi` : null,
    cfu: dettaglio?.listDettaglio_CFU,
    tasse: dettaglio?.listDettaglio_tasse,
    livello: prodotto.listTesta_livello,
    tipoLaurea: prodotto.listino_durataLaurea_descrizione,
    corsoLaurea: prodotto.listino_corsoLaurea_descrizione,
  };
}

/** Caratteristiche del percorso formativo scelto, sempre in sola lettura:
 * quali compaiono dipende dal tipo di corso del percorso (vedi
 * campiPercorsoVisibili in config/pratica.js). Niente da mostrare per un
 * percorso senza caratteristiche note per il suo tipo. */
export default function CaratteristichePercorso({ prodotto }) {
  if (!prodotto) return null;
  const campi = campiPercorsoVisibili(prodotto.listino_tipoCorso_id);
  if (!campi.length) return null;
  const valori = valoriPercorso(prodotto);
  // La sezione porta con se' il proprio separatore: cosi' non ne resta uno
  // orfano nella scheda quando il percorso non ha caratteristiche da
  // mostrare (return null sopra).
  return <>
    <hr className={stili.separatore} />
    <section className={stili.sezione} aria-labelledby="caratteristiche-percorso">
      <h2 id="caratteristiche-percorso" className={stili.titolo}>Caratteristiche del percorso</h2>
      <div className={stili.colonne}>
        {campi.map((chiave) => (
          <div key={chiave}>
            <span className={etichetta()}>{ETICHETTE_CAMPI_PERCORSO[chiave]}</span>
            <p className={stili.valore}>{testo(valori[chiave])}</p>
          </div>
        ))}
      </div>
    </section>
  </>;
}
