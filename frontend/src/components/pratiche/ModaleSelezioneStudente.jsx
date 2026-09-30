import { useState } from "react";
import Dialogo from "../shared/Dialogo.jsx";
import { X } from "../../config/icone.js";
import { pulsante, pulsanteIcona } from "../../config/styles/pulsante.js";
import { STILI_MODALE_TABELLA as stili } from "../../config/styles/pratica.js";
import { TESTI_MODALE_STUDENTE as testi } from "../../config/testi/pratiche.js";
import { statoCliente } from "../../lib/righeElenco.js";
import { opzioneStudente } from "../../lib/opzioniPratica.js";
import usePagineRemote from "../../hooks/usePagineRemote.js";
import IndicatoriStato from "../shared/IndicatoriStato.jsx";
import CampoRicerca from "../shared/CampoRicerca.jsx";

const LIMITE = 20;
const estrai = (dati) => ({ elementi: dati, altri: dati.length === LIMITE });

/** Vero solo se le tre verifiche (email, cellulare, diploma) sono superate. */
function selezionabile(indicatori) {
  return indicatori.every((indicatore) => indicatore.attivo);
}

/** Modale di selezione dello studente per una pratica nuova: elenco dei
 * sottoscrittori (ruolo Utente, solo account attivi, stessa visibilità
 * dell'elenco Sottoscrittori), con le stesse tre verifiche mostrate lì.
 * Chi non le ha tutte e tre superate resta visibile ma non si può scegliere. */
export default function ModaleSelezioneStudente({ onScegli, onChiudi }) {
  const [ricerca, setRicerca] = useState("");
  const pagina = usePagineRemote(
    `/clienti/?solo_utenti=true&solo_attivi=true&limit=${LIMITE}&search=${encodeURIComponent(ricerca)}`,
    estrai,
  );
  return (
    <Dialogo aperto onChiudi={onChiudi} etichetta={testi.titolo} variante="selezione">
      <div className={stili.contenuto}>
        <div className="flex items-center justify-between gap-3">
          <h3 id="modale-studente-titolo" className={stili.titolo}>{testi.titolo}</h3>
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
                <th className={stili.intestazioneColonna}>{testi.colonne.codiceFiscale}</th>
                <th className={stili.intestazioneColonna}>{testi.colonne.denominazione}</th>
                <th className={stili.intestazioneColonna}>{testi.colonne.stato}</th>
              </tr>
            </thead>
            <tbody>
              {pagina.elementi.map((cliente) => {
                const indicatori = statoCliente(cliente, false);
                const scelto = selezionabile(indicatori);
                const denominazione = [cliente.cliente_nome, cliente.cliente_cognome]
                  .map((parte) => String(parte ?? "").trim()).filter(Boolean).join(" ") || "-";
                const comune = { className: stili.cella, title: scelto ? undefined : testi.nonSelezionabile };
                return (
                  <tr key={cliente.cliente_id}
                    className={`${stili.riga} ${scelto ? stili.rigaSelezionabile : stili.rigaBloccata}`}
                    tabIndex={scelto ? 0 : undefined}
                    role={scelto ? "button" : undefined}
                    aria-disabled={!scelto}
                    onClick={() => scelto && onScegli(opzioneStudente(cliente))}
                    onKeyDown={(evento) => {
                      if (!scelto || (evento.key !== " " && evento.key !== "Enter")) return;
                      evento.preventDefault();
                      onScegli(opzioneStudente(cliente));
                    }}>
                    <td {...comune}>{cliente.cliente_codice_fiscale || "-"}</td>
                    <td {...comune}>{denominazione}</td>
                    <td {...comune}><IndicatoriStato indicatori={indicatori} /></td>
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
      </div>
    </Dialogo>
  );
}
