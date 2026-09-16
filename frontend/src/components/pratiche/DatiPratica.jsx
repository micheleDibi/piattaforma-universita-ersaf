import { CAMPI_PRATICA } from "../../config/pratica.js";
import { campo, etichetta } from "../../config/styles/campo.js";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";

export default function DatiPratica({ form, nuova }) {
  return <section className={stili.sezione} aria-labelledby="dati-pratica">
    <h2 id="dati-pratica" className={stili.titolo}>Dati della pratica</h2>
    <div className={stili.colonne}>
      {CAMPI_PRATICA.map(({ nome, label, ...opzioni }) => <div key={nome}>
        <label htmlFor={nome} className={etichetta()}>{label}</label>
        <input id={nome} name={nome} {...opzioni} value={form.dati[nome]} onChange={form.aggiorna} className={campo("comodo")} />
      </div>)}
      <div><label htmlFor="pratica_stato_id" className={etichetta()}>Stato</label>
        <select id="pratica_stato_id" name="pratica_stato_id" value={form.dati.pratica_stato_id} onChange={form.aggiorna} className={campo("comodo")} required>
          <option value="">Seleziona uno stato</option>
          {form.stati.map(stato => <option key={stato.id} value={stato.id}>{stato.label}</option>)}
        </select>
      </div>
      <div><label htmlFor="pratica_dataCreazione" className={etichetta()}>Data di creazione</label>
        <input id="pratica_dataCreazione" name="pratica_dataCreazione" type="date" value={form.dati.pratica_dataCreazione}
          onChange={form.aggiorna} readOnly={!nuova} required className={campo("comodo")} />
      </div>
    </div>
    <div><label htmlFor="pratica_note" className={etichetta()}>Note</label>
      <textarea id="pratica_note" name="pratica_note" rows={4} value={form.dati.pratica_note} onChange={form.aggiorna} className={campo("comodo")} />
    </div>
  </section>;
}
