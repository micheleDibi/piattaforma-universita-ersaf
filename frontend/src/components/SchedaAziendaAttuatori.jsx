import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import {
  campo as classiCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import CampiAzienda from "./CampiAzienda.jsx";
import { VUOTO_AZIENDA } from "../config/campiAzienda.js";
import DettaglioConvenzioniUniversitarie from "./DettaglioConvenzioniUniversitarie.jsx";

const DATI_AZIENDA_VISUALIZZATI = [
  ["azienda_ragione_sociale", "Ragione sociale"],
  ["azienda_partitaIVA", "Partita IVA"],
  ["azienda_codiceFiscale", "Codice fiscale"],
  ["azienda_email", "Email"],
  ["azienda_pec", "PEC"],
  ["azienda_telefono", "Telefono"],
];

// Solo formato: 11 cifre. Il checksum ufficiale rifiuterebbe P.IVA reali ma
// malformate gia' presenti nel database (vedi azienda_partitaIVA con 10
// cifre trovata durante i test) - qui basta sapere se vale la pena
// interrogare il backend, che poi risponde 404 se non esiste davvero.
function formatoPivaValido(piva) {
  return /^\d{11}$/.test(piva);
}

// aziendaId: null se il cliente non ha ancora un'azienda associata.
// isEditMode + clienteId: se il cliente esiste gia' sul DB, l'associazione si
// salva subito con una PUT dedicata (come le percentuali). Se il cliente e'
// ancora in creazione, cercare/creare l'azienda funziona comunque (esiste
// gia' sul DB non appena trovata/creata) - solo il legame col cliente resta
// in formData.azienda_id finche' l'utente non salva l'attuatore, e viaggia
// con il resto del payload in quel momento.
export default function SchedaAziendaAttuatori({
  aziendaId,
  isEditMode,
  clienteId,
  onCambiaAziendaId,
}) {
  const [azienda, setAzienda] = useState(null);
  const [caricamento, setCaricamento] = useState(Boolean(aziendaId));
  const [errore, setErrore] = useState("");

  const [modalitaRicerca, setModalitaRicerca] = useState(!aziendaId);
  const [piva, setPiva] = useState("");
  const [erroreRicerca, setErroreRicerca] = useState("");
  const [ricercaInCorso, setRicercaInCorso] = useState(false);
  const [associazioneInCorso, setAssociazioneInCorso] = useState(false);

  const [modaleAperto, setModaleAperto] = useState(false);
  const [datiNuovaAzienda, setDatiNuovaAzienda] = useState(VUOTO_AZIENDA);
  const [erroreModale, setErroreModale] = useState("");
  const [salvataggioModale, setSalvataggioModale] = useState(false);

  // Quando cambia l'azienda lo stato si riallinea durante il render e non in
  // un effetto: stesso risultato, senza un render in piu' a cascata. Al primo
  // render i valori iniziali coincidono gia' con questi.
  const [aziendaIdMostrata, setAziendaIdMostrata] = useState(aziendaId);
  if (aziendaId !== aziendaIdMostrata) {
    setAziendaIdMostrata(aziendaId);
    setModalitaRicerca(!aziendaId);
    if (!aziendaId) {
      setAzienda(null);
      setCaricamento(false);
    } else {
      setCaricamento(true);
      setErrore("");
    }
  }

  useEffect(() => {
    if (!aziendaId) return;

    let annullato = false;

    apiFetch(`/aziende/${aziendaId}`)
      .then(async (risposta) => {
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
        return risposta.json();
      })
      .then((datiAzienda) => {
        if (annullato) return;
        setAzienda(datiAzienda);
      })
      .catch((err) => {
        if (annullato) return;
        setErrore(err.message);
      })
      .finally(() => {
        if (!annullato) setCaricamento(false);
      });

    return () => {
      annullato = true;
    };
  }, [aziendaId]);

  // Unica funzione per associare, cambiare o rimuovere: cambia solo quale id
  // viene passato (un id, un id diverso, o null).
  const associaAzienda = async (nuovoAziendaId) => {
    setAssociazioneInCorso(true);
    setErrore("");
    try {
      if (isEditMode) {
        const risposta = await apiFetch(`/clienti/${clienteId}`, {
          method: "PUT",
          body: JSON.stringify({ azienda_id: nuovoAziendaId }),
        });
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      }
      onCambiaAziendaId(nuovoAziendaId);
    } catch (err) {
      setErrore(err.message);
    } finally {
      setAssociazioneInCorso(false);
    }
  };

  const cercaAzienda = async () => {
    setErroreRicerca("");

    if (!formatoPivaValido(piva)) {
      setErroreRicerca("Inserisci 11 cifre.");
      return;
    }

    setRicercaInCorso(true);
    try {
      const risposta = await apiFetch(
        `/aziende/cerca-per-piva?partita_iva=${piva}`,
      );
      if (risposta.status === 404) {
        // Non esiste: si apre il modale di creazione con la P.IVA gia'
        // precompilata e bloccata, per non disallinearla da quella cercata.
        setDatiNuovaAzienda({ ...VUOTO_AZIENDA, azienda_partitaIVA: piva });
        setErroreModale("");
        setModaleAperto(true);
        return;
      }
      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));

      const trovata = await leggiJson(risposta);
      await associaAzienda(trovata.azienda_id);
    } catch (err) {
      setErroreRicerca(err.message);
    } finally {
      setRicercaInCorso(false);
    }
  };

  const aggiornaDatiNuovaAzienda = (evento) =>
    setDatiNuovaAzienda((prec) => ({
      ...prec,
      [evento.target.name]: evento.target.value,
    }));

  const creaAzienda = async (evento) => {
    evento.preventDefault();
    evento.stopPropagation(); // il portal non basta: gli eventi React
    // seguono l'albero dei componenti, non quello del DOM, quindi senza
    // questa riga il submit risaliva comunque fino al <form> di
    // NuovoSottoscrittore, facendone scattare handleSubmit (alert +
    // navigate verso l'elenco attuatori) subito dopo la creazione azienda.
    setErroreModale("");
    setSalvataggioModale(true);
    // ...resto invariato

    const corpo = Object.fromEntries(
      Object.entries(datiNuovaAzienda).filter(([, valore]) => valore !== ""),
    );

    try {
      const risposta = await apiFetch("/aziende/", {
        method: "POST",
        body: JSON.stringify(corpo),
      });
      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));

      const creata = await leggiJson(risposta);
      setModaleAperto(false);
      await associaAzienda(creata.azienda_id);
    } catch (err) {
      setErroreModale(err.message);
    } finally {
      setSalvataggioModale(false);
    }
  };

  const rimuoviAssociazione = () => {
    if (!window.confirm("Rimuovere l'azienda associata a questo attuatore?")) {
      return;
    }
    setPiva("");
    associaAzienda(null);
  };

  if (caricamento) {
    return (
      <IndicatoreCaricamento
        dimensione="grande"
        messaggio="Caricamento in corso..."
        centrato
      />
    );
  }

  return (
    <div className="space-y-8">
      {errore && (
        <div className="whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
          {errore}
        </div>
      )}

      {modalitaRicerca ? (
        <div className="flex flex-col gap-3 max-w-sm">
          <div className="flex flex-col">
            <label htmlFor="ricerca-piva" className={classiEtichetta()}>
              PARTITA IVA
            </label>
            <input
              id="ricerca-piva"
              type="text"
              inputMode="numeric"
              maxLength={11}
              value={piva}
              onChange={(e) => setPiva(e.target.value.replace(/\D/g, ""))}
              className={classiCampo("comodo")}
              placeholder="11 cifre"
            />
          </div>
          {erroreRicerca && (
            <p className="text-sm text-negativo">{erroreRicerca}</p>
          )}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={cercaAzienda}
              disabled={ricercaInCorso || associazioneInCorso}
              className={pulsante("primario", "grande")}
            >
              {ricercaInCorso ? "Ricerca in corso..." : "Cerca azienda"}
            </button>
            {aziendaId && (
              <button
                type="button"
                onClick={() => setModalitaRicerca(false)}
                className={pulsante("discreto", "grande")}
              >
                Annulla
              </button>
            )}
          </div>
        </div>
      ) : (
        <>
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {azienda?.azienda_ragione_sociale}
              </h3>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setModalitaRicerca(true)}
                  disabled={associazioneInCorso}
                  className={pulsante("discreto", "grande")}
                >
                  Cambia azienda
                </button>
                <button
                  type="button"
                  onClick={rimuoviAssociazione}
                  disabled={associazioneInCorso}
                  className={pulsante("discreto", "grande")}
                >
                  Rimuovi associazione
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              {DATI_AZIENDA_VISUALIZZATI.map(([nome, etichetta]) => (
                <div key={nome} className="flex flex-col">
                  <span className={classiEtichetta()}>
                    {etichetta.toUpperCase()}
                  </span>
                  <span className="text-sm">{azienda?.[nome] || "-"}</span>
                </div>
              ))}
            </div>
          </div>

          <hr className="border-bordo" />

          <DettaglioConvenzioniUniversitarie aziendaId={aziendaId} soloLettura />
        </>
      )}

      {/* Portal su document.body: il modale finisce COSI' fuori dal <form>
          esterno di NuovoSottoscrittore. Senza il portal, questo <form> era
          annidato in quello, e l'evento submit risaliva (il bubbling non si
          ferma con preventDefault) facendo scattare ANCHE handleSubmit del
          cliente - con formData.azienda_id ancora vecchio, e con
          l'alert+navigate che portava via dalla pagina a meta' flusso. */}
      {modaleAperto &&
        createPortal(
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
            <form
              onSubmit={creaAzienda}
              className={`${scheda()} w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 sm:p-8`}
            >
              <h3 className="text-lg font-semibold mb-1">
                Nessuna azienda trovata con questa Partita IVA
              </h3>
              <p className="text-sm text-testo-tenue mb-6">
                Compila i dati per crearla: verrà associata automaticamente a
                questo attuatore.
              </p>

              {erroreModale && (
                <div className="mb-6 whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
                  {erroreModale}
                </div>
              )}

              <div className="mb-8">
                <CampiAzienda
                  dati={datiNuovaAzienda}
                  onChange={aggiornaDatiNuovaAzienda}
                  disabilita={{ azienda_partitaIVA: true }}
                  nascondi={{ azienda_codice_nazionale: true }}
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={salvataggioModale}
                  className={pulsante("primario", "grande")}
                >
                  {salvataggioModale ? "Creazione..." : "Crea e associa"}
                </button>
                <button
                  type="button"
                  onClick={() => setModaleAperto(false)}
                  className={pulsante("discreto", "grande")}
                >
                  Annulla
                </button>
              </div>
            </form>
          </div>,
          document.body,
        )}
    </div>
  );
}
