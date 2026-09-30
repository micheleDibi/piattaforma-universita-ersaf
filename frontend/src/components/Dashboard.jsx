import IntestazionePagina from "./shared/IntestazionePagina";
import ScorciatoieDashboard from "./dashboard/ScorciatoieDashboard.jsx";
import ModuloEduNews24 from "./edunews24/ModuloEduNews24.jsx";
import { contenutoPagina } from "../config/styles/pagina";
import { TESTI_DASHBOARD } from "../config/testi/dashboard.js";
import { useSessione } from "../hooks/useSessione.js";
import { descrizioneDashboard } from "../lib/dashboard.js";

/**
 * Pagina d'arrivo dopo l'accesso: benvenuto con il solo nome della sessione,
 * scorciatoie alle sezioni del menu del ruolo e, sotto, i moduli (oggi
 * EduNews24, che con la funzione spenta non disegna nulla e non sposta il
 * resto). Composizione in config/styles/dashboard.css.
 */
export default function Dashboard() {
  const sessione = useSessione();

  return (
    <div className={contenutoPagina()}>
      <div className="dashboard">
        <IntestazionePagina
          titolo={TESTI_DASHBOARD.titolo}
          descrizione={descrizioneDashboard(sessione)}
        />
        <ScorciatoieDashboard ruolo={sessione?.ruoloCodice} />
        <div className="dashboard__moduli">
          <ModuloEduNews24 />
        </div>
      </div>
    </div>
  );
}
