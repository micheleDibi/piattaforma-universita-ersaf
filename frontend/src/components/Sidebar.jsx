import { useState } from "react";
import ElencoSottoscrittori from "./ElencoSottoscrittori";

function Sidebar() {
  const [active, setActive] = useState("dashboard");

  const links = [
    { id: "dashboard", label: "Dashboard" },
    { id: "subscribers", label: "Elenco Sottoscrittori" },
    { id: "actuators", label: "Elenco Attuatori" },
  ];

  // Funzione per decidere cosa mostrare a destra in base al link attivo
  const renderContent = () => {
    switch (active) {
      case "dashboard":
        return (
          <div className="p-6 text-xl font-semibold text-gray-800">
            Benvenuto nella Dashboard
          </div>
        );
      case "subscribers":
        return <ElencoSottoscrittori soloAttuatori={false} />;
      case "actuators":
        return <ElencoSottoscrittori soloAttuatori={true} />;
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans overflow-hidden">
      <aside className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col shrink-0">
        <h2 className="text-xl font-bold mb-6 px-2 text-gray-800">
          Il mio App
        </h2>

        <nav className="space-y-1 flex-1">
          {links.map((link) => (
            <button
              key={link.id}
              onClick={() => setActive(link.id)}
              className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors cursor-pointer ${
                active === link.id
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {link.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Area principale dei contenuti a destra (con scroll indipendente) */}
      <main className="flex-1 overflow-y-auto">{renderContent()}</main>
    </div>
  );
}

export default Sidebar;
