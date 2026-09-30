import { MASSIMO_REGIONI_MODULO } from "../../config/edunews24.js";
import { STILI_EDUNEWS24, titoloVoce } from "../../config/styles/edunews24.js";
import { TESTI_EDUNEWS24 as testi } from "../../config/testi/edunews24.js";
import {
  chiaveVoce,
  descriviArea,
  giornoRoma,
  partiGiorno,
  statoOpportunita,
  testoArea,
  testoAreaAccessibile,
  tonoTarga,
} from "../../lib/edunews24.js";
import DistintivoScadenza from "./DistintivoScadenza.jsx";
import LinkEsterno from "./LinkEsterno.jsx";
import MetadatiVoce from "./MetadatiVoce.jsx";
import Targa from "./Targa.jsx";

// Targa della riga: la scadenza per la selezione ("Senza scadenza" se manca,
// nel tono del distintivo), la data di pubblicazione per gli interpelli.
function datiTarga(voce, stato) {
  if (voce.tipo === "selezione-personale") {
    const tono = tonoTarga(stato);
    const scadenza = partiGiorno(voce.scadenza);
    if (!scadenza) return { tono, etichetta: testi.senzaScadenza, sr: testi.scadenzaNonIndicata };
    return { tono, cifra: scadenza.giorno, mese: scadenza.mese, sr: testi.scadenzaSr(scadenza.esteso) };
  }
  const pubblicazione = partiGiorno(giornoRoma(voce.pubblicato_il));
  if (!pubblicazione) return { tono: "normale", etichetta: testi.senzaData };
  return {
    tono: "normale",
    cifra: pubblicazione.giorno,
    mese: pubblicazione.mese,
    sr: testi.pubblicazioneSr(pubblicazione.esteso),
  };
}

function RigaTabellone({ voce, adesso }) {
  const stato = statoOpportunita(voce, adesso);
  const classe = voce.tipo === "interpello" ? voce.classe_concorso : null;
  const area = descriviArea(voce, MASSIMO_REGIONI_MODULO);
  // Sede e area su una riga troncata; il testo completo va ai lettori di schermo.
  const luogo = [voce.sede, testoArea(area)].filter(Boolean).join(", ");
  const dettagli = luogo
    ? [{
        chiave: "luogo",
        testo: luogo,
        sr: [voce.sede, testoAreaAccessibile(area)].filter(Boolean).join(", "),
        className: "edunews24-riga__dove",
      }]
    : [];

  return (
    <li className="edunews24-riga edunews24-voce" data-contesto="modulo">
      <Targa forma="riga" {...datiTarga(voce, stato)} />
      <div className="edunews24-riga__stato">
        {stato && <DistintivoScadenza stato={stato} />}
        {classe && (
          <span className={STILI_EDUNEWS24.classe}>
            <span aria-hidden="true">{testi.classe(classe)}</span>
            <span className="sr-only">{testi.classeSr(classe)}</span>
          </span>
        )}
      </div>
      <div className="edunews24-riga__corpo">
        <h3 className="edunews24-voce__titolo">
          <LinkEsterno href={voce.url} className="edunews24-voce__link group">
            <span className={titoloVoce("voce", 2)}>{voce.titolo}</span>
          </LinkEsterno>
        </h3>
      </div>
      <MetadatiVoce voce={voce} adesso={adesso} conData={false} dettagli={dettagli} className="edunews24-riga__luogo" />
    </li>
  );
}

/**
 * Tabellone di Interpelli e Selezione nel modulo, sotto la voce principale:
 * righe [targa | stato | titolo | luogo] con il link del titolo esteso a
 * tutta la riga. Riceve fino a 3 voci: il CSS ne mostra 2 nel modulo
 * impilato e 3 dai 38rem. Nella cella di stato il distintivo della
 * selezione o la classe di concorso degli interpelli, vuota se manca.
 */
export default function TabelloneOpportunita({ sezione, voci, adesso }) {
  return (
    <div className="edunews24-tabellone">
      <ul role="list" className="edunews24-tabellone__elenco" aria-label={testi.tabellone[sezione]}>
        {voci.map((voce) => <RigaTabellone key={chiaveVoce(voce)} voce={voce} adesso={adesso} />)}
      </ul>
    </div>
  );
}
