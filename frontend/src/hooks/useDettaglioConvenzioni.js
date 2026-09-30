import { useEffect, useState } from "react";
import { caricaDettaglioConvenzioni, salvaDettaglioConvenzioni } from "../lib/schedaAzienda.js";
import { CAMPI_PERCENTUALI } from "../config/campiPercentuali.js";

/**
 * Percentuali delle convenzioni universitarie di un'azienda: lettura e, se
 * serve, scrittura. Condivisa da DettaglioConvenzioniUniversitarie.jsx sia in
 * sola lettura (scheda dell'attuatore, che chiama solo caricamento/dettaglio)
 * sia in scrittura (scheda dell'azienda, che chiama anche salva): il
 * salvataggio non ha piu' un pulsante proprio, lo aziona "Salva modifiche"
 * della scheda azienda (vedi SchedaAzienda.jsx), che deve anche sapere se
 * serve fermarsi per una conferma prima di proseguire con l'anagrafica.
 *
 * Senza aziendaId (azienda nuova) non legge e non salva niente.
 *
 * @param {string|number|undefined} aziendaId
 */
export default function useDettaglioConvenzioni(aziendaId) {
  const [dettaglio, setDettaglio] = useState(null);
  const [caricamento, setCaricamento] = useState(Boolean(aziendaId));
  const [errore, setErrore] = useState("");
  const [salvataggio, setSalvataggio] = useState(false);
  // null: nessuna conferma in sospeso. Un array (mai vuoto quando presente):
  // i campi che verrebbero azzerati, per il messaggio di conferma (vedi
  // messaggioAzzeramento in lib/schedaAzienda.js).
  const [resetPendente, setResetPendente] = useState(null);

  useEffect(() => {
    if (!aziendaId) return;
    let annullato = false;
    caricaDettaglioConvenzioni(aziendaId)
      .then((dati) => { if (!annullato) setDettaglio(dati); })
      .catch((err) => { if (!annullato) setErrore(err.message); })
      .finally(() => { if (!annullato) setCaricamento(false); });
    return () => { annullato = true; };
  }, [aziendaId]);

  const aggiornaPercentuale = (evento) => {
    const { name, value } = evento.target;
    setDettaglio((prec) => ({ ...prec, [name]: value === "" ? 0 : Number(value) }));
  };

  // true: salvato (o non c'era niente da confermare). false: in sospeso in
  // attesa di conferma, o fallito con errore - in entrambi i casi chi chiama
  // deve fermarsi e non proseguire con il resto del salvataggio della scheda.
  const salva = async (conferma = false) => {
    setErrore("");
    setSalvataggio(true);
    try {
      const valori = Object.fromEntries(
        CAMPI_PERCENTUALI.map(([chiave]) => [chiave, dettaglio?.[chiave] ?? 0]),
      );
      const risultato = await salvaDettaglioConvenzioni(aziendaId, valori, { conferma });
      if (risultato.esito === "richiedeConferma") {
        setResetPendente(risultato.reset);
        return false;
      }
      setResetPendente(null);
      setDettaglio(risultato.dettaglio);
      return true;
    } catch (err) {
      setErrore(err.message);
      return false;
    } finally {
      setSalvataggio(false);
    }
  };

  return {
    dettaglio, caricamento, errore, salvataggio, resetPendente,
    aggiornaPercentuale, salva,
    annullaConferma: () => setResetPendente(null),
  };
}
