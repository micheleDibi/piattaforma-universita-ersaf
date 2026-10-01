import { suffissoCampo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import {
  intestazioneCampi,
  rigaCampi,
  tabellaCampi,
} from "../config/styles/tabella";
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import { CONVENZIONI } from "../config/campiPercentuali.js";
import { messaggioAzzeramentoFiglie } from "../lib/schedaAzienda.js";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";

const TESTI = TESTI_AZIENDA.convenzioni;

// Sola presentazione: lettura, scrittura, salvataggio e la conferma
// dell'azzeramento a cascata vivono in useDettaglioConvenzioni.js, condiviso
// da chi la mostra in sola lettura (scheda dell'attuatore) e da chi la
// mostra in scrittura (scheda dell'azienda). Non ha piu' un pulsante di
// salvataggio proprio: in scrittura lo aziona "Salva modifiche" della scheda
// azienda, che deve fermarsi per la conferma prima di salvare anche
// l'anagrafica (vedi SchedaAzienda.jsx).
//
// inSezione: dentro una SezioneModulo, che porta titolo e descrizione.
// Altrimenti (scheda Azienda dell'attuatore) il blocco ha un titolo proprio.
// soloLettura: la scheda dell'attuatore mostra le percentuali dell'azienda
// associata solo in visione, perche' si modificano dalla scheda dell'azienda
// (che le applica anche alle aziende figlie): niente input, niente conferma.
export default function DettaglioConvenzioniUniversitarie({
  dettaglio,
  caricamento,
  errore,
  onChangePercentuale,
  resetPendente,
  onConferma,
  onAnnulla,
  salvataggio,
  soloLettura = false,
  inSezione = false,
}) {
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
          onChange={onChangePercentuale}
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

      {!soloLettura && resetPendente && (
        <div className={stili.conferma}>
          <div className={stili.messaggioConferma}>
            <AlertMessage
              message={{
                type: "warning",
                text: messaggioAzzeramentoFiglie(resetPendente),
                nota: TESTI_AZIENDA.azzeramento.notaFiglie,
              }}
              separato={false}
            />
          </div>
          <div className={stili.pulsantiConferma}>
            <button
              type="button"
              onClick={onConferma}
              disabled={salvataggio}
              className={pulsante("primario", "piccolo")}
            >
              {TESTI_AZIENDA.azzeramento.conferma}
            </button>
            <button
              type="button"
              onClick={onAnnulla}
              className={pulsante("testuale", "piccolo")}
            >
              {TESTI_AZIENDA.azzeramento.annulla}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
