import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import AlertMessage from "./ALertMessage";
import ProdottoFormInfo from "./ProdottoFormInfo";
import ProdottoDettagliTabella from "./ProdottoDettagliTabella";

// Converte una stringa numerica "italiana" (con virgola o punto) in Number.
// Restituisce null se non è un numero valido.
const parseNumeroItaliano = (valore) => {
  if (valore === "" || valore === null || valore === undefined) return null;
  const normalizzato = String(valore).replace(",", ".");
  const num = Number(normalizzato);
  return isNaN(num) ? null : num;
};

export default function InserimentoProdotto() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isModifica = Boolean(id);

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
      listDettaglio_dataInizioValidazione: new Date()
        .toISOString()
        .split("T")[0],
      listDettaglio_dataFineValidazione: "9999-12-31",
      listDettaglio_prezzo: "",
      listDettaglio_durata: "",
      listDettaglio_CFU: "",
      listDettaglio_tasse: "",
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const getIeri = (dataString) => {
    const data = new Date(dataString);
    data.setDate(data.getDate() - 1);
    return data.toISOString().split("T")[0];
  };

  const fetchNextCode = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/listini-testa/next-code",
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

    if (isModifica) {
      fetch(`http://localhost:8000/listini-testa/${id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Errore nel recupero del prodotto");
          return res.json();
        })
        .then((data) => {
          setFormData({
            listTesta_codice: data.listTesta_codice || "",
            listTesta_descrizione: data.listTesta_descrizione || "",
            listTesta_livello: data.listTesta_livello ?? "",
            listino_tipo_id: data.listino_tipo_id ?? 2,
            listino_modalita_id: data.listino_modalita_id ?? "",
            listino_tipoCorso_id: data.listino_tipoCorso_id ?? 8,
            listino_durataLaurea_id: data.listino_durataLaurea_id ?? "",
            listino_facolta_id: data.listino_facolta_id ?? "",
            listino_corsoLaurea_id: data.listino_corsoLaurea_id ?? "",
            nome_universita_id: data.nome_universita_id ?? "",
            listino_attivoSN: data.listino_attivoSN ?? -1,
            listTesta_created_by: data.listTesta_created_by || 1,
          });

          if (data.dettagli && data.dettagli.length > 0) {
            setDettagli(
              data.dettagli.map((d) => ({
                listDettaglio_dataInizioValidazione:
                  d.listDettaglio_dataInizioValidazione || "",
                listDettaglio_dataFineValidazione:
                  d.listDettaglio_dataFineValidazione || "9999-12-31",
                // Il prezzo/tasse dal DB restano numeri: la tabella li formatterà a 2 decimali in visualizzazione
                listDettaglio_prezzo: d.listDettaglio_prezzo ?? "",
                listDettaglio_durata: d.listDettaglio_durata ?? "",
                listDettaglio_CFU: d.listDettaglio_CFU ?? "",
                listDettaglio_tasse: d.listDettaglio_tasse ?? "",
              })),
            );
          }
        })
        .catch((err) => {
          setMessage({ type: "error", text: err.message });
        });
    } else {
      fetchNextCode();
    }
  }, [id, isModifica]);

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

  // Durante la digitazione: prezzo/tasse restano stringa libera (niente parseFloat qui!),
  // durata/CFU restano interi come prima.
  const handleDettaglioChange = (index, e) => {
    const { name, value } = e.target;
    const newDettagli = [...dettagli];

    let val = value;

    if (["listDettaglio_durata", "listDettaglio_CFU"].includes(name)) {
      val = value === "" ? null : parseInt(value, 10);
    } else if (["listDettaglio_prezzo", "listDettaglio_tasse"].includes(name)) {
      // Manteniamo esattamente ciò che l'utente sta scrivendo (anche con la virgola).
      // La conversione a numero avviene solo al blur, vedi handleDettaglioBlur.
      val = value;
    } else if (value === "") {
      val = null;
    }

    newDettagli[index][name] = val;
    setDettagli(newDettagli);
  };

  // Al blur di prezzo/tasse: convertiamo la stringa (con virgola o punto) in numero arrotondato a 2 decimali.
  const handleDettaglioBlur = (index, e) => {
    const { name, value } = e.target;
    if (!["listDettaglio_prezzo", "listDettaglio_tasse"].includes(name)) return;

    const numero = parseNumeroItaliano(value);
    const newDettagli = [...dettagli];
    newDettagli[index][name] =
      numero === null ? null : Number(numero.toFixed(2));
    setDettagli(newDettagli);
  };

  const handleAggiungiRiga = () => {
    const oggi = new Date().toISOString().split("T")[0];
    const dataIeri = getIeri(oggi);

    setDettagli((prevDettagli) => {
      const dettagliAggiornati = prevDettagli.map((det, index) => {
        if (index === prevDettagli.length - 1) {
          return {
            ...det,
            listDettaglio_dataFineValidazione: dataIeri,
          };
        }
        return det;
      });

      return [
        ...dettagliAggiornati,
        {
          listDettaglio_dataInizioValidazione: oggi,
          listDettaglio_dataFineValidazione: "9999-12-31",
          listDettaglio_prezzo: "",
          listDettaglio_durata: "",
          listDettaglio_CFU: "",
          listDettaglio_tasse: "",
          isNew: true,
        },
      ];
    });
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

    let dettagliDaInviare = [...dettagli];

    // VALIDAZIONE PREZZO E TASSE (uso parseNumeroItaliano per gestire eventuale virgola residua)
    for (let i = 0; i < dettagliDaInviare.length; i++) {
      const det = dettagliDaInviare[i];
      const prezzo = parseNumeroItaliano(det.listDettaglio_prezzo);
      const tasse = parseNumeroItaliano(det.listDettaglio_tasse);

      if (prezzo === null || prezzo <= 0) {
        setMessage({
          type: "error",
          text: `Errore nella riga ${i + 1}: Il prezzo è obbligatorio e deve essere maggiore di zero.`,
        });
        setLoading(false);
        return;
      }

      if (
        det.listDettaglio_tasse !== "" &&
        det.listDettaglio_tasse !== null &&
        det.listDettaglio_tasse !== undefined &&
        tasse !== null &&
        tasse <= 0
      ) {
        setMessage({
          type: "error",
          text: `Errore nella riga ${i + 1}: Le tasse non possono essere uguali a zero o negative.`,
        });
        setLoading(false);
        return;
      }
    }

    if (dettagliDaInviare.length > 1) {
      const ultimaRiga = dettagliDaInviare[dettagliDaInviare.length - 1];
      if (ultimaRiga.listDettaglio_dataInizioValidazione) {
        const indicePrecedente = dettagliDaInviare.length - 2;
        dettagliDaInviare[indicePrecedente] = {
          ...dettagliDaInviare[indicePrecedente],
          listDettaglio_dataFineValidazione: getIeri(
            ultimaRiga.listDettaglio_dataInizioValidazione,
          ),
        };
      }
    }

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
      dettagli: dettagliDaInviare.map((d) => ({
        listDettaglio_dataInizioValidazione:
          d.listDettaglio_dataInizioValidazione || null,
        listDettaglio_dataFineValidazione:
          d.listDettaglio_dataFineValidazione || "9999-12-31",
        listDettaglio_prezzo: parseNumeroItaliano(d.listDettaglio_prezzo),
        listDettaglio_durata:
          d.listDettaglio_durata !== "" && d.listDettaglio_durata !== null
            ? parseInt(d.listDettaglio_durata, 10)
            : null,
        listDettaglio_CFU:
          d.listDettaglio_CFU !== "" && d.listDettaglio_CFU !== null
            ? parseInt(d.listDettaglio_CFU, 10)
            : null,
        listDettaglio_tasse: parseNumeroItaliano(d.listDettaglio_tasse),
      })),
    };

    try {
      const url = isModifica
        ? `http://localhost:8000/listini-testa/${id}`
        : "http://localhost:8000/listini-testa/";

      const method = isModifica ? "PUT" : "POST";

      const response = await fetch(url, {
        method: method,
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
        if (
          !isModifica &&
          (response.status === 400 || response.status === 409)
        ) {
          await fetchNextCode();
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
        text: isModifica
          ? "Prodotto aggiornato con successo! Reindirizzamento in corso..."
          : "Prodotto salvato con successo! Reindirizzamento in corso...",
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
            {isModifica ? "Modifica Prodotto" : "Inserimento Prodotto"}
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
          handleDettaglioBlur={handleDettaglioBlur}
          handleAggiungiRiga={handleAggiungiRiga}
          handleRimuoviRiga={handleRimuoviRiga}
          isModifica={isModifica}
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
            {loading
              ? "Salvataggio in corso..."
              : isModifica
                ? "Aggiorna Prodotto"
                : "Salva Prodotto"}
          </button>
        </div>
      </form>
    </div>
  );
}
