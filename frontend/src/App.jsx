import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import "./App.css";

import Login from "./components/Login";
import PasswordDimenticata from "./components/PasswordDimenticata";
import ReimpostaPassword from "./components/ReimpostaPassword";
import GuscioApplicazione from "./components/shell/GuscioApplicazione";
import RichiediSessione from "./components/shell/RichiediSessione";
import Dashboard from "./components/Dashboard";
import MioProfilo from "./components/MioProfilo";
import ElencoClienti from "./components/ElencoClienti";
import ElencoAziende from "./components/ElencoAziende";
import ElencoPratiche from "./components/ElencoPratiche";
import ElencoProdottiFormativi from "./components/ElencoProdottiFormativi";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import SchedaUtente from "./components/SchedaUtente";
import SchedaAzienda from "./components/SchedaAzienda";
import InserimentoProdotto from "./components/InserimentoProdotto";
import { ROTTA_INIZIALE, ROTTE } from "./config/routes/rotte";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Pagine pubbliche, fuori dal guscio. */}
        <Route path={ROTTE.accesso} element={<Login />} />
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

          <Route path="/nuovo" element={<NuovoSottoscrittore />} />
          <Route path="/modifica/:id" element={<NuovoSottoscrittore />} />
          <Route path="/utente/:id" element={<SchedaUtente />} />
          <Route path="/nuova-azienda" element={<SchedaAzienda />} />
          <Route path="/modifica-azienda/:id" element={<SchedaAzienda />} />
          <Route path="/inserimentoprodotto" element={<InserimentoProdotto />} />
          <Route
            path="/inserimentoprodotto/:id"
            element={<InserimentoProdotto />}
          />
        </Route>

        {/* Rotte storiche: ci puntano collegamenti esistenti e segnalibri. */}
        <Route path="/home" element={<Navigate to={ROTTA_INIZIALE} replace />} />
        <Route
          path="/elenco"
          element={<Navigate to={ROTTE.sottoscrittori} replace />}
        />
        <Route
          path="/prodotti-formativi"
          element={<Navigate to={ROTTE.prodotti} replace />}
        />

        {/* Il secondo fattore rimane nel flusso di accesso; le rotte sono protette dalla sessione cookie. */}
        <Route path="*" element={<Navigate to={ROTTE.accesso} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
