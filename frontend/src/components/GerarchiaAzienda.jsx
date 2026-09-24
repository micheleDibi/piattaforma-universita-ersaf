import { useState } from "react";
import { apiFetch, messaggioErrore } from "../lib/api";
import { leggiRuolo } from "../lib/sessione";
import { nomeAzienda } from "../lib/schedaAzienda.js";
import { pulsante } from "../config/styles/pulsante";
import { notaCampo } from "../config/styles/campo";
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import ModalCambiaPadreAzienda from "./ModalCambiaPadreAzienda.jsx";
import AlertMessage from "./AlertMessage.jsx";

const TESTI = TESTI_AZIENDA.gerarchia;

/**
 * Riquadro "Azienda padre" della scheda azienda, con "Cambia padre" per il
 * Nazionale. Il padre lo legge la scheda (usePadreAzienda), che lo usa anche
 * nel sottotitolo: qui arriva gia' letto, con `onRicarica` per rileggerlo
 * dopo un cambio.
 *
 * @param {{
 *   aziendaId: string,
 *   padre: object|null|undefined,
 *   errore?: string,
 *   onRicarica: () => void,
 * }} props
 *   padre: undefined in caricamento, null se l'azienda e' radice.
 */
export default function GerarchiaAzienda({
  aziendaId,
  padre,
  errore,
  onRicarica,
}) {
  const [salvataggio, setSalvataggio] = useState(false);
  const [messaggioSalvataggio, setMessaggioSalvataggio] = useState("");
  const [modaleAperta, setModaleAperta] = useState(false);
  // undefined = nessuna conferma in sospeso. Puo' contenere null (valore
  // valido: "rendi radice") o un oggetto azienda selezionata dal modale.
  const [azionePendente, setAzionePendente] = useState(undefined);

  const eNazionale = leggiRuolo() === "nazionale";

  // Niente <form>/onSubmit: questo componente vive dentro il <form> di
  // SchedaAzienda.jsx, e React non gestisce form annidati.
  const cambiaPadre = async (aziendaSelezionata, conferma = false) => {
    setModaleAperta(false);
    setSalvataggio(true);
    setMessaggioSalvataggio("");
    try {
      const query = conferma ? "?conferma_reset=true" : "";
      const risposta = await apiFetch(
        `/aziende-xcod/${aziendaId}/padre${query}`,
        {
          method: "PUT",
          body: JSON.stringify({
            nuovo_padre_id: aziendaSelezionata
              ? aziendaSelezionata.azienda_id
              : null,
          }),
        },
      );

      if (risposta.status === 409) {
        setAzionePendente(aziendaSelezionata ?? null);
        return;
      }

      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      setAzionePendente(undefined);
      onRicarica();
    } catch (err) {
      setMessaggioSalvataggio(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  if (errore)
    return (
      <AlertMessage message={{ type: "error", text: errore }} separato={false} />
    );

  return (
    <div className={stili.riquadroPadre}>
      <div className={stili.rigaPadre}>
        <div className={stili.testoPadre}>
          <span className={stili.etichettaPadre}>{TESTI.etichetta}</span>
          <span className={stili.nomePadre}>
            {padre === undefined
              ? TESTI.caricamento
              : padre === null
                ? TESTI.radice
                : nomeAzienda(padre)}
          </span>
        </div>

        {eNazionale && (
          <button
            type="button"
            onClick={() => setModaleAperta(true)}
            disabled={salvataggio}
            className={`${pulsante("contorno", "medio")} shrink-0`}
          >
            {salvataggio ? TESTI_AZIENDA.salvataggio : TESTI.cambia}
          </button>
        )}
      </div>

      {messaggioSalvataggio && (
        <p className={notaCampo("errore")}>{messaggioSalvataggio}</p>
      )}

      {azionePendente !== undefined && (
        <div className={`${stili.conferma} mt-3`}>
          <div className={stili.messaggioConferma}>
            <AlertMessage
              message={{
                type: "warning",
                text: TESTI_AZIENDA.azzeramento.messaggio,
              }}
              separato={false}
            />
          </div>
          <div className={stili.pulsantiConferma}>
            <button
              type="button"
              onClick={() => cambiaPadre(azionePendente, true)}
              disabled={salvataggio}
              className={pulsante("primario", "piccolo")}
            >
              {TESTI_AZIENDA.azzeramento.conferma}
            </button>
            <button
              type="button"
              onClick={() => setAzionePendente(undefined)}
              className={pulsante("testuale", "piccolo")}
            >
              {TESTI_AZIENDA.azzeramento.annulla}
            </button>
          </div>
        </div>
      )}

      <ModalCambiaPadreAzienda
        isOpen={modaleAperta}
        onClose={() => setModaleAperta(false)}
        onSelectPadre={cambiaPadre}
        aziendaIdEsclusa={Number(aziendaId)}
      />
    </div>
  );
}
