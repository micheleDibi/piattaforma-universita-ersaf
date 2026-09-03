import { useState } from "react";
import Sidebar from "./Sidebar";
import ElencoSottoscrittori from "./ElencoSottoscrittori";

export default function Homepage() {
  const [active, setActive] = useState("subscribers");

  return (
    <div className="flex min-h-screen w-screen bg-gray-100 font-sans">
      <Sidebar active={active} setActive={setActive} />

      <main className="flex-1 w-full">
        {active === "dashboard" && (
          <div className="p-6 text-xl font-semibold text-gray-800">
            Benvenuto nella Dashboard
          </div>
        )}

        {active === "subscribers" && (
          <ElencoSottoscrittori key="subscribers" soloAttuatori={false} />
        )}

        {active === "actuators" && (
          <ElencoSottoscrittori key="actuators" soloAttuatori={true} />
        )}
      </main>
    </div>
  );
}
