import { useEffect, useState } from "react";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import {
  campo as classiCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import { CAMPI_PERCENTUALI } from "../config/campiPercentuali.js";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";

// soloLettura: la scheda dell'attuatore mostra le percentuali dell'azienda
// associata solo in visione, perche' si modificano dalla scheda dell'azienda
// (che le applica anche alle aziende figlie).
export default function DettaglioConvenzioniUniversitarie({
  aziendaId,
  soloLettura = false,
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

  if (caricamento) {
    return (
      <div className={`${scheda()} p-6`}>
        <IndicatoreCaricamento messaggio="Caricamento in corso..." centrato />
      </div>
    );
  }

  return (
    <div className={`${scheda()} p-6`}>
      <h4 className="text-base font-semibold mb-4">
        Dettaglio convenzioni universitarie
      </h4>

      {errore && (
        <div className="mb-4 whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
          {errore}
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        {CAMPI_PERCENTUALI.map(([nome, etichetta]) =>
          soloLettura ? (
            <div key={nome} className="flex flex-col">
              <span className={classiEtichetta()}>{etichetta.toUpperCase()}</span>
              <span className="text-sm">{dettaglio?.[nome] ?? 0}%</span>
            </div>
          ) : (
            <div key={nome} className="flex flex-col">
              <label htmlFor={nome} className={classiEtichetta()}>
                {etichetta.toUpperCase()}
              </label>
              <input
                id={nome}
                name={nome}
                type="number"
                min="0"
                max="100"
                value={dettaglio?.[nome] ?? 0}
                onChange={aggiornaPercentuale}
                className={classiCampo("comodo")}
              />
            </div>
          ),
        )}
      </div>

      {!soloLettura && (
        <div className="flex flex-col items-end gap-3 mt-6">
          {confermaResetPendente && (
            <div className="flex w-full items-center justify-between gap-4 rounded-controllo border border-bordo p-3">
              <AlertMessage
                message={{
                  type: "warning",
                  text: "Alcune percentuali verranno azzerate. Continuare?",
                }}
                separato={false}
              />
              <div className="flex shrink-0 gap-3">
                <button
                  type="button"
                  onClick={() => salvaDettaglio(true)}
                  disabled={salvataggio}
                  className={pulsante("primario", "piccolo")}
                >
                  Conferma
                </button>
                <button
                  type="button"
                  onClick={() => setConfermaResetPendente(false)}
                  className={pulsante("discreto", "piccolo")}
                >
                  Annulla
                </button>
              </div>
            </div>
          )}
          {/* type="button": puo' vivere dentro il <form> di una scheda che
              lo racchiude, non deve inviarne il submit. */}
          <button
            type="button"
            onClick={() => salvaDettaglio()}
            disabled={salvataggio}
            className={pulsante("primario", "grande")}
          >
            {salvataggio ? "Salvataggio..." : "Salva percentuali"}
          </button>
        </div>
      )}
    </div>
  );
}
