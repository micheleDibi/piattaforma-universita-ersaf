import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { BLOCCHI_PRATICHE } from "../lib/configPratiche";
import AlertMessage from "./AlertMessage.jsx";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import { STILI_PANNELLO_PRATICHE as stili } from "../config/styles/pratica.js";
import { TESTI_PANNELLO_PRATICHE as testi } from "../config/testi/pratiche.js";

export default function PannelloPratiche() {
  const navigate = useNavigate();
  const [permessi, setPermessi] = useState(null);
  const [errore, setErrore] = useState(null);

  useEffect(() => {
    let attivo = true;
    apiFetch("/clienti/permessi-pratiche")
      .then(async (risposta) => {
        if (!attivo) return;
        if (!risposta.ok) {
          setErrore(await messaggioErrore(risposta, testi.erroreCaricamento));
          return;
        }
        setPermessi(await leggiJson(risposta));
      })
      .catch(
        (err) =>
          attivo &&
          setErrore(err.message ?? testi.erroreCaricamento),
      );
    return () => {
      attivo = false;
    };
  }, []);

  // resto del componente invariato

  function bloccoAttivo(blocco) {
    return permessi.abilPraticheUniv && permessi[blocco.flagPermesso];
  }

  function selezionaPulsante(blocco, pulsante) {
    if (pulsante.semprebloccato) return;

    if (pulsante.tipo === "prevalutazione") {
      navigate(`/prevalutazioni?universita=${blocco.nomeUniversitaId}`);
      return;
    }

    const params = new URLSearchParams();
    params.set("universita", blocco.nomeUniversitaId);
    pulsante.listinoTipoCorsoIds.forEach((idTipo) =>
      params.append("tipoCorso", idTipo),
    );
    if (pulsante.haFiltroInterno) params.set("filtroInterno", "1");
    navigate(`/pratiche?${params.toString()}`);
  }

  if (errore) {
    return (
      <AlertMessage message={{ type: "error", text: errore }} separato={false} />
    );
  }

  if (!permessi) {
    return (
      <IndicatoreCaricamento dimensione="compatto" messaggio={testi.caricamento} />
    );
  }

  return (
    <div className={stili.contenuto}>
      {!permessi.abilPraticheUniv && (
        <AlertMessage
          message={{ type: "warning", text: testi.senzaAbilitazione }}
          separato={false}
        />
      )}

      {BLOCCHI_PRATICHE.map((blocco) => {
        const abilitato = bloccoAttivo(blocco);
        return (
          <section key={blocco.chiave} className={stili.sezione}>
            <h2 className={stili.titolo}>{blocco.titolo}</h2>
            <div className={stili.riga}>
              <img
                src={blocco.logo}
                alt={blocco.titolo}
                className={stili.logo}
              />
              <div className={stili.tipologie}>
                {blocco.pulsanti.map((pulsante) => {
                  const disabilitato = !abilitato || pulsante.semprebloccato;
                  return (
                    <button
                      key={pulsante.chiave}
                      type="button"
                      disabled={disabilitato}
                      onClick={() => selezionaPulsante(blocco, pulsante)}
                      className={stili.tipologia}
                    >
                      {pulsante.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>
        );
      })}
    </div>
  );
}
