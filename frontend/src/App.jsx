import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import "./App.css";

import Login from "./components/Login";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import Homepage from "./components/Homepage";
import ElencoClienti from "./components/ElencoClienti";
import ElencoAziende from "./components/ElencoAziende";
import PasswordDimenticata from "./components/PasswordDimenticata";
import ReimpostaPassword from "./components/ReimpostaPassword";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/password-dimenticata" element={<PasswordDimenticata />} />
        <Route path="/reimposta-password" element={<ReimpostaPassword />} />

        <Route path="/elenco" element={<ElencoClienti />} />
        <Route path="/home" element={<Homepage />} />
        <Route path="/nuovo" element={<NuovoSottoscrittore />} />
        <Route path="/modifica/:id" element={<NuovoSottoscrittore />} />
        <Route path="/aziende" element={<ElencoAziende />} />
        {/* Il difetto che ha prodotto il bug di /nazionale non era la rotta
            mancante: era che una rotta assente non produce alcun segnale e
            lascia una pagina bianca. Vale anche per un refuso nel link della
            mail di reset. Non si registra un segnaposto /nazionale: sarebbe
            una pagina irraggiungibile, perche' per quel ruolo il backend esce
            prima con requires_2fa, e il 2FA e' fuori perimetro. */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
