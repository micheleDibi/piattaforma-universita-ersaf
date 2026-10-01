import { CAMPI_PRATICA, CAMPI_RINNOVO, codiceAsgModificabile, eGruppoLauree } from "../../config/pratica.js";
import { campo, etichetta, sceltaInLinea, spunta } from "../../config/styles/campo.js";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";
import { leggiRuolo } from "../../lib/sessione.js";
import { eVero } from "../../lib/flagLegacy.js";

export default function DatiPratica({ form, nuova, prodotto }) {
  // Lo stato lo cambia solo il Nazionale, e solo in modifica: una pratica
  // nasce sempre in Bozza, il server lo impone comunque (vedi crea_pratica
  // in backend/src/pratiche/routers.py).
  const eNazionale = leggiRuolo() === "nazionale";
  // Il rinnovo si mostra solo per le Lauree (vedi la card Trello "Pratica -
  // visibilita' campi per percorso formativo"): gli altri tipi di corso non
  // hanno questo concetto.
  const mostraRinnovo = eGruppoLauree(prodotto?.listino_tipoCorso_id);
  // Solo per il Nazionale e solo sulle pratiche eCampus: gli altri ruoli non
  // lo ricevono nemmeno dal server.
  const mostraCodiceAsg = !nuova && codiceAsgModificabile(leggiRuolo(), form.dati.nome_universita_id);
  return <section className={stili.sezione} aria-labelledby="dati-pratica">
    <h2 id="dati-pratica" className={stili.titolo}>Dati della pratica</h2>
    <div className={stili.colonne}>
      {/* Sempre di sola lettura: lo genera il server al salvataggio (vedi
          backend/src/pratiche/codice.py), resta vuoto solo prima di quello. */}
      <div><span className={etichetta()}>Codice pratica</span>
        <p className={stili.valore}>{form.dati.pratica_numero || "-"}</p>
      </div>
      {mostraCodiceAsg && <div><label htmlFor="pratica_codiceASG" className={etichetta()}>Codice ASG</label>
        <input id="pratica_codiceASG" name="pratica_codiceASG" maxLength={45} value={form.dati.pratica_codiceASG ?? ""}
          onChange={form.aggiorna} className={campo("comodo")} />
      </div>}
      {CAMPI_PRATICA.map(({ nome, label, ...opzioni }) => <div key={nome}>
        <label htmlFor={nome} className={etichetta()}>{label}</label>
        <input id={nome} name={nome} {...opzioni} value={form.dati[nome]} onChange={form.aggiorna} className={campo("comodo")} />
      </div>)}
      {/* Sempre di sola lettura: arriva dal percorso formativo scelto
          (vedi prezzoAttuale in lib/praticaForm.js), non si digita mai. */}
      <div><label htmlFor="pratica_prezzo" className={etichetta()}>Prezzo (€)</label>
        <input id="pratica_prezzo" name="pratica_prezzo" type="number" min="0" step="any" required
          readOnly value={form.dati.pratica_prezzo} onChange={form.aggiorna} className={campo("comodo")} />
      </div>
      {/* In creazione sempre di sola lettura, parte su "Bozza": il server la
          impone comunque. In modifica la cambia solo il Nazionale, con la
          tendina; per tutti gli altri resta di sola lettura. */}
      {!nuova && eNazionale ? (
        <div><label htmlFor="pratica_stato_id" className={etichetta()}>Stato</label>
          <select id="pratica_stato_id" name="pratica_stato_id" value={form.dati.pratica_stato_id}
            onChange={form.aggiorna} className={campo("comodo")}>
            {form.stati?.map(stato => <option key={stato.id} value={stato.id}>{stato.label}</option>)}
          </select>
        </div>
      ) : (
        <div><span className={etichetta()}>Stato</span>
          <p className={stili.valore}>{nuova ? (form.statoIniziale?.label ?? "Bozza") : form.dati.pratica_stato_descrizione}</p>
        </div>
      )}
      {/* Sempre di sola lettura: in creazione e' sempre la data odierna, non
          modificabile; in modifica resta quella storica della pratica. */}
      <div><label htmlFor="pratica_dataCreazione" className={etichetta()}>Data di creazione</label>
        <input id="pratica_dataCreazione" name="pratica_dataCreazione" type="date" value={form.dati.pratica_dataCreazione}
          onChange={form.aggiorna} readOnly required className={campo("comodo")} />
      </div>
    </div>
    {/* Solo per le Lauree: un solo anno alla volta, o nessuno (vedi
        impostaRinnovo in hooks/useSchedaPratica.js e il validatore gemello
        lato server, CAMPI_RINNOVO in backend/src/pratiche/rinnovi.py). */}
    {mostraRinnovo && (
      <fieldset>
        <legend className={etichetta()}>Rinnovo</legend>
        <div className={stili.scelteRinnovo}>
          {CAMPI_RINNOVO.map(({ nome, label }) => (
            <label key={nome} className={sceltaInLinea()}>
              <input type="checkbox" name={nome} className={spunta()}
                checked={eVero(form.dati[nome])}
                onChange={evento => form.impostaRinnovo(evento.target.checked ? nome : null)} />
              {label}
            </label>
          ))}
        </div>
      </fieldset>
    )}
    <div><label htmlFor="pratica_note" className={etichetta()}>Note</label>
      <textarea id="pratica_note" name="pratica_note" rows={4} value={form.dati.pratica_note} onChange={form.aggiorna} className={campo("comodo")} />
    </div>
  </section>;
}
