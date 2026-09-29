import { MASSIMO_REGIONI_MODULO } from "../../config/edunews24.js";
import { STILI_EDUNEWS24, occhiello, sintesi, titoloVoce } from "../../config/styles/edunews24.js";
import { TESTI_EDUNEWS24 as testi } from "../../config/testi/edunews24.js";
import {
  descriviArea,
  giornoRoma,
  partiGiorno,
  statoOpportunita,
  testoArea,
  testoAreaAccessibile,
} from "../../lib/edunews24.js";
import DistintivoScadenza from "./DistintivoScadenza.jsx";
import LinkEsterno from "./LinkEsterno.jsx";
import MetadatiVoce from "./MetadatiVoce.jsx";
import Timbro from "./Timbro.jsx";

// Data del timbro: la scadenza per la selezione, altrimenti la pubblicazione
// (interpelli, e selezioni senza scadenza, che il distintivo dice "Aperto").
function datiTimbro(voce) {
  const scadenza = voce.tipo === "selezione-personale" ? partiGiorno(voce.scadenza) : null;
  if (scadenza) {
    return {
      etichetta: testi.scadeIl,
      cifra: `${scadenza.giorno} ${scadenza.mese}`,
      anno: scadenza.anno,
      sr: testi.scadenzaSr(scadenza.esteso),
    };
  }
  const pubblicazione = partiGiorno(giornoRoma(voce.pubblicato_il));
  if (!pubblicazione) return null;
  return {
    etichetta: testi.pubblicatoIl,
    cifra: `${pubblicazione.giorno} ${pubblicazione.mese}`,
    anno: pubblicazione.anno,
    sr: testi.pubblicazioneSr(pubblicazione.esteso),
  };
}

/**
 * Voce principale di Interpelli e Selezione nel modulo: il timbro pieno con
 * la data (scadenza o pubblicazione), il distintivo di stato (selezione) o la
 * classe di concorso (interpelli), l'ente, il titolo su 2 righe, la sintesi
 * (solo nel regime ampio, dal CSS) e i metadati con l'area e "Fonte". Il link
 * del titolo copre tutta la voce, che disegna l'anello di fuoco.
 */
export default function VocePrincipale({ voce, adesso }) {
  const timbro = datiTimbro(voce);
  const stato = statoOpportunita(voce, adesso);
  const classe = voce.tipo === "interpello" ? voce.classe_concorso : null;
  const area = descriviArea(voce, MASSIMO_REGIONI_MODULO);
  const dettagli = area ? [{ chiave: "area", testo: testoArea(area), sr: testoAreaAccessibile(area) }] : [];

  return (
    <div className="edunews24-principale edunews24-voce">
      {timbro && <Timbro {...timbro} />}
      {(stato || classe) && (
        <div className="edunews24-principale__stato">
          {stato ? <DistintivoScadenza stato={stato} /> : <span className={STILI_EDUNEWS24.classe}>{testi.classeSr(classe)}</span>}
        </div>
      )}
      {voce.ente && <p className={["edunews24-principale__ente", occhiello("ente")].join(" ")}>{voce.ente}</p>}
      <div className="edunews24-principale__corpo">
        <h3 className="edunews24-principale__titolo">
          <LinkEsterno href={voce.url} className="edunews24-voce__link group">
            <span className={titoloVoce(null, 2)}>{voce.titolo}</span>
          </LinkEsterno>
        </h3>
        {voce.sintesi && (
          <div className="edunews24-principale__sintesi">
            <p className={sintesi(2)}>{voce.sintesi}</p>
          </div>
        )}
        <MetadatiVoce voce={voce} adesso={adesso} conData={false} dettagli={dettagli} />
      </div>
    </div>
  );
}
