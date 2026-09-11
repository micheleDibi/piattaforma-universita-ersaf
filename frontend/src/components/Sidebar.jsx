import { useNavigate } from "react-router";
import { leggiRuolo } from "../lib/sessione";
import { logout } from "../lib/logout";

function Sidebar({ active, setActive }) {
  const navigate = useNavigate();
  const canSee = leggiRuolo() === "aderente";

  const links = [
    { id: "dashboard", label: "Dashboard" },
    { id: "sottoscrittori", label: "Elenco Sottoscrittori" },
    { id: "attuatori", label: "Elenco Attuatori", visible: canSee },
    { id: "aziende", label: "Elenco Aziende", visible: canSee },
    { id: "pratiche", label: "Elenco Pratiche", visible: canSee },
    { id: "prodotti", label: "Elenco prodotti", visible: canSee },
  ].filter((link) => link.visible != false);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <aside className="w-64 bg-superficie border-r border-bordo p-4 flex flex-col shrink-0 h-screen sticky top-0">
      <h2 className="text-xl font-bold mb-6 px-2 text-testo">Il mio App</h2>

      {/* Navigazione e pulsante Esci raggruppati */}
      <div className="flex flex-col gap-6">
        <nav className="space-y-1">
          {links.map((link) => (
            <button
              type="button"
              key={link.id}
              onClick={() => setActive(link.id)}
              className={`w-full text-left px-3 py-2 rounded-controllo font-medium transition-colors cursor-pointer ${
                active === link.id
                  ? "bg-primario text-su-primario"
                  : "text-testo-tenue hover:bg-superficie-alta"
              }`}
            >
              {link.label}
            </button>
          ))}
        </nav>

        <button
          type="button"
          onClick={handleLogout}
          className="w-full text-left px-3 py-2 rounded-controllo font-medium text-negativo hover:bg-negativo-tenue transition-colors cursor-pointer border-t border-bordo pt-4"
        >
          Esci
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
