import { STILI_EDUNEWS24 } from "../../config/styles/edunews24.js";
import { chiaveVoce, raggruppaPerGiorno } from "../../lib/edunews24.js";
import RigaOpportunita from "./RigaOpportunita.jsx";

/**
 * Interpelli o Selezione nella pagina: righe dense raggruppate per giorno di
 * pubblicazione (Roma), con l'intestazione "Oggi", "Ieri" (piu' la data
 * estesa) o la data. Il raggruppamento si fa sull'elenco accumulato, quindi
 * un gruppo che continua dopo "Carica altri" non ripete l'intestazione. Le
 * voci chiuse e scadute restano, con targa e distintivo neutri.
 */
export default function OpportunitaPagina({ sezione, voci, adesso }) {
  const gruppi = raggruppaPerGiorno(voci, adesso);
  return (
    <>
      {gruppi.map(({ giorno, etichetta, dataEstesa, voci: elenco }) => (
        <section key={giorno ?? "senza-data"} className="edunews24-gruppo">
          <div className="edunews24-gruppo__intestazione">
            <h2 className={STILI_EDUNEWS24.titoloGruppo}>
              {giorno && !dataEstesa ? <time dateTime={giorno}>{etichetta}</time> : etichetta}
            </h2>
            {giorno && dataEstesa && <time dateTime={giorno} className={STILI_EDUNEWS24.dataGruppo}>{dataEstesa}</time>}
          </div>
          <ul role="list" className="edunews24-elenco">
            {elenco.map((voce) => (
              <RigaOpportunita key={chiaveVoce(voce)} voce={voce} sezione={sezione} adesso={adesso} />
            ))}
          </ul>
        </section>
      ))}
    </>
  );
}
