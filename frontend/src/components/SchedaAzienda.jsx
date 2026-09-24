import PaginaNonTrovata from "./PaginaNonTrovata.jsx";
import StatoCaricamentoDettaglio from "./shared/StatoCaricamentoDettaglio.jsx";
import useNavigazioneElenco from "../hooks/useNavigazioneElenco.js";
import usePadreAzienda from "../hooks/usePadreAzienda.js";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { apiFetch, messaggioErrore } from "../lib/api";
import { sottotitoloAzienda } from "../lib/schedaAzienda.js";
import { contenutoPagina } from "../config/styles/pagina";
import { pulsante } from "../config/styles/pulsante";
import { barraAzioniModulo } from "../config/styles/superficie";
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { ROTTE } from "../config/routes/rotte";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import IntestazionePagina from "./shared/IntestazionePagina";
import IndicatoreCaricamento from "./shared/IndicatoreCaricamento.jsx";
import CampiAzienda from "./CampiAzienda.jsx";
import GerarchiaAzienda from "./GerarchiaAzienda.jsx";
import DettaglioConvenzioniUniversitarie from "./DettaglioConvenzioniUniversitarie.jsx";
import SezioneModulo from "./shared/SezioneModulo.jsx";
import AlertMessage from "./AlertMessage.jsx";
import { SEZIONI_AZIENDA, VUOTO_AZIENDA } from "../config/campiAzienda.js";

const SEZIONI = TESTI_AZIENDA.sezioni;

export default function SchedaAzienda() {
  const { aziendaId: id } = useParams();
  const navigate = useNavigate();
  const { ritorno } = useNavigazioneElenco(ROTTE.aziende);
  const inModifica = Boolean(id);

  const [erroreLettura, setErroreLettura] = useState(null);
  const [dati, setDati] = useState(VUOTO_AZIENDA);
  // Valori letti dal server: sottotitolo e note dei campi non ancora modificati.
  const [salvati, setSalvati] = useState(VUOTO_AZIENDA);
  const [anomalie, setAnomalie] = useState([]);
  const [caricamento, setCaricamento] = useState(inModifica);
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  const padre = usePadreAzienda(inModifica ? id : undefined);

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
        const valori = {
          ...VUOTO_AZIENDA,
          ...Object.fromEntries(
            Object.entries(azienda).map(([k, v]) => [k, v ?? ""]),
          ),
        };
        setDati(valori);
        setSalvati(valori);
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
        messaggio={TESTI_AZIENDA.caricamento}
        centrato
      />
    );

  return (
    <div className={contenutoPagina("modulo", { codaAmpia: true })}>
      <IntestazionePagina
        titolo={
          inModifica ? TESTI_AZIENDA.titoloModifica : TESTI_AZIENDA.titoloNuova
        }
        descrizione={
          inModifica
            ? sottotitoloAzienda(salvati.azienda_ragione_sociale, padre.padre)
            : undefined
        }
        indietro={{ rotta: ritorno, etichetta: TESTI_AZIENDA.ritorno }}
      />
      <form onSubmit={invia} className="flex flex-col gap-5">
        {anomalie.length > 0 && (
          <AlertMessage
            message={{ type: "warning", text: anomalie }}
            separato={false}
          />
        )}
        {errore && (
          <AlertMessage
            message={{ type: "error", text: errore }}
            separato={false}
          />
        )}

        <div className={stili.schedaModulo}>
          {SEZIONI_AZIENDA.map(({ chiave, campi }) => (
            <SezioneModulo
              key={chiave}
              titolo={SEZIONI[chiave].titolo}
              descrizione={SEZIONI[chiave].descrizione}
            >
              <CampiAzienda
                dati={dati}
                onChange={aggiorna}
                anomalie={anomalie}
                salvati={salvati}
                gruppo={campi}
              />
            </SezioneModulo>
          ))}
          {inModifica && (
            <SezioneModulo
              titolo={SEZIONI.gerarchia.titolo}
              descrizione={SEZIONI.gerarchia.descrizione}
              griglia={false}
            >
              <GerarchiaAzienda
                aziendaId={id}
                padre={padre.padre}
                errore={padre.errore}
                onRicarica={padre.ricarica}
              />
            </SezioneModulo>
          )}
          {inModifica && (
            <SezioneModulo
              titolo={SEZIONI.convenzioni.titolo}
              descrizione={SEZIONI.convenzioni.descrizione}
              griglia={false}
            >
              <DettaglioConvenzioniUniversitarie aziendaId={id} inSezione />
            </SezioneModulo>
          )}
        </div>

        <div className={barraAzioniModulo("pagina")}>
          <button
            type="button"
            onClick={() => navigate(ritorno)}
            className={pulsante("testuale", "grande")}
          >
            {TESTI_AZIENDA.annulla}
          </button>
          <button
            type="submit"
            disabled={salvataggio}
            className={pulsante("primario", "grande")}
          >
            {salvataggio
              ? TESTI_AZIENDA.salvataggio
              : inModifica
                ? TESTI_AZIENDA.salvaModifiche
                : TESTI_AZIENDA.salva}
          </button>
        </div>
      </form>
    </div>
  );
}
