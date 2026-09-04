import { useState } from "react";
import Sidebar from "./Sidebar";
import ElencoClienti from "./ElencoClienti";
import ElencoAziende from "./ElencoAziende";

export default function Homepage() {
  const [active, setActive] = useState("sottoscrittori");

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
          <ElencoClienti key="sottoscrittori" soloAttuatori={false} />
        )}

        {active === "attuatori" && (
          <ElencoClienti key="attuatori" soloAttuatori={true} />
        )}

        {active === "aziende" && (
          <ElencoAziende key="aziende" soloAttuatori={true} />
        )}
      </main>
    </div>
  );
}
