import { useEffect, useState } from "react";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { suffissoCampo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import {
  intestazioneCampi,
  rigaCampi,
  tabellaCampi,
} from "../config/styles/tabella";
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import {
  CAMPI_PERCENTUALI,
  CONVENZIONI,
} from "../config/campiPercentuali.js";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";

const TESTI = TESTI_AZIENDA.convenzioni;

// inSezione: dentro una SezioneModulo, che porta titolo e descrizione.
// Altrimenti (scheda Azienda dell'attuatore) il blocco ha un titolo proprio.
// soloLettura: la scheda dell'attuatore mostra le percentuali dell'azienda
// associata solo in visione, perche' si modificano dalla scheda dell'azienda
// (che le applica anche alle aziende figlie).
export default function DettaglioConvenzioniUniversitarie({
  aziendaId,
  soloLettura = false,
  inSezione = false,
}) {
  const [dettaglio, setDettaglio] = useState(null);
  const [caricamento, setCaricamento] = useState(Boolean(aziendaId));
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  const [confermaResetPendente, setConfermaResetPendente] = useState(false);

  useEffect(() => {
    if (!aziendaId) return;

    let annullato = false;
    apiFetch(`/aziende/${aziendaId}/dettagli`)
      .then(async (risposta) => {
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
        return risposta.json();
      })
      .then((dati) => {
        if (annullato) return;
        setDettaglio(dati);
      })
      .catch((err) => {
        if (annullato) return;
        setErrore(err.message);
      })
      .finally(() => {
        if (!annullato) setCaricamento(false);
      });

    return () => {
      annullato = true;
    };
  }, [aziendaId]);

  const aggiornaPercentuale = (evento) => {
    const { name, value } = evento.target;
    setDettaglio((prec) => ({
      ...prec,
      [name]: value === "" ? 0 : Number(value),
    }));
  };

  const salvaDettaglio = async (conferma = false) => {
    setErrore("");
    setSalvataggio(true);
    try {
      const corpo = Object.fromEntries(
        CAMPI_PERCENTUALI.map(([chiave]) => [chiave, dettaglio?.[chiave] ?? 0]),
      );
      const query = conferma ? "?conferma_reset=true" : "";
      const risposta = await apiFetch(
        `/aziende/${aziendaId}/dettagli${query}`,
        { method: "PUT", body: JSON.stringify(corpo) },
      );

      if (risposta.status === 409) {
        setConfermaResetPendente(true);
        return;
      }

      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      setConfermaResetPendente(false);
      setDettaglio(await leggiJson(risposta));
    } catch (err) {
      setErrore(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  const titolo = !inSezione && (
    <h3 className={stili.titoloConvenzioni}>{TESTI.titoloAttuatore}</h3>
  );

  if (caricamento) {
    return (
      <div className={stili.convenzioni}>
        {titolo}
        <IndicatoreCaricamento messaggio={TESTI_AZIENDA.caricamento} centrato />
      </div>
    );
  }

  const cella = (ateneo, nome, indice) => {
    if (!nome)
      return (
        <span key={indice} role="cell" className={stili.cellaNonPrevista}>
          <span aria-hidden="true">{TESTI_AZIENDA.trattino}</span>
          <span className="sr-only">{TESTI.nonPrevista}</span>
        </span>
      );
    const simbolo = (
      <span aria-hidden="true" className={suffissoCampo()}>
        {TESTI.percento}
      </span>
    );
    if (soloLettura)
      return (
        <span key={nome} role="cell" className={stili.cellaPercentuale}>
          <span className={stili.percentualeLettura}>
            {dettaglio?.[nome] ?? 0}
            <span className="sr-only">{TESTI.percento}</span>
          </span>
          {simbolo}
        </span>
      );
    return (
      <div key={nome} role="cell" className={stili.cellaPercentuale}>
        <input
          id={nome}
          name={nome}
          type="number"
          min="0"
          max="100"
          aria-label={TESTI.etichettaCampo(ateneo, TESTI.tipologie[indice])}
          value={dettaglio?.[nome] ?? 0}
          onChange={aggiornaPercentuale}
          className={stili.percentuale}
        />
        {simbolo}
      </div>
    );
  };

  return (
    <div className={stili.convenzioni}>
      {titolo}

      {errore && (
        <AlertMessage message={{ type: "error", text: errore }} separato={false} />
      )}

      <div role="table" aria-label={TESTI.etichettaTabella} className={tabellaCampi()}>
        <div role="row" className={intestazioneCampi("normale", "convenzioni")}>
          <span role="columnheader">{TESTI.ateneo}</span>
          {TESTI.tipologie.map((tipologia) => (
            <span key={tipologia} role="columnheader">
              {tipologia}
            </span>
          ))}
        </div>
        {CONVENZIONI.map(([ateneo, ...campi]) => (
          <div key={ateneo} role="row" className={rigaCampi("normale", "convenzioni")}>
            <span role="rowheader" className={stili.ateneo}>
              {ateneo}
            </span>
            {campi.map((nome, indice) => cella(ateneo, nome, indice))}
          </div>
        ))}
      </div>

      {!soloLettura && confermaResetPendente && (
        <div className={stili.conferma}>
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
              onClick={() => salvaDettaglio(true)}
              disabled={salvataggio}
              className={pulsante("primario", "piccolo")}
            >
              {TESTI_AZIENDA.azzeramento.conferma}
            </button>
            <button
              type="button"
              onClick={() => setConfermaResetPendente(false)}
              className={pulsante("testuale", "piccolo")}
            >
              {TESTI_AZIENDA.azzeramento.annulla}
            </button>
          </div>
        </div>
      )}

      {!soloLettura && (
        <div className={stili.azioniConvenzioni}>
          {/* type="button": puo' vivere dentro il <form> di una scheda che
              lo racchiude, non deve inviarne il submit. */}
          <button
            type="button"
            onClick={() => salvaDettaglio()}
            disabled={salvataggio}
            className={pulsante("contornoPrimario", "normale")}
          >
            {salvataggio ? TESTI_AZIENDA.salvataggio : TESTI.salva}
          </button>
        </div>
      )}
    </div>
  );
}
