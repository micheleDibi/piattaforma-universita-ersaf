import { ChevronRight } from "../../config/icone.js";

// Composizione nativa della tabella: colonne e campi sono
// dichiarati dal modello, senza componenti cosmetici per celle o singoli testi.
export default function TabellaElenco({ dati, modello, onApri }) {
  return (
    <table className="elenco-adattivo__tabella">
      <caption className="sr-only">{modello.etichetta}</caption>
      <colgroup>
        {modello.colonne.map((colonna) => <col key={colonna.id} data-colonna={colonna.id} />)}
        <col data-colonna="azioni" />
      </colgroup>
      <thead>
        <tr>
          {modello.colonne.map((colonna) => <th key={colonna.id} scope="col">{colonna.etichetta}</th>)}
          <th scope="col"><span className="sr-only">Azioni</span></th>
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
                      <span key={campo.id} className="elenco-adattivo__badge" data-tono={riga.tonoStato}>
                        <span className="elenco-adattivo__badge-punto" aria-hidden="true" />
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
                  return (
                    <span key={campo.id} className="elenco-adattivo__valore" data-rilievo={campo.rilievo}>
                      {valore}
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
