import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import StatoCaricamentoDettaglio from "./shared/StatoCaricamentoDettaglio.jsx";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { apiFetch, messaggioErrore } from "../lib/api";
// Alias: in questo file `campo` ed `etichetta` sono gia' un helper di rendering
// e un parametro destrutturato, quindi le varianti arrivano con altro nome.
import {
  campo as classiCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";
import { contenutoPagina } from "../config/styles/pagina";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import { ROTTE } from "../config/routes/rotte";
import IntestazionePagina from "./shared/IntestazionePagina";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";

// obbligatori nel database (NOT NULL senza un default utile)
const OBBLIGATORI = [
  ["azienda_ragione_sociale", "Ragione sociale"],
  ["azienda_partitaIVA", "Partita IVA"],
  ["azienda_via", "Via"],
  ["azienda_citta", "Città"],
  ["azienda_CAP", "CAP"],
  ["azienda_provincia", "Provincia"],
];

const FACOLTATIVI = [
  ["azienda_civico", "Civico"],
  ["azienda_codiceFiscale", "Codice fiscale"],
  ["azienda_fatturazioneSDI", "Codice SDI"],
  ["azienda_email", "Email"],
  ["azienda_pec", "PEC"],
  ["azienda_telefono", "Telefono"],
  ["azienda_sitoWeb", "Sito web"],
  ["azienda_iban", "IBAN"],
  ["azienda_codice_bic", "Codice BIC"],
  ["azienda_codice_nazionale", "Codice nazionale"],
];

const VUOTO = Object.fromEntries(
  [...OBBLIGATORI, ...FACOLTATIVI].map(([campo]) => [campo, ""]),
);

export default function SchedaAzienda() {
  const { aziendaId: id } = useParams();
  const navigate = useNavigate();
  const { ritorno } = useNavigazioneElenco(ROTTE.aziende);
  const inModifica = Boolean(id);

  const [erroreLettura, setErroreLettura] = useState(null);
  const [dati, setDati] = useState(VUOTO);
  const [caricamento, setCaricamento] = useState(inModifica);
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);

  useEffect(() => {
    if (!inModifica) return;

    let annullato = false;
    apiFetch(`/aziende/${id}`)
      .then(async (risposta) => {
        if (!risposta.ok) throw Object.assign(new Error(await messaggioErrore(risposta)), { status: risposta.status });
        return risposta.json();
      })
      .then((azienda) => {
        if (annullato) return;
        // Le colonne nullable arrivano null: negli input serve la stringa
        // vuota, altrimenti React passa da controllato a non controllato.
        setDati({
          ...VUOTO,
          ...Object.fromEntries(
            Object.entries(azienda).map(([k, v]) => [k, v ?? ""]),
          ),
        });
        setCaricamento(false);
      })
      .catch((err) => {
        if (annullato) return;
        setErroreLettura(err);
        setCaricamento(false);
      });

    return () => {
      annullato = true;
    };
  }, [id, inModifica]);

  const aggiorna = (evento) =>
    setDati((prec) => ({ ...prec, [evento.target.name]: evento.target.value }));

  const invia = async (evento) => {
    evento.preventDefault();
    setErrore("");
    setSalvataggio(true);

    // In modifica si manda solo cio' che e' valorizzato: il PUT usa
    // exclude_unset, quindi i campi omessi restano quelli che sono.
    const corpo = Object.fromEntries(
      Object.entries(dati).filter(([, valore]) => valore !== ""),
    );

    try {
      const risposta = await apiFetch(
        inModifica ? `/aziende/${id}` : "/aziende/",
        { method: inModifica ? "PUT" : "POST", body: JSON.stringify(corpo) },
      );
      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      navigate(ritorno);
    } catch (err) {
      setErrore(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  if (erroreLettura?.status === 404) return <PaginaNonTrovata />;
  if (erroreLettura) return <StatoCaricamentoDettaglio errore={erroreLettura} ritorno={ritorno} />;

  if (caricamento)
    return (
      <IndicatoreCaricamento
        dimensione="grande"
        messaggio="Caricamento in corso..."
        centrato
      />
    );

  const campo = ([nome, etichetta], obbligatorio) => (
    <div key={nome} className="flex flex-col">
      <label
        htmlFor={nome}
        className={classiEtichetta()}
      >
        {etichetta.toUpperCase()}
        {obbligatorio && <span className="text-negativo"> *</span>}
      </label>
      <input
        id={nome}
        name={nome}
        type="text"
        required={obbligatorio}
        value={dati[nome]}
        onChange={aggiorna}
        className={classiCampo("comodo")}
      />
    </div>
  );

  return (
    <div className={contenutoPagina("modulo")}>
      <IntestazionePagina
        titolo={inModifica ? "Modifica azienda" : "Nuova azienda"}
        indietro={{ rotta: ritorno, etichetta: "Aziende" }}
      />
      <form onSubmit={invia} className={`${scheda()} p-6 sm:p-8`}>
        {errore && (
          <div className="mb-6 whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
            {errore}
          </div>
        )}

        <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2">
          {OBBLIGATORI.map((c) => campo(c, true))}
          {FACOLTATIVI.map((c) => campo(c, false))}
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={salvataggio}
            className={pulsante("primario", "grande")}
          >
            {salvataggio ? "Salvataggio..." : "Salva"}
          </button>
          <button
            type="button"
            onClick={() => navigate(ritorno)}
            className={pulsante("discreto", "grande")}
          >
            Annulla
          </button>
        </div>
      </form>
    </div>
  );
}
