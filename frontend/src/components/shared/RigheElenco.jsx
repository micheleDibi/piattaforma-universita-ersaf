import TabellaElenco from "./TabellaElenco.jsx";
import ListaElenco from "./ListaElenco.jsx";
import { statoVuoto } from "../../config/styles/tabella.js";

/** Due presentazioni native degli stessi dati; solo quella visibile è accessibile.
 * Nessun controllo con stato viene duplicato: ricerca e filtri restano nella testata. */
export default function RigheElenco({ dati, modello, onApri, vuoto }) {
  return (
    <div className="elenco-adattivo" data-modello={modello.id} data-ampiezza={modello.ampiezza}>
      {dati.length === 0 ? (
        vuoto && <p className={statoVuoto()} role="status">{vuoto}</p>
      ) : (
        <>
          <TabellaElenco dati={dati} modello={modello} onApri={onApri} />
          <ListaElenco dati={dati} modello={modello} onApri={onApri} />
        </>
      )}
    </div>
  );
}
