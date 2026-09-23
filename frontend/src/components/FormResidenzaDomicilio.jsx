import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { useConfermaAzione } from "../hooks/useConfermaAzione.js";
import { TESTI_COPIA } from "../config/testi/copia.js";
import { TESTI_RESIDENZA as testi } from "../config/testi/anagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

// [suffisso, colonne]
const CAMPI_INDIRIZZO = [
  ["Indirizzo", 5],
  ["Civico", 1],
  ["Comune", 3],
  ["Cap", 2],
  ["Provincia", 1],
];
// In residenza CAP e provincia non sono obbligatori, come prima.
const OBBLIGATORI_RESIDENZA = new Set(["Indirizzo", "Civico", "Comune"]);

export default function FormResidenzaDomicilio({
  formData,
  handleChange,
  handleCopyResidenza,
}) {
  const { esegui, stato } = useConfermaAzione(handleCopyResidenza);

  const campi = (prefisso) =>
    CAMPI_INDIRIZZO.map(([suffisso, colonne]) => {
      const nome = `${prefisso}${suffisso}`;
      const obbligatorio =
        prefisso === "residenza" && OBBLIGATORI_RESIDENZA.has(suffisso);
      return (
        <CampoModulo
          key={nome}
          per={nome}
          etichetta={testi.campi[suffisso]}
          obbligatorio={obbligatorio}
          colonne={colonne}
        >
          <input
            id={nome}
            type="text"
            name={nome}
            value={formData[nome]}
            onChange={handleChange}
            className={campo("comodo")}
            required={obbligatorio}
          />
        </CampoModulo>
      );
    });

  return (
    <>
      <SezioneModulo titolo={testi.residenza}>{campi("residenza")}</SezioneModulo>
      <SezioneModulo
        titolo={testi.domicilio}
        descrizione={testi.descrizioneDomicilio}
        azioni={
          <>
            <button
              type="button"
              onClick={esegui}
              disabled={stato === "attesa"}
              data-esito={stato}
              className={pulsante("contorno", "piccolo")}
            >
              {stato === "eseguita" ? TESTI_COPIA.confermaResidenza : testi.copia}
            </button>
            <span role="status" className="sr-only">
              {stato === "eseguita" ? TESTI_COPIA.confermaResidenza : ""}
            </span>
          </>
        }
      >
        {campi("domicilio")}
      </SezioneModulo>
    </>
  );
}
