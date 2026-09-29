import { useId } from "react";
import { Link } from "react-router";
import { ChevronRight } from "../../config/icone.js";
import { scheda } from "../../config/styles/superficie.js";
import { TESTI_DASHBOARD } from "../../config/testi/dashboard.js";
import { scorciatoieDashboard } from "../../lib/dashboard.js";

/**
 * Scorciatoie della Dashboard: le sezioni che il ruolo vede nel menu, tranne
 * la Dashboard, ciascuna con icona, nome e una riga di descrizione. Statiche:
 * niente dati e niente chiamate. Il collegamento copre tutta la cella e il
 * fuoco si disegna sulla cella (config/styles/dashboard.css).
 *
 * @param {{ ruolo?: string }} props  ruolo della sessione, gia' normalizzato
 */
export default function ScorciatoieDashboard({ ruolo }) {
  const id = useId();
  const idTitolo = `${id}-titolo`;

  return (
    <section className="dashboard__scorciatoie" aria-labelledby={idTitolo}>
      <h2 id={idTitolo} className="sr-only">{TESTI_DASHBOARD.titoloScorciatoie}</h2>
      <div className={`${scheda()} overflow-clip`}>
        <ul role="list" className="dashboard__griglia">
          {scorciatoieDashboard(ruolo).map(({ rotta, etichetta, icona: Icona, descrizione }, indice) => {
            const idDescrizione = `${id}-descrizione-${indice}`;
            return (
              <li key={rotta} className="dashboard__scorciatoia">
                <span className="dashboard__icona">
                  <Icona aria-hidden="true" />
                </span>
                <Link to={rotta} className="dashboard__collegamento" aria-describedby={idDescrizione}>
                  <span className="dashboard__nome">{etichetta}</span>
                </Link>
                <p id={idDescrizione} className="dashboard__descrizione">{descrizione}</p>
                <ChevronRight aria-hidden="true" className="dashboard__freccia" />
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
