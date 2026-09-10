import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { API_BASE_URL } from "../lib/api";
import AlertMessage from "./ALertMessage";
import ProdottoFormInfo from "./ProdottoFormInfo";
import ProdottoDettagliTabella from "./ProdottoDettagliTabella";

export default function InserimentoProdotto() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    listTesta_codice: "",
    listTesta_descrizione: "",
    listTesta_livello: "",
    listino_tipo_id: 2,
    listino_modalita_id: "",
    listino_tipoCorso_id: 8,
    listino_durataLaurea_id: "",
    listino_facolta_id: "",
    listino_corsoLaurea_id: "",
    nome_universita_id: "",
    listino_attivoSN: -1,
    listTesta_created_by: 1,
  });

  const [dettagli, setDettagli] = useState([
    {
      listDettaglio_dataInizioValidazione: "",
      listDettaglio_dataFineValidazione: "9999-12-31",
      listDettaglio_prezzo: "",
      listDettaglio_durata: "",
      listDettaglio_CFU: "",
      listDettaglio_tasse: "",
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const fetchNextCode = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/listini-testa/next-code`,
      );
      if (response.ok) {
        const data = await response.json();
        if (data.codice) {
          setFormData((prev) => ({
            ...prev,
            listTesta_codice: data.codice,
          }));
        }
      }
    } catch (err) {
      console.error("Errore nel recupero del codice automatico:", err);
    }
  };

  useEffect(() => {
    const utenteId = localStorage.getItem("utente_id");
    if (utenteId) {
      setFormData((prev) => ({
        ...prev,
        listTesta_created_by: Number(utenteId),
      }));
    }
    fetchNextCode();
  }, []);

  const handleGeneraCodice = async () => {
    await fetchNextCode();
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    let val;
    if (type === "checkbox") {
      val = checked ? -1 : 0;
    } else if (value === "") {
      val = "";
    } else if (name.endsWith("_id") || name === "listTesta_livello") {
      val = Number(value);
    } else {
      val = value;
    }

    setFormData((prev) => {
      const updated = { ...prev, [name]: val };
      if (name === "listino_tipoCorso_id") {
        updated.listino_tipo_id = val === 8 ? 2 : 1;
      }
      return updated;
    });
  };

  const handleDettaglioChange = (index, e) => {
    const { name, value } = e.target;
    const newDettagli = [...dettagli];

    let val = value;
    if (value === "") {
      val = null;
    } else if (["listDettaglio_prezzo", "listDettaglio_tasse"].includes(name)) {
      val = parseFloat(value);
    } else if (["listDettaglio_durata", "listDettaglio_CFU"].includes(name)) {
      val = parseInt(value, 10);
    }

    newDettagli[index][name] = val;
    setDettagli(newDettagli);
  };

  const handleAggiungiRiga = () => {
    setDettagli([
      ...dettagli,
      {
        listDettaglio_dataInizioValidazione: "",
        listDettaglio_dataFineValidazione: "9999-12-31",
        listDettaglio_prezzo: "",
        listDettaglio_durata: "",
        listDettaglio_CFU: "",
        listDettaglio_tasse: "",
      },
    ]);
  };

  const handleRimuoviRiga = (index) => {
    const newDettagli = dettagli.filter((_, i) => i !== index);
    setDettagli(newDettagli);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    if (!formData.listTesta_codice || formData.listTesta_codice.trim() === "") {
      setMessage({
        type: "error",
        text: "Il campo codice non può essere vuoto.",
      });
      setLoading(false);
      return;
    }

    // Costruzione del payload convertendo in null i campi opzionali vuoti
    const payload = {
      ...formData,
      listTesta_livello:
        formData.listTesta_livello !== ""
          ? Number(formData.listTesta_livello)
          : null,
      listino_modalita_id:
        formData.listino_modalita_id !== ""
          ? Number(formData.listino_modalita_id)
          : null,
      listino_tipoCorso_id:
        formData.listino_tipoCorso_id !== ""
          ? Number(formData.listino_tipoCorso_id)
          : null,
      listino_durataLaurea_id:
        formData.listino_durataLaurea_id !== ""
          ? Number(formData.listino_durataLaurea_id)
          : null,
      listino_facolta_id:
        formData.listino_facolta_id !== ""
          ? Number(formData.listino_facolta_id)
          : null,
      listino_corsoLaurea_id:
        formData.listino_corsoLaurea_id !== ""
          ? Number(formData.listino_corsoLaurea_id)
          : null,
      nome_universita_id:
        formData.nome_universita_id !== ""
          ? Number(formData.nome_universita_id)
          : null,
      dettagli: dettagli.map((d) => ({
        listDettaglio_dataInizioValidazione:
          d.listDettaglio_dataInizioValidazione || null,
        listDettaglio_dataFineValidazione:
          d.listDettaglio_dataFineValidazione || "9999-12-31",
        listDettaglio_prezzo:
          d.listDettaglio_prezzo !== "" && d.listDettaglio_prezzo !== null
            ? parseFloat(d.listDettaglio_prezzo)
            : null,
        listDettaglio_durata:
          d.listDettaglio_durata !== "" && d.listDettaglio_durata !== null
            ? parseInt(d.listDettaglio_durata, 10)
            : null,
        listDettaglio_CFU:
          d.listDettaglio_CFU !== "" && d.listDettaglio_CFU !== null
            ? parseInt(d.listDettaglio_CFU, 10)
            : null,
        listDettaglio_tasse:
          d.listDettaglio_tasse !== "" && d.listDettaglio_tasse !== null
            ? parseFloat(d.listDettaglio_tasse)
            : null,
      })),
    };

    try {
      const response = await fetch(`${API_BASE_URL}/listini-testa/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const responseText = await response.text();
      let result = {};
      try {
        result = responseText ? JSON.parse(responseText) : {};
      } catch {}

      if (!response.ok) {
        if (response.status === 400 || response.status === 409) {
          await fetchNextCode();
          throw new Error(
            result.detail ||
              "Il codice esiste già o si è verificato un conflitto. È stato generato un nuovo codice.",
          );
        }

        throw new Error(
          result.detail
            ? typeof result.detail === "object"
              ? JSON.stringify(result.detail, null, 2)
              : result.detail
            : `Errore del server (Codice: ${response.status})`,
        );
      }

      setMessage({
        type: "success",
        text: "Prodotto salvato con successo! Reindirizzamento in corso...",
      });

      setTimeout(() => {
        navigate("/prodotti-formativi");
      }, 1000);
    } catch (err) {
      setMessage({ type: "error", text: err.message });
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-xl shadow-md border border-slate-200 mt-6 font-sans">
      <div className="flex justify-between items-center border-b border-slate-200 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-800">
            Inserimento Prodotto
          </h2>
        </div>
        <button
          type="button"
          onClick={() => navigate("/home")}
          className="px-4 py-2 border border-slate-300 text-slate-700 hover:bg-slate-100 text-sm font-medium rounded-lg transition-colors shadow-sm cursor-pointer"
        >
          ← Torna all'elenco
        </button>
      </div>

      <AlertMessage message={message} />

      <form onSubmit={handleSubmit} className="space-y-6">
        <ProdottoFormInfo
          formData={formData}
          handleChange={handleChange}
          handleGeneraCodice={handleGeneraCodice}
        />

        <ProdottoDettagliTabella
          dettagli={dettagli}
          handleDettaglioChange={handleDettaglioChange}
          handleAggiungiRiga={handleAggiungiRiga}
          handleRimuoviRiga={handleRimuoviRiga}
        />

        <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
          <button
            type="button"
            onClick={() => navigate("/prodotti-formativi")}
            className="px-5 py-2.5 border border-slate-300 text-slate-700 hover:bg-slate-100 font-medium rounded-lg text-sm transition-colors cursor-pointer"
          >
            Annulla
          </button>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2.5 rounded-lg text-sm transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
          >
            {loading ? "Salvataggio in corso..." : "Salva Prodotto"}
          </button>
        </div>
      </form>
    </div>
  );
}
