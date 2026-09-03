import { BrowserRouter, Route, Routes } from "react-router";
import "./App.css";

import Login from "./components/Login";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import Homepage from "./components/Homepage";
import ElencoSottoscrittori from "./components/ElencoSottoscrittori";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route path="/elenco" element={<ElencoSottoscrittori />} />
        <Route path="/home" element={<Homepage />} />
        <Route path="/nuovo" element={<NuovoSottoscrittore />} />
        <Route path="/modifica/:id" element={<NuovoSottoscrittore />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
