import { useRef } from "react";
import { useTestataElenco } from "../../hooks/useTestataElenco.js";
import FiltriElenco from "./FiltriElenco.jsx";

/** Titolo, ricerca e azioni restano gli stessi nodi anche durante l'aggancio. */
export default function IntestazioneElenco({ titolo, azioni, ricerca, filtri }) {
  const soglia = useRef(null);
  const testata = useRef(null);
  useTestataElenco(soglia, testata);
  return (
    <>
      <div ref={soglia} className="soglia-testata-elenco" aria-hidden="true" />
      <div ref={testata} className="testata-elenco">
        <header className="testata-elenco__contenuto" aria-label={titolo}
          data-filtri={Boolean(filtri)}>
          <h1 className="testata-elenco__titolo">{titolo}</h1>
          <search className="testata-elenco__strumenti" aria-label={titolo}>
            <div className="testata-elenco__ricerca">{ricerca}</div>
            {filtri && <FiltriElenco {...filtri} />}
          </search>
          <div className="testata-elenco__azioni">{azioni}</div>
        </header>
      </div>
    </>
  );
}
