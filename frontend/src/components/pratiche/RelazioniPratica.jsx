import SelezioneRicercabile from "../shared/SelezioneRicercabile.jsx";
import { SELEZIONE_STUDENTE, SELEZIONE_PERCORSO, SELEZIONE_EMITTENTE } from "../../config/pratica.js";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";
import { etichetta } from "../../config/styles/campo.js";

export default function RelazioniPratica({ form, nuova }) {
  const relazioni = [
    [SELEZIONE_STUDENTE, form.studente, form.setStudente],
    [SELEZIONE_EMITTENTE, form.emittente, form.setEmittente],
    [SELEZIONE_PERCORSO, form.percorso, form.setPercorso],
  ];
  return <section className={stili.sezione} aria-labelledby="iscrizione-pratica">
    <h2 id="iscrizione-pratica" className={stili.titolo}>Iscrizione</h2>
    <div className={stili.colonne}>
      {relazioni.map(([configurazione, valore, aggiorna]) => nuova
        ? <SelezioneRicercabile key={configurazione.titolo} configurazione={configurazione}
          selezionati={valore ? [valore] : []} onCambia={scelte => aggiorna(scelte[0] || null)} />
        : <dl key={configurazione.titolo}><dt className={etichetta()}>{configurazione.titolo}</dt><dd className={stili.valore}>{valore?.label || "Non indicato"}</dd></dl>)}
      <dl><dt className={etichetta()}>Università</dt><dd className={stili.valore}>{form.universitaLabel || (nuova ? "Seleziona un percorso formativo" : "Non indicata")}</dd></dl>
    </div>
    {form.erroreProdotto && <p role="alert" className="text-negativo">{form.erroreProdotto}</p>}
  </section>;
}
