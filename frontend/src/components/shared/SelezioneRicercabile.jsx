import { useId, useState } from "react";
import { X } from "../../config/icone";
import { campo, spunta } from "../../config/styles/campo";
import { pulsante, pulsanteIcona } from "../../config/styles/pulsante";
import { cambiaSelezione, paginaOpzioni } from "../../lib/selezioneRicercabile";
import usePagineRemote from "../../hooks/usePagineRemote";

// Ricerca remota e selezioni indipendenti: cercare un altro nome non perde le scelte.
export default function SelezioneRicercabile({ configurazione, selezionati, onCambia }) {
  const id = useId();
  const [ricerca, setRicerca] = useState("");
  const { titolo, endpoint, multipla, segnaposto } = configurazione;
  const pagina = usePagineRemote(`${endpoint}?limit=20&search=${encodeURIComponent(ricerca)}`, paginaOpzioni);
  return <fieldset className="selezione-ricercabile" onBlur={event => {
    if (!event.currentTarget.contains(event.relatedTarget)) setRicerca("");
  }}>
    <legend>{titolo}</legend>
    {!!selezionati.length && <ul className="selezione-ricercabile__scelte" aria-label={`${titolo} selezionati`}>
      {selezionati.map(opzione => <li key={opzione.id}>
        <span>{opzione.label}<small>{opzione.dettaglio}</small></span>
        <button type="button" className={pulsanteIcona("neutro", "grande")}
          aria-label={`Rimuovi ${opzione.label}`}
          onClick={() => onCambia(selezionati.filter(item => item.id !== opzione.id))}><X aria-hidden="true" /></button>
      </li>)}
    </ul>}
    <input type="search" className={campo()} value={ricerca} placeholder={segnaposto}
      aria-label={`Cerca ${titolo.toLowerCase()}`} aria-controls={`${id}-risultati`}
      onChange={event => setRicerca(event.target.value)} />
    <div id={`${id}-risultati`} className="selezione-ricercabile__risultati" aria-busy={pagina.loading}>
      {pagina.elementi.map(opzione => <label key={opzione.id}>
        <input type={multipla ? "checkbox" : "radio"} name={id} className={spunta()}
          checked={selezionati.some(item => item.id === opzione.id)}
          disabled={multipla && selezionati.length >= 100 && !selezionati.some(item => item.id === opzione.id)}
          onChange={() => onCambia(cambiaSelezione(selezionati, opzione, multipla))} />
        <span>{opzione.label}<small>{opzione.dettaglio}</small></span>
      </label>)}
      <p role="status">{pagina.loading ? "Ricerca in corso…" : !pagina.errore && !pagina.elementi.length ? "Nessun risultato." : ""}</p>
      {pagina.errore && <p role="alert">{pagina.errore}</p>}
      {(pagina.altri || pagina.errore) && <button type="button" disabled={pagina.loading}
        className={pulsante("discreto")} onClick={pagina.carica}>{pagina.errore ? "Riprova" : "Mostra altri"}</button>}
    </div>
  </fieldset>;
}
