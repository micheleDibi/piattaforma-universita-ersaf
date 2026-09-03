import { BrowserRouter, Route, Routes } from "react-router";
import "./App.css";
import ElencoSottoscrittori from "./components/ElencoSottoscrittori";
import Login from "./components/Login";
import NuovoSottoscrittore from "./components/NuovoSottoscrittore";
import Sidebar from "./components/Sidebar";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/side" element={<Sidebar />} />
        <Route path="/elenco" element={<ElencoSottoscrittori />} />
        <Route path="/nuovo" element={<NuovoSottoscrittore />} />
        <Route path="/modifica/:id" element={<NuovoSottoscrittore />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
