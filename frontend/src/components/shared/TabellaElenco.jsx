import { useId } from "react";
import { ChevronRight } from "../../config/icone.js";
import AvvisoTooltip from "./AvvisoTooltip.jsx";
import IndicatoriStato from "./IndicatoriStato.jsx";
import { campoIndicatori, idIndicatori } from "../../lib/righeElenco.js";
import { TESTI_ELENCO } from "../../config/testi/elenco.js";

export default function TabellaElenco({ dati, modello, onApri }) {
  const base = useId();
  const indicatori = campoIndicatori(modello.colonne.flatMap((colonna) => colonna.campi));
  return (
    <table className="elenco-adattivo__tabella">
      <caption className="sr-only">{modello.etichetta}</caption>
      <colgroup>
        {modello.colonne.map((colonna) => (
          <col key={colonna.id} data-colonna={colonna.id} />
        ))}
        <col data-colonna="azioni" />
      </colgroup>
      <thead>
        <tr>
          {modello.colonne.map((colonna) => (
            <th key={colonna.id} scope="col">
              {colonna.etichetta}
            </th>
          ))}
          <th scope="col">
            <span className="sr-only">{TESTI_ELENCO.colonnaAzioni}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {dati.map((riga) => (
          <tr
            key={riga.id}
            onClick={() => onApri(riga.id)}
            onKeyDown={(evento) => {
              if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                onApri(riga.id);
              }
            }}
            tabIndex={0}
            role="button"
            aria-label={TESTI_ELENCO.visualizza(riga.nomeAzione)}
            aria-describedby={idIndicatori(base, riga, indicatori)}
          >
            {modello.colonne.map((colonna) => (
              <td key={colonna.id}>
                {colonna.campi.map((campo) => {
                  const valore = riga.campi[campo.id];
                  if (campo.rilievo === "stato") {
                    return (
                      <span
                        key={campo.id}
                        className="elenco-adattivo__badge"
                        data-tono={riga.tonoStato}
                      >
                        {campo.puntino !== false && (
                          <span
                            className="elenco-adattivo__badge-punto"
                            aria-hidden="true"
                          />
                        )}
                        <span>{valore}</span>
                      </span>
                    );
                  }
                  if (campo.rilievo === "indicatori") {
                    return (
                      <IndicatoriStato key={campo.id} indicatori={valore}
                        id={idIndicatori(base, riga, indicatori)} />
                    );
                  }
                  if (campo.rilievo === "persona") {
                    return (
                      <span key={campo.id} className="elenco-adattivo__persona">
                        <span className="elenco-adattivo__iniziali" aria-hidden="true">
                          {riga.iniziali}
                        </span>
                        <span className="elenco-adattivo__valore" data-rilievo="principale"
                          title={campo.righe ? valore : undefined}>
                          {valore}
                        </span>
                        <AvvisoTooltip messaggi={riga.campi.avviso} />
                      </span>
                    );
                  }
                  if (campo.rilievo === "codice") {
                    return (
                      <span key={campo.id} className="elenco-adattivo__codice">
                        {valore}
                      </span>
                    );
                  }
                  const avviso = riga.campi.avviso;
                  const conAvviso =
                    modello.avvisoDopo === campo.id && avviso?.length > 0;
                  return (
                    <span
                      key={campo.id}
                      className={
                        conAvviso
                          ? "elenco-adattivo__valore elenco-adattivo__valore--con-avviso"
                          : "elenco-adattivo__valore"
                      }
                      data-rilievo={campo.rilievo}
                      // Con `righe` il valore puo' essere tagliato: il title lo
                      // mostra per intero al passaggio del puntatore.
                      title={campo.righe ? valore : undefined}
                    >
                      <span>{valore}</span>
                      {conAvviso && <AvvisoTooltip messaggi={avviso} />}
                    </span>
                  );
                })}
              </td>
            ))}
            <td className="elenco-adattivo__azione" aria-hidden="true">
              <ChevronRight className="elenco-adattivo__chevron inline-block" />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
