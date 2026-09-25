import { useEffect, useState } from "react";
import { Link } from "react-router";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { BLOCCHI_PRATICHE } from "../lib/configPratiche";
import { costruisciPannello, STATI_PANNELLO } from "../lib/pannelloPratiche.js";
import { ChevronRight } from "../config/icone.js";
import AlertMessage from "./AlertMessage.jsx";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import { STILI_PANNELLO_PRATICHE as stili } from "../config/styles/pratica.js";
import { TESTI_PANNELLO_PRATICHE as testi } from "../config/testi/pratiche.js";

async function leggi(percorso) {
  const risposta = await apiFetch(percorso);
  if (!risposta.ok) {
    throw new Error(await messaggioErrore(risposta, testi.erroreCaricamento));
  }
  return leggiJson(risposta);
}

function Punto({ stato }) {
  return <span className="pannello-pratiche__punto" data-stato={stato.chiave} />;
}

/** Nome per il lettore di schermo: le colonne degli stati non hanno intestazione. */
function descrivi(nome, totale, celle) {
  return testi.descriviTipologia(
    nome,
    totale,
    testi.elencoStati(STATI_PANNELLO.map((s, i) => [testi.stati[s.chiave], celle[i]])),
  );
}

/** Una tipologia: riga della tabella o voce della lista, secondo la forma. */
function Tipologia({ riga, attiva, className, children }) {
  const etichetta = descrivi(riga.label, riga.totale, riga.celle);
  if (!attiva) {
    return (
      <div className={className} role="link" aria-disabled="true" aria-label={etichetta}>
        {children}
      </div>
    );
  }
  return (
    <Link to={riga.percorso} className={className} aria-label={etichetta}>
      {children}
    </Link>
  );
}

function Striscia({ pannello }) {
  return (
    <div className="pannello-pratiche__striscia">
      <div className="pannello-pratiche__totale">
        <span className="pannello-pratiche__totale-etichetta">{testi.totalePratiche}</span>
        <span className="pannello-pratiche__totale-numero">{pannello.totale}</span>
      </div>
      {STATI_PANNELLO.map((stato, i) => (
        <div key={stato.chiave} className="pannello-pratiche__stato">
          <span className="pannello-pratiche__stato-etichetta">
            <Punto stato={stato} />
            {testi.stati[stato.chiave]}
          </span>
          <span className="pannello-pratiche__stato-numero">{pannello.totaliStati[i]}</span>
        </div>
      ))}
    </div>
  );
}

function Tabella({ ateneo }) {
  return (
    <div className="pannello-pratiche__tabella">
      <div className="pannello-pratiche__colonne" aria-hidden="true">
        <span>{testi.tipologia}</span>
        {STATI_PANNELLO.map((stato) => (
          <span key={stato.chiave} className="pannello-pratiche__colonna-stato">
            <Punto stato={stato} />
            {testi.stati[stato.chiave]}
          </span>
        ))}
        <span className="pannello-pratiche__colonna-totale">{testi.totale}</span>
        <span />
      </div>
      {ateneo.righe.map((riga) => (
        <Tipologia
          key={riga.chiave}
          riga={riga}
          attiva={ateneo.abilitato && !riga.bloccata}
          className="pannello-pratiche__riga"
        >
          <span className="pannello-pratiche__tipologia">{riga.label}</span>
          {riga.celle.map((n, i) => (
            <span
              key={STATI_PANNELLO[i].chiave}
              className="pannello-pratiche__valore"
              data-nullo={n === 0 || undefined}
            >
              {n}
            </span>
          ))}
          <span className="pannello-pratiche__totale-riga">{riga.totale}</span>
          <ChevronRight className="pannello-pratiche__chevron" aria-hidden="true" />
        </Tipologia>
      ))}
      <div className="pannello-pratiche__somma">
        {/* Fuori dalla griglia (sr-only e' posizionato): le celle restano al loro posto. */}
        <span className="sr-only">{descrivi(testi.totaleAteneo, ateneo.totale, ateneo.somme)}</span>
        <span className="pannello-pratiche__somma-etichetta" aria-hidden="true">
          {testi.totaleAteneo}
        </span>
        {ateneo.somme.map((n, i) => (
          <span
            key={STATI_PANNELLO[i].chiave}
            className="pannello-pratiche__valore"
            data-nullo={n === 0 || undefined}
            aria-hidden="true"
          >
            {n}
          </span>
        ))}
        <span className="pannello-pratiche__totale-ateneo" aria-hidden="true">
          {ateneo.totale}
        </span>
        <span />
      </div>
    </div>
  );
}

function Lista({ ateneo }) {
  return (
    <div className="pannello-pratiche__lista">
      {ateneo.righe.map((riga) => (
        <Tipologia
          key={riga.chiave}
          riga={riga}
          attiva={ateneo.abilitato && !riga.bloccata}
          className="pannello-pratiche__voce"
        >
          <span className="pannello-pratiche__voce-testa">
            <span className="pannello-pratiche__voce-nome">{riga.label}</span>
            <span className="pannello-pratiche__voce-totale">
              {riga.totale}{" "}
              <ChevronRight className="pannello-pratiche__voce-chevron" aria-hidden="true" />
            </span>
          </span>
          <span className="pannello-pratiche__voce-celle">
            {STATI_PANNELLO.map((stato, i) => (
              <span key={stato.chiave} className="pannello-pratiche__voce-cella">
                <span className="pannello-pratiche__voce-stato">
                  <Punto stato={stato} />
                  {testi.stati[stato.chiave]}
                </span>
                <span
                  className="pannello-pratiche__voce-valore"
                  data-nullo={riga.celle[i] === 0 || undefined}
                >
                  {riga.celle[i]}
                </span>
              </span>
            ))}
          </span>
        </Tipologia>
      ))}
      <div className="pannello-pratiche__voce-somma">
        <span className="pannello-pratiche__somma-etichetta">{testi.totaleAteneo}</span>
        <span className="pannello-pratiche__totale-ateneo">{ateneo.totale}</span>
      </div>
    </div>
  );
}

function Ateneo({ ateneo }) {
  return (
    <section className="pannello-pratiche__ateneo">
      <div className="pannello-pratiche__testata">
        <img src={ateneo.logo} alt="" className="pannello-pratiche__logo" />
        <div className="pannello-pratiche__identita">
          <h2 className="pannello-pratiche__nome">{ateneo.titolo}</h2>
          <span className="pannello-pratiche__riepilogo">
            {testi.riepilogoAteneo(ateneo.totale, ateneo.righe.length)}
          </span>
        </div>
      </div>
      <Tabella ateneo={ateneo} />
      <Lista ateneo={ateneo} />
    </section>
  );
}

export default function PannelloPratiche() {
  const [pannello, setPannello] = useState(null);
  const [errore, setErrore] = useState(null);

  useEffect(() => {
    let attivo = true;
    Promise.all([leggi("/clienti/permessi-pratiche"), leggi("/pratiche/conteggi")])
      .then(([permessi, conteggi]) => {
        if (attivo) setPannello(costruisciPannello(BLOCCHI_PRATICHE, conteggi ?? [], permessi ?? {}));
      })
      .catch((err) => attivo && setErrore(err.message ?? testi.erroreCaricamento));
    return () => {
      attivo = false;
    };
  }, []);

  return (
    <div className={stili.pagina}>
      <div className="pannello-pratiche__intestazione">
        <h1 className={stili.titolo}>{testi.titolo}</h1>
        <p className={stili.descrizione}>{testi.descrizione}</p>
      </div>

      {errore ? (
        <AlertMessage message={{ type: "error", text: errore }} separato={false} />
      ) : !pannello ? (
        <IndicatoreCaricamento dimensione="compatto" messaggio={testi.caricamento} />
      ) : (
        <>
          {pannello.senzaAbilitazione && (
            <AlertMessage
              message={{ type: "warning", text: testi.senzaAbilitazione }}
              separato={false}
            />
          )}
          <Striscia pannello={pannello} />
          {pannello.atenei.map((ateneo) => (
            <Ateneo key={ateneo.chiave} ateneo={ateneo} />
          ))}
        </>
      )}
    </div>
  );
}
