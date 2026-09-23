import { campo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { useConfermaAzione } from "../hooks/useConfermaAzione.js";
import { TESTI_COPIA } from "../config/testi/copia.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";

// [suffisso, etichetta, colonne]
const CAMPI_INDIRIZZO = [
  ["Indirizzo", "Indirizzo", 5],
  ["Civico", "Civico", 1],
  ["Comune", "Comune", 3],
  ["Cap", "CAP", 2],
  ["Provincia", "Prov.", 1],
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
    CAMPI_INDIRIZZO.map(([suffisso, etichetta, colonne]) => {
      const nome = `${prefisso}${suffisso}`;
      const obbligatorio =
        prefisso === "residenza" && OBBLIGATORI_RESIDENZA.has(suffisso);
      return (
        <CampoModulo
          key={nome}
          per={nome}
          etichetta={etichetta}
          obbligatorio={obbligatorio}
          colonne={colonne}
        >
          <input
            id={nome}
            type="text"
            name={nome}
            value={formData[nome]}
            onChange={handleChange}
            className={`${campo("comodo")} transition`}
            required={obbligatorio}
          />
        </CampoModulo>
      );
    });

  return (
    <>
      <SezioneModulo titolo="Residenza">{campi("residenza")}</SezioneModulo>
      <SezioneModulo
        titolo="Domicilio"
        descrizione="Solo se diverso dalla residenza."
      >
        {campi("domicilio")}
        <div className="col-span-6 flex justify-end">
          <button
            type="button"
            onClick={esegui}
            disabled={stato === "attesa"}
            data-esito={stato}
            className={pulsante("ausiliario")}
          >
            {stato === "eseguita"
              ? TESTI_COPIA.confermaResidenza
              : "Copia da residenza"}
          </button>
          <span role="status" className="sr-only">
            {stato === "eseguita" ? TESTI_COPIA.confermaResidenza : ""}
          </span>
        </div>
      </SezioneModulo>
    </>
  );
}
