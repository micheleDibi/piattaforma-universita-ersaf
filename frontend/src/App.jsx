import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import "./App.css";

import Login from "./components/Login";
import VerificaOtp from "./components/VerificaOtp";
import RouteGuard from "./lib/RouteGuard";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import Homepage from "./components/Homepage";
import ElencoClienti from "./components/ElencoClienti";
import ElencoAziende from "./components/ElencoAziende";
import PasswordDimenticata from "./components/PasswordDimenticata";
import ReimpostaPassword from "./components/ReimpostaPassword";
import SchedaUtente from "./components/SchedaUtente";
import SchedaAzienda from "./components/SchedaAzienda";
import ElencoProdottiFormativi from "./components/ElencoProdottiFormativi";
import InserimentoProdotto from "./components/InserimentoProdotto";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Pubbliche: raggiungibili senza token */}
        <Route path="/" element={<Login />} />
        <Route path="/verifica-otp" element={<VerificaOtp />} />
        <Route path="/password-dimenticata" element={<PasswordDimenticata />} />
        <Route path="/reimposta-password" element={<ReimpostaPassword />} />

        {/* Protette: senza token, RouteGuard rimanda a "/" */}
        <Route element={<RouteGuard />}>
          <Route
            path="/prodotti-formativi"
            element={<ElencoProdottiFormativi />}
          />
          <Route path="/elenco" element={<ElencoClienti />} />
          <Route
            path="/inserimentoprodotto"
            element={<InserimentoProdotto />}
          />
          <Route
            path="/inserimentoprodotto/:id"
            element={<InserimentoProdotto />}
          />
          <Route path="/home" element={<Homepage />} />
          <Route path="/nuovo" element={<NuovoSottoscrittore />} />
          <Route path="/modifica/:id" element={<NuovoSottoscrittore />} />
          <Route path="/aziende" element={<ElencoAziende />} />
          <Route path="/nuova-azienda" element={<SchedaAzienda />} />
          <Route path="/modifica-azienda/:id" element={<SchedaAzienda />} />
          <Route path="/utente/:id" element={<SchedaUtente />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
