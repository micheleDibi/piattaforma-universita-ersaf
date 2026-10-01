import { X } from "../../config/icone.js";
import { pulsanteIcona } from "../../config/styles/pulsante.js";
import { STILI_PRATICA as stili } from "../../config/styles/pratica.js";
import { TESTI_CORSI_PRATICA as testi } from "../../config/testi/pratiche.js";
import { formattaImporto } from "../../lib/praticaForm.js";

const testo = (valore) => (valore === null || valore === undefined || valore === "" ? "-" : String(valore));

/** I corsi di una pratica Corsi Singoli, al posto delle "Caratteristiche del
 * percorso" (che per Corsi Singoli mostravano CFU e corso di laurea del solo
 * primo corso): una riga per corso con codice, denominazione, corso di
 * laurea, CFU e prezzo. Con `onRimuovi` (pratica nuova) ogni riga ha la X per
 * toglierlo; in visualizzazione l'elenco e' di sola lettura. Porta con se' il
 * proprio separatore, come CaratteristichePercorso. */
export default function ElencoCorsiPratica({ corsi, onRimuovi }) {
  return <>
    <hr className={stili.separatore} />
    <section className={stili.sezione} aria-labelledby="corsi-pratica">
      <h2 id="corsi-pratica" className={stili.titolo}>{testi.titolo}</h2>
      {corsi.length ? (
        <div className={stili.tabellaCorsi}>
          <table className={stili.tabella}>
            <thead>
              <tr>
                <th scope="col" className={stili.intestazione}>{testi.colonne.codice}</th>
                <th scope="col" className={stili.intestazione}>{testi.colonne.denominazione}</th>
                <th scope="col" className={stili.intestazione}>{testi.colonne.corsoLaurea}</th>
                <th scope="col" className={stili.intestazioneNumero}>{testi.colonne.cfu}</th>
                <th scope="col" className={stili.intestazioneNumero}>{testi.colonne.prezzo}</th>
                {onRimuovi && <th scope="col" className={stili.intestazione}><span className="sr-only">{testi.colonne.azioni}</span></th>}
              </tr>
            </thead>
            <tbody>
              {corsi.map((corso) => (
                <tr key={corso.id} className={stili.rigaCorso}>
                  <td className={stili.cellaCodice}>{testo(corso.codice)}</td>
                  <td className={stili.cella}>{testo(corso.label)}</td>
                  <td className={stili.cellaTenue}>{testo(corso.corsoLaurea)}</td>
                  <td className={stili.cellaNumero}>{testo(corso.cfu)}</td>
                  <td className={stili.cellaNumero}>{corso.prezzo == null ? "-" : formattaImporto(corso.prezzo)}</td>
                  {onRimuovi && (
                    <td className={stili.cellaAzione}>
                      <button type="button" className={pulsanteIcona("neutro", "minima")}
                        aria-label={testi.rimuovi(corso.label)} title={testi.rimuovi(corso.label)}
                        onClick={() => onRimuovi(corso)}>
                        <X aria-hidden="true" />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className={stili.nota}>{testi.vuoto}</p>
      )}
    </section>
  </>;
}
