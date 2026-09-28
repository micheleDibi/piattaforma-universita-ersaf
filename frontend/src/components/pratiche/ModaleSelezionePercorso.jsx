import { useState } from "react";
import { createPortal } from "react-dom";
import { X } from "../../config/icone.js";
import { pulsante, pulsanteIcona } from "../../config/styles/pulsante.js";
import { STILI_MODALE_TABELLA as stili } from "../../config/styles/pratica.js";
import { TESTI_MODALE_PERCORSO as testi } from "../../config/testi/pratiche.js";
import { paginaPercorsi } from "../../lib/opzioniPratica.js";
import usePagineRemote from "../../hooks/usePagineRemote.js";
import CampoRicerca from "../shared/CampoRicerca.jsx";

const LIMITE = 20;

function formattaImporto(numero) {
  return Number(numero).toLocaleString("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function costruisciEndpoint(universitaId, tipoCorsoIds, ricerca) {
  const params = new URLSearchParams({ limit: String(LIMITE), search: ricerca, attivo: "-1", valido_oggi: "true" });
  if (universitaId) params.set("nome_universita_id", String(universitaId));
  tipoCorsoIds.forEach((id) => params.append("listino_tipo_corso_id", String(id)));
  return `/listini-testa/?${params}`;
}

/** Modale di selezione del percorso formativo per una pratica nuova: elenco
 * filtrato per l'università e il/i tipo/i di corso di provenienza (vedi
 * leggiContestoUrl in lib/schedaPratica.js), solo prodotti attivi con un
 * dettaglio di listino valido oggi (GET /listini-testa/ fa gia' questo
 * filtro, qui non serve gestire il caso "nessun prezzo attivo").
 *
 * A scelta singola per la maggior parte dei tipi di corso: un click sceglie
 * e chiude subito, come ModaleSelezioneStudente. A scelta multipla solo per
 * Corsi Singoli (`multipla`): un click aggiunge o toglie dalla selezione, un
 * piede mostra quanti corsi e il totale, e resta aperto finche' non si preme
 * Conferma. */
export default function ModaleSelezionePercorso({ universitaId, tipoCorsoIds, multipla, selezionati: selezionatiIniziali, onConferma, onChiudi }) {
  const [ricerca, setRicerca] = useState("");
  const [selezionati, setSelezionati] = useState(selezionatiIniziali ?? []);
  const pagina = usePagineRemote(costruisciEndpoint(universitaId, tipoCorsoIds, ricerca), paginaPercorsi);
  const gia = (id) => selezionati.some((s) => s.id === id);
  const clicca = (opzione) => {
    if (!multipla) { onConferma([opzione]); onChiudi(); return; }
    setSelezionati((precedenti) =>
      gia(opzione.id) ? precedenti.filter((s) => s.id !== opzione.id) : [...precedenti, opzione]);
  };
  const totale = selezionati.reduce((somma, corso) => somma + Number(corso.prezzo ?? 0), 0);
  return createPortal(
    <div className={stili.velo}>
      <div className={stili.finestraLarga} role="dialog" aria-modal="true" aria-labelledby="modale-percorso-titolo">
        <div className="flex items-center justify-between gap-3">
          <h3 id="modale-percorso-titolo" className={stili.titolo}>{multipla ? testi.titoloMultiplo : testi.titolo}</h3>
          <button type="button" onClick={onChiudi} className={pulsanteIcona("neutro", "grande")}
            aria-label={testi.chiudi}>
            <X aria-hidden="true" />
          </button>
        </div>
        <div className="mt-4">
          <CampoRicerca valore={ricerca} onCambia={setRicerca}
            segnaposto={testi.segnaposto} etichetta={testi.segnaposto} />
        </div>
        <div className={stili.corpo}>
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className={stili.intestazioneColonna}>{testi.colonne.codice}</th>
                <th className={stili.intestazioneColonna}>{testi.colonne.denominazione}</th>
                <th className={stili.intestazioneColonna}>{testi.colonne.prezzo}</th>
                <th className={stili.intestazioneColonna}>{testi.colonne.cfu}</th>
              </tr>
            </thead>
            <tbody>
              {pagina.elementi.map((opzione) => {
                const scelto = gia(opzione.id);
                return (
                  <tr key={opzione.id}
                    className={`${stili.riga} ${scelto ? stili.rigaScelta : stili.rigaSelezionabile}`}
                    tabIndex={0}
                    role={multipla ? "checkbox" : "button"}
                    aria-checked={multipla ? scelto : undefined}
                    onClick={() => clicca(opzione)}
                    onKeyDown={(evento) => {
                      if (evento.key !== " " && evento.key !== "Enter") return;
                      evento.preventDefault();
                      clicca(opzione);
                    }}>
                    <td className={stili.cella}>{opzione.codice || "-"}</td>
                    <td className={stili.cella}>{opzione.label}</td>
                    <td className={stili.cella}>{opzione.prezzo == null ? "-" : formattaImporto(opzione.prezzo)}</td>
                    <td className={stili.cella}>{opzione.cfu ?? "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p role="status" className="py-3 text-center text-sm text-testo-tenue">
            {pagina.loading ? testi.caricamento
              : !pagina.errore && !pagina.elementi.length ? testi.vuoto : ""}
          </p>
          {pagina.errore && <p role="alert" className="pb-3 text-center text-sm text-negativo">{pagina.errore}</p>}
          {(pagina.altri || pagina.errore) && (
            <div className="flex justify-center pb-2">
              <button type="button" disabled={pagina.loading} onClick={pagina.carica}
                className={pulsante("discreto")}>
                {pagina.errore ? testi.riprova : testi.mostraAltri}
              </button>
            </div>
          )}
        </div>
        {multipla && (
          <div className={stili.piede}>
            <span className={stili.totale}>{testi.scelti(selezionati.length)} · {testi.totale(formattaImporto(totale))}</span>
            <button type="button" className={pulsante("primario")} disabled={!selezionati.length}
              onClick={() => { onConferma(selezionati); onChiudi(); }}>
              {testi.conferma}
            </button>
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}
