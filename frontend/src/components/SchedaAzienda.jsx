import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { apiFetch, messaggioErrore } from "../lib/api";
import { contenutoPagina } from "../config/styles/pagina";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import { ROTTE } from "../config/routes/rotte";
import IntestazionePagina from "./shared/IntestazionePagina";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import CampiAzienda, { VUOTO_AZIENDA } from "./CampiAzienda.jsx";

export default function SchedaAzienda() {
  const { id } = useParams();
  const navigate = useNavigate();
  const inModifica = Boolean(id);

  const [dati, setDati] = useState(VUOTO_AZIENDA);
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
        setDati({
          ...VUOTO_AZIENDA,
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

    const corpo = Object.fromEntries(
      Object.entries(dati).filter(([, valore]) => valore !== ""),
    );

    try {
      const risposta = await apiFetch(
        inModifica ? `/aziende/${id}` : "/aziende/",
        { method: inModifica ? "PUT" : "POST", body: JSON.stringify(corpo) },
      );
      if (!risposta.ok) throw new Error(await messaggioErrore(risposta));
      navigate(ROTTE.aziende);
    } catch (err) {
      setErrore(err.message);
    } finally {
      setSalvataggio(false);
    }
  };

  if (caricamento)
    return (
      <IndicatoreCaricamento
        dimensione="grande"
        messaggio="Caricamento in corso..."
        centrato
      />
    );

  return (
    <div className={contenutoPagina("modulo")}>
      <IntestazionePagina
        titolo={inModifica ? "Modifica azienda" : "Nuova azienda"}
        indietro={{ rotta: ROTTE.aziende, etichetta: "Aziende" }}
      />
      <form onSubmit={invia} className={`${scheda()} p-6 sm:p-8`}>
        {errore && (
          <div className="mb-6 whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
            {errore}
          </div>
        )}

        <div className="mb-8">
          <CampiAzienda dati={dati} onChange={aggiorna} />
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
            onClick={() => navigate(ROTTE.aziende)}
            className={pulsante("discreto", "grande")}
          >
            Annulla
          </button>
        </div>
      </form>
    </div>
  );
}
