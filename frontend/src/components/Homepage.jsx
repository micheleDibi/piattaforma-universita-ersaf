import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import ElencoClienti from "./ElencoClienti";
import ElencoAziende from "./ElencoAziende";
import ElencoProdottiFormativi from "./ElencoProdottiFormativi";

export default function Homepage() {
  // Legge da localStorage la tab salvata, altrimenti parte da "sottoscrittori"
  const [active, setActive] = useState(() => {
    return localStorage.getItem("home_active_tab") || "sottoscrittori";
  });

  // Salva su localStorage ogni volta che la tab attiva cambia
  useEffect(() => {
    localStorage.setItem("home_active_tab", active);
  }, [active]);

  return (
    <div className="flex min-h-screen w-screen bg-gray-100 font-sans">
      <Sidebar active={active} setActive={setActive} />

      <main className="flex-1 w-full">
        {active === "dashboard" && (
          <div className="p-6 text-xl font-semibold text-gray-800">
            Benvenuto nella Dashboard
          </div>
        )}

        {active === "sottoscrittori" && (
          <ElencoClienti
            key="sottoscrittori"
            soloAttuatori={false}
            soloUtenti={true}
          />
        )}

        {active === "attuatori" && (
          <ElencoClienti key="attuatori" soloAttuatori={true} />
        )}

        {active === "aziende" && (
          <ElencoAziende key="aziende" soloAttuatori={true} />
        )}

        {active === "prodotti" && (
          <ElencoProdottiFormativi key="prodotti" soloAttuatori={true} />
        )}
      </main>
    </div>
  );
}
