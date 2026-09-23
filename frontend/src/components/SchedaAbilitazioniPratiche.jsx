import { TESTI_ABILITAZIONI_PRATICHE } from "../config/testi/anagrafica.js";
import {
  interruttore,
  levettaInterruttore,
  STILI_ANAGRAFICA as stili,
} from "../config/styles/anagrafica.js";

// Colonne dei flag legacy: -1 abilitato, 0 no. Le etichette stanno in config/testi.
const CAMPI_ABILITAZIONE = [
  "cliente_abilPraticheUniv",
  "cliente_abilitazione_ecampus",
  "cliente_abilitazione_link_campus",
  "cliente_abilitazione_corsi_speciali",
  "cliente_abilitazione_a4u",
];

/**
 * Abilitazioni dell'attuatore alle pratiche: una riga a scheda per flag.
 * L'intera riga e' l'etichetta dell'interruttore, quindi si clicca ovunque.
 */
export default function SchedaAbilitazioniPratiche({ formData, onCambia }) {
  return (
    <div className={stili.abilitazioni}>
      {CAMPI_ABILITAZIONE.map((chiave) => {
        const attivo = formData[chiave] === -1;
        return (
          <label key={chiave} className={stili.rigaAbilitazione}>
            {TESTI_ABILITAZIONI_PRATICHE[chiave]}
            <button
              type="button"
              role="switch"
              aria-checked={attivo}
              onClick={() => onCambia(chiave, attivo ? 0 : -1)}
              className={interruttore(attivo)}
            >
              <span aria-hidden="true" className={levettaInterruttore(attivo)} />
            </button>
          </label>
        );
      })}
    </div>
  );
}
