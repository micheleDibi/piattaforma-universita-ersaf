import { campo } from "../../config/styles/campo.js";
import { pulsante } from "../../config/styles/pulsante.js";
import { pillola } from "../../config/styles/pillola.js";
import { notaRecapito, STILI_ANAGRAFICA as stili } from "../../config/styles/anagrafica.js";
import { TESTI_CONTATTI as testi } from "../../config/testi/anagrafica.js";
import { dataVerifica, statoRecapito } from "../../lib/schedaAnagrafica.js";
import { Check } from "../../config/icone.js";

/**
 * Scheda in evidenza di un recapito usato per l'accesso (email o cellulare):
 * etichetta con la pillola "Verificata" oppure il pulsante "Verifica", campo
 * grande e note brevi (anomalie, data della verifica, invito a salvare).
 *
 * @param {{
 *   tipo: "email"|"cellulare",
 *   valore: string,
 *   onChange: Function,
 *   verifica: { disponibile: boolean, stato?: object, apri: Function },
 *   nota?: string[],
 * }} props
 */
export default function CampoContatto({ tipo, valore, onChange, verifica, nota = [] }) {
  const id = `contatto-${tipo}`;
  const { verificato, verificatoIl, mostraVerifica, verificaDisabilitata, daSalvare } =
    statoRecapito(verifica, valore);
  const avviso = nota.length > 0;
  const conNote = avviso || Boolean(verificatoIl) || daSalvare;
  return (
    <div className={stili.schedaRecapito}>
      <div className={stili.testataRecapito}>
        <label htmlFor={id} className={stili.etichettaRecapito}>
          {testi[tipo]}
        </label>
        {verificato && (
          <span className={pillola("positivo")}>
            <Check aria-hidden="true" className={stili.spuntaRecapito} />
            {testi.verificato(tipo)}
          </span>
        )}
        {mostraVerifica && (
          <button
            type="button"
            disabled={verificaDisabilitata}
            className={`${pulsante("contorno", "minimo")} ${stili.pulsanteRecapito}`}
            onClick={verifica.apri}
          >
            {testi.verifica}
          </button>
        )}
      </div>
      <input
        id={id}
        type={tipo === "email" ? "email" : "tel"}
        name={tipo}
        value={valore}
        onChange={onChange}
        className={campo("recapito", { avviso })}
        aria-describedby={conNote ? `${id}-nota` : undefined}
      />
      {conNote && (
        <div id={`${id}-nota`}>
          {nota.map((testo, indice) => (
            <p key={`${indice}-${testo}`} className={notaRecapito("avviso")}>
              {testo}
            </p>
          ))}
          {verificatoIl && (
            <p className={notaRecapito()}>{testi.verificatoIl(dataVerifica(verificatoIl))}</p>
          )}
          {daSalvare && <p className={notaRecapito()}>{testi.daSalvare}</p>}
        </div>
      )}
    </div>
  );
}
