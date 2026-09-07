import { useEffect, useState } from "react";
import { useParams } from "react-router";
import ModalCambiaPadre from "./ModalCambiaPadre";

export default function SchedaUtente() {
  const { id } = useParams();

  const [cliente, setCliente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [username, setUsername] = useState("");
  const [ruoloId, setRuoloId] = useState("");
  const [attivoSN, setAttivoSN] = useState(-1);
  const [saving, setSaving] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const currentId = id || 1;

    fetch(`http://localhost:8000/clienti/${currentId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Errore nel recupero dei dati dal server");
        }
        return response.json();
      })
      .then((data) => {
        setCliente(data);
        setUsername(data.utente?.utente_username || "");
        setRuoloId(data.cliente_ruolo ?? "");
        setAttivoSN(data.utente?.utente_attivoSN ?? -1);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  const handleSelectPadre = (attuatoreSelezionato) => {
    setCliente((prev) => ({
      ...prev,
      utente: {
        ...prev.utente,
        utente_padre: attuatoreSelezionato.cliente_id,
        padre: {
          cliente_id: attuatoreSelezionato.cliente_id,
          cliente_nome: attuatoreSelezionato.cliente_nome,
          cliente_cognome: attuatoreSelezionato.cliente_cognome,
        },
      },
    }));
    setIsModalOpen(false);
  };

  const handleSave = async () => {
    const currentId = id || 1;
    setSaving(true);

    const token =
      localStorage.getItem("token") || localStorage.getItem("sessione_token");
    const headers = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    try {
      const payloadCliente = {
        ...cliente,
        cliente_ruolo: Number(ruoloId),
      };

      const resCliente = await fetch(
        `http://localhost:8000/clienti/${currentId}`,
        {
          method: "PUT",
          headers,
          body: JSON.stringify(payloadCliente),
        },
      );

      if (!resCliente.ok)
        throw new Error("Errore durante l'aggiornamento del cliente");
      const clienteAggiornato = await resCliente.json();

      const utenteId = cliente.utente?.utente_id;
      if (utenteId) {
        const resUtente = await fetch(
          `http://localhost:8000/utenti/${utenteId}`,
          {
            method: "PUT",
            headers,
            body: JSON.stringify({
              ...cliente.utente,
              utente_username: username,
              utente_attivoSN: Number(attivoSN),
              utente_padre: cliente.utente?.utente_padre,
            }),
          },
        );

        if (!resUtente.ok)
          throw new Error("Errore durante l'aggiornamento dell'utente");
        const utenteAggiornato = await resUtente.json();

        clienteAggiornato.utente = utenteAggiornato;
      }

      setCliente(clienteAggiornato);
      alert("Modifiche salvate con successo!");
    } catch (err) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleLoginAutomatico = async () => {
    const utenteId = cliente?.utente?.utente_id;
    if (!utenteId) return;

    const currentToken =
      localStorage.getItem("token") || localStorage.getItem("sessione_token");
    try {
      const res = await fetch(
        `http://localhost:8000/auth/login-as/${utenteId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(currentToken
              ? { Authorization: `Bearer ${currentToken}` }
              : {}),
          },
        },
      );

      if (!res.ok) throw new Error("Errore durante il login automatico");
      const data = await res.json();

      if (data.token) {
        localStorage.removeItem("sessione_token");
        localStorage.removeItem("ruolo_codice");

        localStorage.setItem("token", data.token);
        if (data.ruolo_codice) {
          localStorage.setItem("codice_ruolo", data.ruolo_codice);
        }
        if (data.utente_id) {
          localStorage.setItem("utente_id", data.utente_id);
        }

        window.location.href = "/home";
      }
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading)
    return (
      <div className="text-center p-12 text-slate-500 text-base">
        Caricamento in corso...
      </div>
    );
  if (error)
    return (
      <div className="text-center p-12 text-red-500 text-base">
        Errore: {error}
      </div>
    );
  if (!cliente) return null;

  const padreObj = cliente.utente?.padre;
  const testoPadre = padreObj
    ? `${padreObj.cliente_nome || ""} ${padreObj.cliente_cognome || ""}`.trim()
    : cliente.utente?.utente_padre
      ? `ID: ${cliente.utente.utente_padre}`
      : "Nessuno";

  const aggiornatoDaObj = cliente.utente?.aggiornato_da;
  const testoAggiornatoDa = aggiornatoDaObj
    ? `${aggiornatoDaObj.cliente_nome || ""} ${aggiornatoDaObj.cliente_cognome || ""}`.trim()
    : cliente.utente?.utente_updated_by
      ? `ID: ${cliente.utente.utente_updated_by}`
      : "Nessuno";

  const isAttivo = Number(attivoSN) === -1;

  const ruoliAttuatori = ["1", "2", "3", "5"];
  // Mostra il login automatico solo se il ruolo è ammesso E l'utente è attivo
  const mostraLoginAutomatico =
    isAttivo && ruoliAttuatori.includes(String(ruoloId));

  return (
    <div className="max-w-[850px] mx-auto my-10 p-5 bg-white text-slate-800 font-sans">
      <h2 className="text-xl font-bold text-slate-800 mb-5 pb-2.5 border-b-2 border-slate-100">
        Dettagli Utente e Ruolo
      </h2>
      <div className="mb-8">
        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className="text-[11px] font-bold text-slate-500 mb-1.5 tracking-wide">
              UTENTE USERNAME
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="p-3 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 outline-none w-full focus:border-blue-600"
            />
          </div>

          <div className="flex flex-col justify-end">
            <div className="flex items-center h-[46px] px-3.5 text-sm text-slate-900">
              Stato Utente:{" "}
              <button
                type="button"
                onClick={() => setAttivoSN(isAttivo ? 0 : -1)}
                className={`ml-3 px-4 py-1.5 rounded-full text-xs font-bold text-white transition-colors cursor-pointer ${
                  isAttivo
                    ? "bg-green-600 hover:bg-green-700"
                    : "bg-red-600 hover:bg-red-700"
                }`}
              >
                {isAttivo ? "Attivo" : "Disattivo"}
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className="text-[11px] font-bold text-slate-500 mb-1.5 tracking-wide">
              RUOLO
            </label>
            <select
              value={ruoloId}
              onChange={(e) => setRuoloId(e.target.value)}
              className="p-3 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 outline-none focus:border-blue-600"
            >
              <option value="">Seleziona ruolo...</option>
              <option value="0">Utente</option>
              <option value="1">Aderente</option>
              <option value="2">Regionale</option>
              <option value="3">Provinciale</option>
              <option value="4">Consulente</option>
              <option value="5">Nazionale</option>
              <option value="6">Operatore</option>
            </select>
          </div>

          <div className="flex flex-col">
            <label className="text-[11px] font-bold text-slate-500 mb-1.5 tracking-wide">
              UTENTE PADRE
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                readOnly
                value={testoPadre}
                className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 outline-none flex-1"
              />
              <button
                type="button"
                onClick={() => setIsModalOpen(true)}
                className="px-3.5 bg-slate-600 text-white border-none rounded-lg text-[13px] font-bold cursor-pointer whitespace-nowrap hover:bg-slate-700"
              >
                Cambia Padre
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className="text-[11px] font-bold text-slate-500 mb-1.5 tracking-wide">
              DATA CREAZIONE
            </label>
            <input
              type="text"
              readOnly
              value={
                cliente.utente?.utente_created_at
                  ? new Date(cliente.utente.utente_created_at).toLocaleString()
                  : ""
              }
              className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 outline-none"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-[11px] font-bold text-slate-500 mb-1.5 tracking-wide">
              ULTIMO AGGIORNAMENTO
            </label>
            <input
              type="text"
              readOnly
              value={
                cliente.utente?.utente_updated_at
                  ? new Date(cliente.utente.utente_updated_at).toLocaleString()
                  : ""
              }
              className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 outline-none"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className="text-[11px] font-bold text-slate-500 mb-1.5 tracking-wide">
              AGGIORNATO DA
            </label>
            <input
              type="text"
              readOnly
              value={testoAggiornatoDa}
              className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 outline-none"
            />
          </div>
        </div>

        <div className="flex items-center gap-3 mt-2.5">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-3 bg-blue-600 text-white border-none rounded-lg text-sm font-bold cursor-pointer hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Salvataggio..." : "Salva Modifiche"}
          </button>

          {mostraLoginAutomatico && (
            <button
              onClick={handleLoginAutomatico}
              type="button"
              className="px-5 py-3 bg-emerald-600 text-white border-none rounded-lg text-sm font-bold cursor-pointer hover:bg-emerald-700"
            >
              Accedi con questo utente
            </button>
          )}
        </div>
      </div>

      <ModalCambiaPadre
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSelectPadre={handleSelectPadre}
      />
    </div>
  );
}
