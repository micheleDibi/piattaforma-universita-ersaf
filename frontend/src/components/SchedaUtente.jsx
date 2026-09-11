import { useEffect, useState } from "react";
import { useParams } from "react-router";
import ModalCambiaPadre from "./ModalCambiaPadre";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { salvaSessione } from "../lib/sessione";
import { campo, etichetta } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { titoloSezione } from "../config/styles/superficie";

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
    // Nessun ripiego a 1. Con `id || 1`, aprire la scheda senza :id mostrava e
    // faceva sovrascrivere username, ruolo e stato attivo del cliente numero 1.
    // Il caso "nessun id" si risolve in render, non con una setState
    // nell'effetto: sarebbe un render a cascata.
    if (!id) return;

    let annullato = false;
    apiFetch(`/clienti/${id}`)
      .then(async (risposta) => {
        if (!risposta.ok) {
          throw new Error(await messaggioErrore(risposta));
        }
        return risposta.json();
      })
      .then((data) => {
        if (annullato) return;
        setCliente(data);
        setUsername(data.utente?.utente_username || "");
        setRuoloId(data.cliente_ruolo ?? "");
        setAttivoSN(data.utente?.utente_attivoSN ?? -1);
        setLoading(false);
      })
      .catch((err) => {
        if (annullato) return;
        setError(err.message);
        setLoading(false);
      });

    // StrictMode monta due volte in sviluppo: senza questo, la risposta del
    // primo montaggio poteva sovrascrivere quella del secondo.
    return () => {
      annullato = true;
    };
  }, [id]);

  const handleSelectPadre = (attuatoreSelezionato) => {
    // utente_padre contiene un utente_id, non un cliente_id: la ForeignKey del
    // database punta a utenti(utente_id). Qui si scriveva il cliente_id, e i
    // due coincidono solo in 377 clienti su 3.906.
    const padreUtenteId = attuatoreSelezionato.utente?.utente_id;
    if (!padreUtenteId) {
      alert("L'attuatore selezionato non ha un utente associato.");
      return;
    }

    setCliente((prev) => ({
      ...prev,
      utente: {
        ...prev.utente,
        utente_padre: padreUtenteId,
        padre: {
          utente_id: padreUtenteId,
          utente_username: attuatoreSelezionato.utente?.utente_username || "",
          cliente: {
            cliente_id: attuatoreSelezionato.cliente_id,
            cliente_nome: attuatoreSelezionato.cliente_nome,
            cliente_cognome: attuatoreSelezionato.cliente_cognome,
          },
        },
      },
    }));
    setIsModalOpen(false);
  };

  const handleSave = async () => {
    if (!id) return;
    // Number("") vale 0, cioe' il ruolo "Utente", che non accede: senza questa
    // guardia bastava salvare con la tendina non selezionata per chiudere
    // fuori l'utente.
    if (ruoloId === "" || ruoloId === null) {
      alert("Seleziona un ruolo prima di salvare.");
      return;
    }

    setSaving(true);
    try {
      // Si mandano SOLO i campi che questa scheda modifica. Prima partiva
      // l'intero oggetto cliente, relazioni annidate comprese.
      const risposteCliente = await apiFetch(`/clienti/${id}`, {
        method: "PUT",
        body: JSON.stringify({ cliente_ruolo: Number(ruoloId) }),
      });
      if (!risposteCliente.ok) {
        throw new Error(await messaggioErrore(risposteCliente));
      }
      const clienteAggiornato = await risposteCliente.json();

      const utenteId = cliente.utente?.utente_id;
      if (utenteId) {
        const rispostaUtente = await apiFetch(`/utenti/${utenteId}`, {
          method: "PUT",
          body: JSON.stringify({
            utente_username: username,
            utente_attivoSN: Number(attivoSN),
            utente_padre: cliente.utente?.utente_padre ?? null,
          }),
        });
        if (!rispostaUtente.ok) {
          throw new Error(await messaggioErrore(rispostaUtente));
        }
        clienteAggiornato.utente = await rispostaUtente.json();
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

    try {
      const risposta = await apiFetch(`/auth/login-as/${utenteId}`, {
        method: "POST",
        // Un 401 qui significa che la MIA sessione e' scaduta: va gestito come
        // altrove, tornando al login.
      });
      if (!risposta.ok) {
        throw new Error(await messaggioErrore(risposta));
      }
      const dati = await leggiJson(risposta);

      if (dati?.token) {
        // Unico punto in cui si scrive la sessione. Prima si cancellavano le
        // chiavi giuste (sessione_token, ruolo_codice) e se ne scrivevano di
        // sbagliate (token, codice_ruolo, col nome invertito): apiFetch non
        // trovava piu' il token e l'impersonificazione non funzionava mai.
        salvaSessione({
          token: dati.token,
          utenteId: dati.utente_id,
          ruoloCodice: dati.ruolo_codice,
        });
        window.location.href = "/home";
      }
    } catch (err) {
      alert(err.message);
    }
  };

  if (!id)
    return (
      <div className="text-center p-12 text-testo-tenue text-base">
        Nessun utente selezionato.
      </div>
    );
  if (loading)
    return (
      <div className="text-center p-12 text-testo-tenue text-base">
        Caricamento in corso...
      </div>
    );
  if (error)
    return (
      <div className="text-center p-12 text-negativo text-base">
        Errore: {error}
      </div>
    );
  if (!cliente) return null;

  // `padre` e `aggiornato_da` sono utenti, non clienti: il nome della persona
  // sta nel cliente annidato, e lo username resta come ripiego per gli 869
  // utenti che una riga clienti non ce l'hanno.
  const nomeUtente = (utente, idNumerico) => {
    if (!utente) return idNumerico ? `ID: ${idNumerico}` : "Nessuno";
    const persona = `${utente.cliente?.cliente_nome || ""} ${
      utente.cliente?.cliente_cognome || ""
    }`.trim();
    return persona || utente.utente_username || `ID: ${utente.utente_id}`;
  };

  const testoPadre = nomeUtente(
    cliente.utente?.padre,
    cliente.utente?.utente_padre,
  );
  const testoAggiornatoDa = nomeUtente(
    cliente.utente?.aggiornato_da,
    cliente.utente?.utente_updated_by,
  );

  const isAttivo = Number(attivoSN) === -1;

  const ruoliAttuatori = ["1", "2", "3", "5"];
  // Mostra il login automatico solo se il ruolo è ammesso E l'utente è attivo
  const mostraLoginAutomatico =
    isAttivo && ruoliAttuatori.includes(String(ruoloId));

  return (
    <div className="max-w-[850px] mx-auto my-10 p-5 bg-superficie text-testo font-sans">
      <h2 className={titoloSezione("separato")}>
        Dettagli Utente e Ruolo
      </h2>
      <div className="mb-8">
        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className={etichetta()}>
              UTENTE USERNAME
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={campo("comodo")}
            />
          </div>

          <div className="flex flex-col justify-end">
            <div className="flex items-center h-[46px] px-3.5 text-sm text-testo-forte">
              Stato Utente:{" "}
              <button
                type="button"
                onClick={() => setAttivoSN(isAttivo ? 0 : -1)}
                className={`ml-3 px-4 py-1.5 rounded-full text-xs font-bold text-su-primario transition-colors cursor-pointer ${
                  isAttivo
                    ? "bg-positivo hover:opacity-90"
                    : "bg-negativo hover:opacity-90"
                }`}
              >
                {isAttivo ? "Attivo" : "Disattivo"}
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className={etichetta()}>
              RUOLO
            </label>
            <select
              value={ruoloId}
              onChange={(e) => setRuoloId(e.target.value)}
              className={campo("comodo")}
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
            <label className={etichetta()}>
              UTENTE PADRE
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                readOnly
                value={testoPadre}
                className={`${campo("comodo")} flex-1`}
              />
              <button
                type="button"
                onClick={() => setIsModalOpen(true)}
                className={`${pulsante("secondario")} whitespace-nowrap`}
              >
                Cambia Padre
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className={etichetta()}>
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
              className={campo("comodo")}
            />
          </div>

          <div className="flex flex-col">
            <label className={etichetta()}>
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
              className={campo("comodo")}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5 mb-4">
          <div className="flex flex-col">
            <label className={etichetta()}>
              AGGIORNATO DA
            </label>
            <input
              type="text"
              readOnly
              value={testoAggiornatoDa}
              className={campo("comodo")}
            />
          </div>
        </div>

        <div className="flex items-center gap-3 mt-2.5">
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className={pulsante("primario", "grande")}
          >
            {saving ? "Salvataggio..." : "Salva Modifiche"}
          </button>

          {mostraLoginAutomatico && (
            <button
              onClick={handleLoginAutomatico}
              type="button"
              className="px-5 py-3 bg-positivo text-su-primario border-none rounded-controllo text-sm font-bold cursor-pointer hover:opacity-90"
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
