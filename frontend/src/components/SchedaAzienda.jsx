import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { apiFetch, messaggioErrore } from "../lib/api";

// I due bottoni di ElencoAziende navigavano a /nuova-azienda e
// /modifica-azienda/:id, che non erano registrate in App.jsx: cadevano nel
// catch-all e l'utente finiva sulla schermata di login senza spiegazione. Il
// backend le rotte le aveva gia'; mancava solo questa pagina.

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
  const { id } = useParams();
  const navigate = useNavigate();
  const inModifica = Boolean(id);

  const [dati, setDati] = useState(VUOTO);
  const [caricamento, setCaricamento] = useState(inModifica);
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);

  useEffect(() => {
    if (!inModifica) return;

    let annullato = false;
    apiFetch(`/aziende/${id}`)
      .then(async (risposta) => {
        if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
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
        setErrore(err.message);
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
      navigate("/aziende");
    } catch (err) {
      setErrore(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  if (caricamento)
    return (
      <div className="p-12 text-center text-slate-500">
        Caricamento in corso...
      </div>
    );

  const campo = ([nome, etichetta], obbligatorio) => (
    <div key={nome} className="flex flex-col">
      <label
        htmlFor={nome}
        className="mb-1.5 text-[11px] font-bold tracking-wide text-slate-500"
      >
        {etichetta.toUpperCase()}
        {obbligatorio && <span className="text-red-500"> *</span>}
      </label>
      <input
        id={nome}
        name={nome}
        type="text"
        required={obbligatorio}
        value={dati[nome]}
        onChange={aggiorna}
        className="rounded-lg border border-slate-300 bg-white p-3 text-sm text-slate-900 outline-none focus:border-blue-600"
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-10">
      <form
        onSubmit={invia}
        className="mx-auto max-w-4xl rounded-3xl border border-slate-100 bg-white p-8 shadow-sm"
      >
        <h2 className="mb-6 border-b-2 border-slate-100 pb-2.5 text-xl font-bold text-slate-800">
          {inModifica ? "Modifica azienda" : "Nuova azienda"}
        </h2>

        {errore && (
          <div className="mb-6 whitespace-pre-line rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
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
            className="cursor-pointer rounded-lg bg-blue-600 px-5 py-3 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {salvataggio ? "Salvataggio..." : "Salva"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/aziende")}
            className="cursor-pointer rounded-lg px-5 py-3 text-sm font-medium text-slate-500 hover:text-slate-800"
          >
            Annulla
          </button>
        </div>
      </form>
    </div>
  );
}
