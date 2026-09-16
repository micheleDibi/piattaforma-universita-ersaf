import { BrowserRouter, Route, Routes } from "react-router";
import "./App.css";

import Login from "./components/Login";
import PasswordDimenticata from "./components/PasswordDimenticata";
import ReimpostaPassword from "./components/ReimpostaPassword";
import GuscioApplicazione from "./components/shell/GuscioApplicazione";
import RichiediSessione from "./components/shell/RichiediSessione";
import SoloOspiti from "./components/shell/SoloOspiti";
import Dashboard from "./components/Dashboard";
import MioProfilo from "./components/MioProfilo";
import ElencoClienti from "./components/ElencoClienti";
import ElencoAziende from "./components/ElencoAziende";
import ElencoPratiche from "./components/ElencoPratiche";
import ElencoProdottiFormativi from "./components/ElencoProdottiFormativi";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import SchedaPratica from "./components/SchedaPratica.jsx";
import PaginaNonTrovata from "./components/PaginaNonTrovata.jsx";
import PaginaEntita from "./components/shell/PaginaEntita.jsx";
import SchedaAzienda from "./components/SchedaAzienda";
import InserimentoProdotto from "./components/InserimentoProdotto";
import { PERCORSI, ROTTE } from "./config/routes/percorsi.js";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Pagine pubbliche, fuori dal guscio; il login rimanda dentro chi ha una sessione valida. */}
        <Route path={ROTTE.accesso} element={<SoloOspiti><Login /></SoloOspiti>} />
        <Route path={ROTTE.recuperoPassword} element={<PasswordDimenticata />} />
        <Route path={ROTTE.reimpostaPassword} element={<ReimpostaPassword />} />

        {/* Pagine autenticate: elenchi e dettagli condividono il guscio, quindi
            la barra laterale resta visibile ovunque. */}
        <Route element={<RichiediSessione><GuscioApplicazione /></RichiediSessione>}>
          <Route path={ROTTE.dashboard} element={<Dashboard />} />
          <Route path={ROTTE.profilo} element={<MioProfilo />} />
          <Route
            path={ROTTE.sottoscrittori}
            element={
              <ElencoClienti
                key="sottoscrittori"
                soloAttuatori={false}
                soloUtenti={true}
              />
            }
          />
          <Route
            path={ROTTE.attuatori}
            element={<ElencoClienti key="attuatori" soloAttuatori={true} />}
          />
          <Route
            path={ROTTE.aziende}
            element={<ElencoAziende soloAttuatori={true} />}
          />
          <Route path={ROTTE.pratiche} element={<ElencoPratiche />} />
          <Route
            path={ROTTE.prodotti}
            element={<ElencoProdottiFormativi soloAttuatori={true} />}
          />

          {[
            [PERCORSI.sottoscrittori, <NuovoSottoscrittore tipoUtente="sottoscrittore" />],
            [PERCORSI.attuatori, <NuovoSottoscrittore tipoUtente="attuatore" />],
            [PERCORSI.aziende, <SchedaAzienda />],
            [PERCORSI.prodotti, <InserimentoProdotto />],
            [PERCORSI.pratiche, <SchedaPratica />],
          ].flatMap(([risorsa, pagina]) => [risorsa.nuovo, risorsa.modello].map(path => (
            <Route key={path} path={path} element={<PaginaEntita risorsa={risorsa}>{pagina}</PaginaEntita>} />
          )))}
        </Route>

        <Route path="*" element={<PaginaNonTrovata />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
