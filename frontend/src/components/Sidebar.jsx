function Sidebar({ active, setActive }) {
  const ruoloCodice = localStorage.getItem("ruolo_codice");
  const canSee = ruoloCodice === "Aderente";
  const links = [
    { id: "dashboard", label: "Dashboard" },
    { id: "sottoscrittori", label: "Elenco Sottoscrittori" },
    { id: "attuatori", label: "Elenco Attuatori", visible: canSee },
  ].filter((link) => link.visible != false);

  return (
    <aside className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col shrink-0 h-screen">
      <h2 className="text-xl font-bold mb-6 px-2 text-gray-800">Il mio App</h2>

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
  );
}
export default Sidebar;
