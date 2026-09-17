import { ChevronRight } from "../../config/icone.js";
import AvvisoTooltip from "./AvvisoTooltip.jsx";

export default function TabellaElenco({ dati, modello, onApri }) {
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
            <span className="sr-only">Azioni</span>
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
            aria-label={`Visualizza ${riga.nomeAzione}`}
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
                        <span
                          className="elenco-adattivo__badge-punto"
                          aria-hidden="true"
                        />
                        <span>{valore}</span>
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
                      className="elenco-adattivo__valore"
                      data-rilievo={campo.rilievo}
                      style={
                        conAvviso
                          ? { display: "inline-flex", alignItems: "center" }
                          : undefined
                      }
                    >
                      <span>{valore}</span>
                      {conAvviso && (
                        <span style={{ marginLeft: "0.85rem" }}>
                          <AvvisoTooltip messaggi={avviso} />
                        </span>
                      )}
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
