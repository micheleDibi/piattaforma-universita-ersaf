import { useState } from "react";
import { X } from "../../config/icone.js";
import ModaleSelezioneStudente from "./ModaleSelezioneStudente.jsx";
import ModaleSelezionePercorso from "./ModaleSelezionePercorso.jsx";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";
import { pulsante, pulsanteIcona } from "../../config/styles/pulsante.js";
import { etichetta } from "../../config/styles/campo.js";

export default function RelazioniPratica({ form, nuova, universitaId, tipoCorsoIds, corsiSingoli }) {
  const [modaleStudenteAperto, setModaleStudenteAperto] = useState(false);
  const [modalePercorsoAperto, setModalePercorsoAperto] = useState(false);
  const percorsi = corsiSingoli ? form.corsiSelezionati : (form.percorso ? [form.percorso] : []);
  return <section className={stili.sezione} aria-labelledby="iscrizione-pratica">
    <h2 id="iscrizione-pratica" className={stili.titolo}>Iscrizione</h2>
    <div className={stili.colonne}>
      {/* Studente: non piu' una ricerca a testo libero. Il modale mostra
          l'elenco dei sottoscrittori, con le loro verifiche, e blocca la
          scelta di chi non le ha ancora tutte e tre superate. */}
      <div>
        <span className={etichetta()}>Studente</span>
        {nuova ? (
          <div className="mt-1 flex flex-wrap items-center gap-3">
            <span className={stili.valore}>{form.studente?.label || "Nessuno studente selezionato"}</span>
            <button type="button" className={pulsante("discreto", "piccolo")}
              onClick={() => setModaleStudenteAperto(true)}>
              {form.studente ? "Cambia" : "Seleziona"}
            </button>
          </div>
        ) : (
          <p className={stili.valore}>{form.studente?.label || "Non indicato"}</p>
        )}
      </div>
      {/* Aderente emittente non compare piu', ne' in creazione ne' in
          modifica: e' un dato tecnico superato (colonna deprecata), e il
          database applica da solo il suo valore convenzionale. */}
      {/* Percorso formativo: un modale con tabella (Codice, Denominazione,
          Prezzo, CFU), filtrato per università e tipo di corso di provenienza
          (vedi leggiContestoUrl in lib/schedaPratica.js). A scelta multipla
          solo per Corsi Singoli: gli altri corsi restano qui come elenco,
          ognuno con il proprio pulsante per toglierlo. */}
      <div>
        <span className={etichetta()}>{corsiSingoli ? "Corsi" : "Percorso formativo"}</span>
        {nuova ? (
          <div className="mt-1 space-y-2">
            {corsiSingoli && !!percorsi.length && (
              <ul className={stili.elencoCorsi}>
                {percorsi.map((corso) => (
                  <li key={corso.id} className={stili.rigaCorso}>
                    <span className={stili.valore}>{corso.label}<small className="ml-1 text-testo-tenue">{corso.codice}</small></span>
                    <button type="button" className={pulsanteIcona("neutro", "minima")}
                      aria-label={`Rimuovi ${corso.label}`}
                      onClick={() => form.setPercorsi(percorsi.filter((c) => c.id !== corso.id))}>
                      <X aria-hidden="true" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="flex flex-wrap items-center gap-3">
              {!corsiSingoli && <span className={stili.valore}>{form.percorso?.label || "Nessun percorso selezionato"}</span>}
              <button type="button" className={pulsante("discreto", "piccolo")}
                onClick={() => setModalePercorsoAperto(true)}>
                {corsiSingoli ? (percorsi.length ? "Aggiungi o modifica" : "Seleziona") : (form.percorso ? "Cambia" : "Seleziona")}
              </button>
            </div>
          </div>
        ) : (
          <p className={stili.valore}>{form.percorso?.label || "Non indicato"}</p>
        )}
      </div>
      <dl><dt className={etichetta()}>Università</dt>
        <dd className={stili.valore}>{form.universitaLabel || (nuova ? "Seleziona un percorso formativo" : "Non indicata")}</dd></dl>
    </div>
    {form.erroreProdotto && <p role="alert" className="text-negativo">{form.erroreProdotto}</p>}
    {modaleStudenteAperto && (
      <ModaleSelezioneStudente
        onScegli={studente => { form.setStudente(studente); setModaleStudenteAperto(false); }}
        onChiudi={() => setModaleStudenteAperto(false)}
      />
    )}
    {modalePercorsoAperto && (
      <ModaleSelezionePercorso
        universitaId={universitaId} tipoCorsoIds={tipoCorsoIds} multipla={corsiSingoli}
        selezionati={percorsi}
        onConferma={form.setPercorsi}
        onChiudi={() => setModalePercorsoAperto(false)}
      />
    )}
  </section>;
}
