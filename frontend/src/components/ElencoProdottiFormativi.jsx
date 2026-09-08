import { useEffect, useState } from "react";

export default function ElencoProdottiFormativi() {
  const [prodotti, setProdotti] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("Tutti i tipi");
  const [loading, setLoading] = useState(true);

  // Recupero dei dati dal backend FastAPI
  useEffect(() => {
    fetch("http://localhost:8000/listini-testa/")
      .then((res) => res.json())
      .then((data) => {
        setProdotti(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Errore nel recupero dei listini:", err);
        setLoading(false);
      });
  }, []);

  const handleModifica = (id) => {
    console.log("Modifica prodotto con id:", id);
  };

  // Filtraggio basato sulla ricerca e sul tipo
  const prodottiFiltrati = prodotti.filter((prodotto) => {
    const matchSearch =
      prodotto.listTesta_descrizione
        ?.toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      prodotto.listTesta_codice
        ?.toLowerCase()
        .includes(searchTerm.toLowerCase());

    const matchTipo =
      filtroTipo === "Tutti i tipi" ||
      prodotto.listino_tipoCorso_descrizione === filtroTipo;

    return matchSearch && matchTipo;
  });

  return (
    <div className="p-6 bg-gray-50 min-h-screen font-sans">
      {/* Header con Titolo, Barra di Ricerca e Pulsante Nuovo */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-800">
          Elenco Prodotti Formativi:
        </h1>

        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-80">
            <input
              type="text"
              placeholder="Cerca per titolo o codice..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-gray-600 placeholder-gray-400 shadow-sm"
            />
          </div>

          <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-md text-sm transition-colors shadow-sm whitespace-nowrap">
            Nuovo Prodotto
          </button>
        </div>
      </div>

      {/* Filtro a tendina secondario */}
      <div className="mb-6">
        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="bg-white border border-gray-300 text-gray-700 text-sm rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm w-full md:w-56"
        >
          <option>Tutti i tipi</option>
          <option>Laurea Triennale</option>
          <option>Master</option>
          <option>Corso di Perfezionamento</option>
        </select>
      </div>

      {/* Tabella Paginata / Contenitore */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-200 text-gray-500 text-xs font-semibold tracking-wider bg-gray-50/50">
              <th className="py-3 px-4">UNIVERSITÀ</th>
              <th className="py-3 px-4">CODICE / SSID</th>
              <th className="py-3 px-4">TITOLO</th>
              <th className="py-3 px-4">TIPO PRODOTTO</th>
              <th className="py-3 px-4">ATTIVO</th>
              <th className="py-3 px-4 text-right">MODIFICA</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-sm text-gray-700">
            {loading ? (
              <tr>
                <td colSpan="6" className="py-6 text-center text-gray-500">
                  Caricamento in corso...
                </td>
              </tr>
            ) : prodottiFiltrati.length === 0 ? (
              <tr>
                <td colSpan="6" className="py-6 text-center text-gray-500">
                  Nessun prodotto trovato.
                </td>
              </tr>
            ) : (
              prodottiFiltrati.map((prodotto) => {
                const isAttivo = prodotto.listino_attivoSN === 1;
                return (
                  <tr
                    key={prodotto.listTesta_id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-4 px-4 font-medium text-gray-900">
                      {prodotto.nome_universita || "-"}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {prodotto.listTesta_codice}
                    </td>
                    <td className="py-4 px-4 text-gray-800">
                      {prodotto.listTesta_descrizione}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {prodotto.listino_tipoCorso_descrizione || "-"}
                    </td>
                    <td className="py-4 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          isAttivo
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {isAttivo ? "Sì" : "No"}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <button
                        onClick={() => handleModifica(prodotto.listTesta_id)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-3 py-1.5 rounded text-xs transition-colors shadow-sm"
                      >
                        Modifica
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
