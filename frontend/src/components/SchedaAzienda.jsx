import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import StatoCaricamentoDettaglio from "./shared/StatoCaricamentoDettaglio.jsx";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { apiFetch, messaggioErrore } from "../lib/api";
import { contenutoPagina } from "../config/styles/pagina";
import { pulsante } from "../config/styles/pulsante";
import { scheda } from "../config/styles/superficie";
import { ROTTE } from "../config/routes/rotte";
import IntestazionePagina from "./shared/IntestazionePagina";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import CampiAzienda from "./CampiAzienda.jsx";
import GerarchiaAzienda from "./GerarchiaAzienda.jsx";
import DettaglioConvenzioniUniversitarie from "./DettaglioConvenzioniUniversitarie.jsx";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import { TriangleAlert } from "../config/icone.js";
import { SEZIONI_AZIENDA, VUOTO_AZIENDA } from "../config/campiAzienda.js";

export default function SchedaAzienda() {
  const { aziendaId: id } = useParams();
  const navigate = useNavigate();
  const { ritorno } = useNavigazioneElenco(ROTTE.aziende);
  const inModifica = Boolean(id);

  const [erroreLettura, setErroreLettura] = useState(null);
  const [dati, setDati] = useState(VUOTO_AZIENDA);
  const [anomalie, setAnomalie] = useState([]);
  const [caricamento, setCaricamento] = useState(inModifica);
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);

  useEffect(() => {
    if (!inModifica) return;

    let annullato = false;
    apiFetch(`/aziende/${id}`)
      .then(async (risposta) => {
        if (!risposta.ok)
          throw Object.assign(new Error(await messaggioErrore(risposta)), {
            status: risposta.status,
          });
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
        setAnomalie(azienda.anomalie ?? []);
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
  if (erroreLettura)
    return (
      <StatoCaricamentoDettaglio errore={erroreLettura} ritorno={ritorno} />
    );

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
        descrizione={
          inModifica ? dati.azienda_ragione_sociale || undefined : undefined
        }
        indietro={{ rotta: ritorno, etichetta: "Aziende" }}
      />
      <form onSubmit={invia} className="flex flex-col gap-5">
        {anomalie.length > 0 && (
          <div className="flex items-start gap-2 rounded-controllo border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800">
            <TriangleAlert
              className="size-icona shrink-0 text-amber-500"
              aria-hidden="true"
            />
            <ul className={anomalie.length > 1 ? "list-disc pl-4" : undefined}>
              {anomalie.map((testo) => (
                <li key={testo}>{testo}</li>
              ))}
            </ul>
          </div>
        )}
        {errore && (
          <div className="whitespace-pre-line rounded-controllo border border-negativo/30 bg-negativo-tenue p-4 text-sm text-negativo">
            {errore}
          </div>
        )}

        <div className={scheda()}>
          {SEZIONI_AZIENDA.map(({ titolo, descrizione, campi }) => (
            <SezioneModulo
              key={titolo}
              titolo={titolo}
              descrizione={descrizione}
            >
              <CampiAzienda
                dati={dati}
                onChange={aggiorna}
                disabilita={{ azienda_codice_nazionale: true }}
                gruppo={campi}
              />
            </SezioneModulo>
          ))}
          {inModifica && (
            <SezioneModulo
              titolo="Gerarchia"
              descrizione="Azienda a cui questa è collegata."
              griglia={false}
            >
              <GerarchiaAzienda aziendaId={id} />
            </SezioneModulo>
          )}
          {inModifica && (
            <SezioneModulo
              titolo="Convenzioni universitarie"
              descrizione="Percentuali applicate per ateneo e tipologia di corso."
              griglia={false}
            >
              <DettaglioConvenzioniUniversitarie aziendaId={id} inSezione />
            </SezioneModulo>
          )}
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate(ritorno)}
            className={pulsante("discreto", "grande")}
          >
            Annulla
          </button>
          <button
            type="submit"
            disabled={salvataggio}
            className={pulsante("primario", "grande")}
          >
            {salvataggio
              ? "Salvataggio..."
              : inModifica
                ? "Salva modifiche"
                : "Salva"}
          </button>
        </div>
      </form>
    </div>
  );
}
