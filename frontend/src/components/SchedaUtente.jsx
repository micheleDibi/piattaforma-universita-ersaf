import { ROTTA_INIZIALE } from "../config/routes/percorsi.js";
import { SEGNAPOSTI_SELEZIONE } from "../config/testi/selezioni.js";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import ModalCambiaPadre from "./ModalCambiaPadre";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { salvaSessione } from "../lib/sessione";
import { campo, etichetta } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { colonnaCampo, pillolaStato, STILI_ANAGRAFICA as stili } from "../config/styles/anagrafica.js";
import { TESTI_ANAGRAFICA, TESTI_UTENTE as testi } from "../config/testi/anagrafica.js";
import { dataCronologia, nomeUtente, statoAccount } from "../lib/schedaAnagrafica.js";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import AlertMessage from "./AlertMessage.jsx";

export default function SchedaUtente() {
  const { clienteId: id } = useParams();

  const [cliente, setCliente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [username, setUsername] = useState("");
  const [ruoloId, setRuoloId] = useState("");
  const [attivoSN, setAttivoSN] = useState(-1);
  const [saving, setSaving] = useState(false);
  const [avviso, setAvviso] = useState(null);

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
      setAvviso({ type: "error", text: testi.padreSenzaUtente });
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
    setAvviso(null);
    // Number("") vale 0, cioe' il ruolo "Utente", che non accede: senza questa
    // guardia bastava salvare con la tendina non selezionata per chiudere
    // fuori l'utente.
    if (ruoloId === "" || ruoloId === null) {
      setAvviso({ type: "error", text: testi.ruoloMancante });
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
      setAvviso({ type: "success", text: testi.salvataggioRiuscito });
    } catch (err) {
      setAvviso({ type: "error", text: err.message });
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

      salvaSessione(dati ?? {});
      window.location.href = ROTTA_INIZIALE;
    } catch (err) {
      setAvviso({ type: "error", text: err.message });
    }
  };

  if (!id) return <div className={stili.vuoto}>{testi.nessunUtente}</div>;
  if (loading)
    return (
      <IndicatoreCaricamento
        dimensione="grande"
        messaggio={testi.caricamento}
        centrato
      />
    );
  if (error) return <div className={stili.errore}>{testi.errore(error)}</div>;
  if (!cliente) return null;

  // `padre` e `aggiornato_da` sono utenti, non clienti: vedi nomeUtente().
  const testoPadre = nomeUtente(
    cliente.utente?.padre,
    cliente.utente?.utente_padre,
  );
  const testoAggiornatoDa = nomeUtente(
    cliente.utente?.aggiornato_da,
    cliente.utente?.utente_updated_by,
  );

  const isAttivo = statoAccount(attivoSN)?.attivo ?? false;
  const formattaData = (valore) => dataCronologia(valore) || testi.vuoto;

  const ruoliAttuatori = ["1", "2", "3", "5"];
  // Mostra il login automatico solo se il ruolo è ammesso E l'utente è attivo
  const mostraLoginAutomatico =
    isAttivo && ruoliAttuatori.includes(String(ruoloId));

  return (
    <div>
      {/* Prima delle sezioni: il <dialog> resta nel DOM anche chiuso, e in
          fondo toglierebbe all'ultima sezione il ruolo di ultima figlia
          (bordo inferiore doppio sopra la barra delle azioni). */}
      <ModalCambiaPadre
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSelectPadre={handleSelectPadre}
      />
      {avviso && (
        <div className={stili.avvisoUtente}>
          <AlertMessage message={avviso} separato={false} />
        </div>
      )}
      <SezioneModulo titolo={testi.account.titolo} descrizione={testi.account.descrizione}>
        <CampoModulo per="utente-username" etichetta={testi.username} colonne={3}>
          <input
            id="utente-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className={campo("comodo")}
          />
        </CampoModulo>

        <div className={colonnaCampo(3)}>
          <span className={etichetta()}>{testi.stato}</span>
          <div className={stili.cellaStato}>
            <button
              type="button"
              onClick={() => setAttivoSN(isAttivo ? 0 : -1)}
              aria-pressed={isAttivo}
              title={testi.cambiaStato}
              className={pillolaStato(isAttivo)}
            >
              {TESTI_ANAGRAFICA.stato(isAttivo)}
            </button>
          </div>
        </div>

        <CampoModulo per="utente-ruolo" etichetta={testi.ruolo} colonne={3}>
          <select
            id="utente-ruolo"
            value={ruoloId}
            onChange={(e) => setRuoloId(e.target.value)}
            className={campo("comodo")}
          >
            <option value="" data-segnaposto>
              {SEGNAPOSTI_SELEZIONE.ruolo}
            </option>
            {testi.ruoli.map(([valore, etichettaRuolo]) => (
              <option key={valore} value={valore}>{etichettaRuolo}</option>
            ))}
          </select>
        </CampoModulo>

        <div className={colonnaCampo(3)}>
          <span className={etichetta()}>{testi.padre}</span>
          <div className={stili.riquadroPadre}>
            <span className={stili.nomePadre}>{testoPadre || testi.vuoto}</span>
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className={`${pulsante("contorno", "minimo")} shrink-0`}
            >
              {testi.cambiaPadre}
            </button>
          </div>
        </div>

        <div className={stili.azioniUtente}>
          {mostraLoginAutomatico && (
            <button
              onClick={handleLoginAutomatico}
              type="button"
              className={pulsante("contorno")}
            >
              {testi.accedi}
            </button>
          )}
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className={pulsante("contorno")}
          >
            {saving ? testi.salvataggio : testi.salva}
          </button>
        </div>
      </SezioneModulo>

      <SezioneModulo titolo={testi.cronologia} griglia={false}>
        <dl className={stili.cronologia}>
          {[
            [testi.creato, formattaData(cliente.utente?.utente_created_at)],
            [testi.aggiornato, formattaData(cliente.utente?.utente_updated_at)],
            [testi.aggiornatoDa, testoAggiornatoDa || testi.vuoto],
          ].map(([voce, valore]) => (
            <div key={voce}>
              <dt className={etichetta("secondaria")}>{voce}</dt>
              <dd className={stili.valoreCronologia}>{valore}</dd>
            </div>
          ))}
        </dl>
      </SezioneModulo>
    </div>
  );
}
