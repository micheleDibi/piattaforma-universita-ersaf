import { useEffect, useState } from "react";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { campo as classiCampo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import { CAMPI_PERCENTUALI } from "../config/campiPercentuali.js";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";

// Righe della tabella: ateneo e campo per Lauree, Master, Perfezionamenti;
// null = la convenzione non prevede quella tipologia.
const ATENEI = [
  ["eCampus", "universita_ecampus_lauree", "universita_ecampus_master", null],
  ["Link", "universita_link_lauree", "universita_link_master", null],
  ["SSML", "universita_SSML_lauree", "universita_SSML_master", null],
  ["A4U", null, "universita_A4U_master", "universita_A4U_perfezionamenti"],
];
const TIPOLOGIE = ["Lauree", "Master", "Perfezionamenti"];
const GRIGLIA =
  "grid grid-cols-[minmax(0,1.2fr)_repeat(3,minmax(0,1fr))] items-center gap-4 px-4 py-2.5";

// inSezione: dentro una SezioneModulo, senza scheda e titolo propri.
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

  const contenitore = inSezione ? "" : `${scheda()} p-6`;

  if (caricamento) {
    return (
      <div className={contenitore}>
        <IndicatoreCaricamento messaggio="Caricamento in corso..." centrato />
      </div>
    );
  }

  return (
    <div className={contenitore}>
      {!inSezione && (
        <h4 className="text-base font-semibold mb-4">
          Dettaglio convenzioni universitarie
        </h4>
      )}

      {errore && (
        <div className="mb-4 whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
          {errore}
        </div>
      )}

      <div className="overflow-x-auto rounded-controllo border border-bordo">
        <div className="min-w-[480px]">
          <div
            className={`${GRIGLIA} border-b border-bordo bg-superficie-tenue text-etichetta uppercase tracking-wider text-testo-tenue`}
          >
            <span>Ateneo</span>
            {TIPOLOGIE.map((tipologia) => (
              <span key={tipologia}>{tipologia}</span>
            ))}
          </div>
          {ATENEI.map(([ateneo, ...campi]) => (
            <div
              key={ateneo}
              className={`${GRIGLIA} border-b border-bordo last:border-b-0`}
            >
              <span className="text-sm font-semibold">{ateneo}</span>
              {campi.map((nome, indice) => {
                if (!nome)
                  return (
                    <span
                      key={indice}
                      className="text-center text-sm text-testo-tenue"
                    >
                      -
                    </span>
                  );
                if (soloLettura)
                  return (
                    <span key={nome} className="text-right text-sm">
                      {dettaglio?.[nome] ?? 0}%
                    </span>
                  );
                return (
                  <div key={nome} className="relative flex items-center">
                    <input
                      id={nome}
                      name={nome}
                      type="number"
                      min="0"
                      max="100"
                      aria-label={`${ateneo} - ${TIPOLOGIE[indice]}`}
                      value={dettaglio?.[nome] ?? 0}
                      onChange={aggiornaPercentuale}
                      className={`${classiCampo("compatto")} pr-8 text-right`}
                    />
                    <span className="pointer-events-none absolute right-3 text-sm text-testo-tenue">
                      %
                    </span>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
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
            className={pulsante("secondario")}
          >
            {salvataggio ? "Salvataggio..." : "Salva percentuali"}
          </button>
        </div>
      )}
    </div>
  );
}
