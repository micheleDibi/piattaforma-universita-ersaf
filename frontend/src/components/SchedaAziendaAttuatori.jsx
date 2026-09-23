import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import { campo as classiCampo } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { barraAzioniModulo } from "../config/styles/superficie";
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import CampoModulo from "./shared/CampoModulo.jsx";
import AlertMessage from "./AlertMessage.jsx";
import CampiAzienda from "./CampiAzienda.jsx";
import { VUOTO_AZIENDA } from "../config/campiAzienda.js";
import DettaglioConvenzioniUniversitarie from "./DettaglioConvenzioniUniversitarie.jsx";

const TESTI = TESTI_AZIENDA.attuatore;

// Dati dell'azienda associata mostrati sotto la ragione sociale.
const DATI_AZIENDA_VISUALIZZATI = [
  "azienda_ragione_sociale",
  "azienda_partitaIVA",
  "azienda_codiceFiscale",
  "azienda_email",
  "azienda_pec",
  "azienda_telefono",
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
      setErroreRicerca(TESTI.pivaIncompleta);
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
    if (!window.confirm(TESTI.confermaRimozione)) {
      return;
    }
    setPiva("");
    associaAzienda(null);
  };

  if (caricamento) {
    return (
      <IndicatoreCaricamento
        dimensione="grande"
        messaggio={TESTI_AZIENDA.caricamento}
        centrato
      />
    );
  }

  return (
    <div className={stili.attuatore}>
      {errore && (
        <AlertMessage message={{ type: "error", text: errore }} separato={false} />
      )}

      {modalitaRicerca ? (
        <div className={stili.ricerca}>
          <CampoModulo
            per="ricerca-piva"
            etichetta={TESTI.etichettaRicerca}
            nota={erroreRicerca}
            tonoNota="errore"
          >
            <input
              id="ricerca-piva"
              type="text"
              inputMode="numeric"
              maxLength={11}
              value={piva}
              onChange={(e) => setPiva(e.target.value.replace(/\D/g, ""))}
              aria-invalid={Boolean(erroreRicerca) || undefined}
              aria-describedby={erroreRicerca ? "ricerca-piva-nota" : undefined}
              className={classiCampo("comodo", { errore: Boolean(erroreRicerca) })}
              placeholder={TESTI.segnapostoRicerca}
            />
          </CampoModulo>
          <div className={stili.azioniRicerca}>
            <button
              type="button"
              onClick={cercaAzienda}
              disabled={ricercaInCorso || associazioneInCorso}
              className={pulsante("primario", "grande")}
            >
              {ricercaInCorso ? TESTI.ricercaInCorso : TESTI.cerca}
            </button>
            {aziendaId && (
              <button
                type="button"
                onClick={() => setModalitaRicerca(false)}
                className={pulsante("testuale", "grande")}
              >
                {TESTI_AZIENDA.annulla}
              </button>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-6">
            <div className={stili.testataAttuatore}>
              <h3 className={stili.titoloAttuatore}>
                {azienda?.azienda_ragione_sociale}
              </h3>
              <div className={stili.azioniAttuatore}>
                <button
                  type="button"
                  onClick={() => setModalitaRicerca(true)}
                  disabled={associazioneInCorso}
                  className={pulsante("contorno", "medio")}
                >
                  {TESTI.cambia}
                </button>
                <button
                  type="button"
                  onClick={rimuoviAssociazione}
                  disabled={associazioneInCorso}
                  className={pulsante("testuale", "medio")}
                >
                  {TESTI.rimuovi}
                </button>
              </div>
            </div>
            <dl className={stili.datiAttuatore}>
              {DATI_AZIENDA_VISUALIZZATI.map((nome) => (
                <div key={nome} className="flex min-w-0 flex-col">
                  <dt className={stili.etichettaDato}>
                    {TESTI_AZIENDA.campi[nome]}
                  </dt>
                  <dd className={stili.valoreDato}>
                    {azienda?.[nome] || TESTI_AZIENDA.trattino}
                  </dd>
                </div>
              ))}
            </dl>
          </div>

          <hr className={stili.separatore} />

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
          <div className={stili.velo}>
            <form
              onSubmit={creaAzienda}
              aria-labelledby="creazione-azienda-titolo"
              className={stili.finestra}
            >
              <h3 id="creazione-azienda-titolo" className={stili.titoloFinestra}>
                {TESTI.titoloCreazione}
              </h3>
              <p className={stili.descrizioneFinestra}>
                {TESTI.descrizioneCreazione}
              </p>

              <div className={stili.corpoFinestra}>
                {erroreModale && (
                  <AlertMessage
                    message={{ type: "error", text: erroreModale }}
                    separato={false}
                  />
                )}
                <CampiAzienda
                  dati={datiNuovaAzienda}
                  onChange={aggiornaDatiNuovaAzienda}
                  soloLettura={{ azienda_partitaIVA: true }}
                  nascondi={{ azienda_codice_nazionale: true }}
                />
              </div>

              <div className={barraAzioniModulo("pagina")}>
                <button
                  type="button"
                  onClick={() => setModaleAperto(false)}
                  className={pulsante("testuale", "grande")}
                >
                  {TESTI_AZIENDA.annulla}
                </button>
                <button
                  type="submit"
                  disabled={salvataggioModale}
                  className={pulsante("primario", "grande")}
                >
                  {salvataggioModale ? TESTI.creazione : TESTI.crea}
                </button>
              </div>
            </form>
          </div>,
          document.body,
        )}
    </div>
  );
}
