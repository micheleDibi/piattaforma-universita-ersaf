import { useState } from "react";
import BarraSchede from "../shared/BarraSchede.jsx";
import { STILI_PROFILO as stili } from "../../config/styles/profilo.js";
import { SCHEDE_PROFILO, TESTI_PROFILO } from "../../config/testi/profilo.js";
import DatiPrincipaliProfilo from "./DatiPrincipaliProfilo.jsx";
import RiepilogoProfilo from "./RiepilogoProfilo.jsx";

export default function DettaglioProfilo({ profilo }) {
  const [attiva, setAttiva] = useState(SCHEDE_PROFILO[0].id);
  const schede = SCHEDE_PROFILO.map(({ id, etichetta }) => ({ id, label: etichetta }));
  return (
    <div className={stili.contenitore}>
      <BarraSchede id="profilo" etichetta={TESTI_PROFILO.titolo} schede={schede}
        attiva={attiva} onChange={setAttiva} />
      {SCHEDE_PROFILO.map(({ id }) => (
        <div key={id} role="tabpanel" id={`profilo-pannello-${id}`} aria-labelledby={`profilo-scheda-${id}`}
          hidden={attiva !== id} tabIndex={0} className={stili.pannello}>
          {id === "dati-principali" ? <DatiPrincipaliProfilo profilo={profilo} /> : <RiepilogoProfilo profilo={profilo} />}
        </div>
      ))}
    </div>
  );
}
