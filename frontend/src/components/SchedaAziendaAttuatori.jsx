import { useEffect, useState } from "react";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";
import {
  campo as classiCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";

const CAMPI_PERCENTUALI = [
  ["universita_ecampus_lauree", "eCampus - Lauree"],
  ["universita_ecampus_master", "eCampus - Master"],
  ["universita_link_lauree", "Link - Lauree"],
  ["universita_link_master", "Link - Master"],
  ["universita_SSML_lauree", "SSML - Lauree"],
  ["universita_SSML_master", "SSML - Master"],
  ["universita_A4U_master", "A4U - Master"],
  ["universita_A4U_perfezionamenti", "A4U - Perfezionamenti"],
];

const DATI_AZIENDA_VISUALIZZATI = [
  ["azienda_ragione_sociale", "Ragione sociale"],
  ["azienda_partitaIVA", "Partita IVA"],
  ["azienda_codiceFiscale", "Codice fiscale"],
  ["azienda_email", "Email"],
  ["azienda_pec", "PEC"],
  ["azienda_telefono", "Telefono"],
];

// Anagrafica azienda mostrata in sola lettura: la modifica si fa dalla
// gestione aziende (SchedaAzienda). Qui si gestisce solo il dettaglio
// percentuali, l'unica cosa specifica di questo cliente/attuatore.
export default function SchedaAziendaAttuatori({ aziendaId }) {
  const [azienda, setAzienda] = useState(null);
  const [dettaglio, setDettaglio] = useState(null);
  const [caricamento, setCaricamento] = useState(Boolean(aziendaId));
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);

  useEffect(() => {
    if (!aziendaId) {
      setCaricamento(false);
      return;
    }

    let annullato = false;
    setCaricamento(true);
    setErrore("");

    Promise.all([
      apiFetch(`/aziende/${aziendaId}`).then(async (risposta) => {
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
        return risposta.json();
      }),
      apiFetch(`/aziende/${aziendaId}/dettagli`).then(async (risposta) => {
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
        return risposta.json();
      }),
    ])
      .then(([datiAzienda, datiDettaglio]) => {
        if (annullato) return;
        setAzienda(datiAzienda);
        setDettaglio(datiDettaglio);
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

  const aggiornaPercentuale = (evento) => {
    const { name, value } = evento.target;
    setDettaglio((prec) => ({
      ...prec,
      [name]: value === "" ? 0 : Number(value),
    }));
  };

  const salvaDettaglio = async () => {
    setErrore("");
    setSalvataggio(true);
    try {
      const corpo = Object.fromEntries(
        CAMPI_PERCENTUALI.map(([chiave]) => [chiave, dettaglio?.[chiave] ?? 0]),
      );
      const risposta = await apiFetch(`/aziende/${aziendaId}/dettagli`, {
        method: "PUT",
        body: JSON.stringify(corpo),
      });
      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      setDettaglio(await leggiJson(risposta));
    } catch (err) {
      setErrore(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  if (!aziendaId) {
    return (
      <div className="py-12 text-center text-testo-tenue">
        <p className="text-sm">Nessuna azienda collegata a questo cliente.</p>
      </div>
    );
  }

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

      <div>
        <h3 className="text-lg font-semibold mb-4">
          {azienda?.azienda_ragione_sociale}
        </h3>
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

      <div className={`${scheda()} p-6`}>
        <h4 className="text-base font-semibold mb-4">
          Dettaglio convenzioni universitarie
        </h4>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          {CAMPI_PERCENTUALI.map(([nome, etichetta]) => (
            <div key={nome} className="flex flex-col">
              <label htmlFor={nome} className={classiEtichetta()}>
                {etichetta.toUpperCase()}
              </label>
              <input
                id={nome}
                name={nome}
                type="number"
                min="0"
                max="100"
                value={dettaglio?.[nome] ?? 0}
                onChange={aggiornaPercentuale}
                className={classiCampo("comodo")}
              />
            </div>
          ))}
        </div>
        <div className="flex justify-end mt-6">
          {/* type="button": vive dentro il <form> di NuovoSottoscrittore,
              non deve inviare il form del cliente */}
          <button
            type="button"
            onClick={salvaDettaglio}
            disabled={salvataggio}
            className={pulsante("primario", "grande")}
          >
            {salvataggio ? "Salvataggio..." : "Salva percentuali"}
          </button>
        </div>
      </div>
    </div>
  );
}
