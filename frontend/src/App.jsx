import { BrowserRouter, Route, Routes } from "react-router";
import "./App.css";

import Login from "./components/Login";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import Homepage from "./components/Homepage";
import ElencoClienti from "./components/ElencoClienti";
import ElencoAziende from "./components/ElencoAziende";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route path="/elenco" element={<ElencoClienti />} />
        <Route path="/home" element={<Homepage />} />
        <Route path="/nuovo" element={<NuovoSottoscrittore />} />
        <Route path="/modifica/:id" element={<NuovoSottoscrittore />} />
        <Route path="/aziende" element={<ElencoAziende />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
