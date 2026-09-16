import { NavLink, useNavigate } from "react-router";
import { LogOut } from "../../config/icone.js";
import {
  ROTTE,
  vociMenuPerRuolo,
} from "../../config/routes/rotte";
import {
  iconaNavigazione,
  notaVersione,
  testataMenu,
  voceNavigazione,
  voceUscita,
} from "../../config/styles/navigazione";
import { VERSIONE_APPLICAZIONE } from "../../lib/versione.js";
import { useSessione } from "../../hooks/useSessione.js";
import TileProfilo from "../profilo/TileProfilo.jsx";
import { logout } from "../../lib/logout";
import { useState } from "react";
import { LOGO_UNIVERSITA } from "../../config/identita.js";
import { STILI_LOGO } from "../../config/styles/identita.js";

/**
 * Contenuto del menu: logo dell'applicazione, voci e uscita.
 *
 * Lo stesso contenuto serve la barra laterale da desktop e il cassetto da
 * mobile; `onNaviga` permette al cassetto di chiudersi quando si sceglie una
 * voce.
 */
export default function MenuNavigazione({ onNaviga }) {
  const [erroreUscita, setErroreUscita] = useState("");
  const navigate = useNavigate();
  const voci = vociMenuPerRuolo(useSessione()?.ruoloCodice);

  const esci = async () => {
    setErroreUscita("");
    try {
      await logout();
      navigate(ROTTE.accesso, { replace: true });
    } catch (errore) { setErroreUscita(errore.message); }
  };

  return (
    <div className="flex h-full flex-col">
      <div className={testataMenu()}>
        <img {...LOGO_UNIVERSITA} className={STILI_LOGO.navigazione} />
      </div>

      <nav
        aria-label="Navigazione principale"
        className="flex-1 space-y-1 overflow-y-auto p-3"
      >
        {voci.map((voce) => {
          const Icona = voce.icona;
          return (
            <NavLink
              key={voce.rotta}
              to={voce.rotta}
              onClick={onNaviga}
              className={({ isActive }) =>
                voceNavigazione(isActive)
              }
            >
              {({ isActive }) => (
                <>
                  <Icona
                    aria-hidden="true"
                    className={iconaNavigazione(isActive)}
                  />
                  <span className="truncate">{voce.etichetta}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className={notaVersione()}>
        <p>{VERSIONE_APPLICAZIONE.versione}</p>
        {VERSIONE_APPLICAZIONE.aggiornamento && <p>{VERSIONE_APPLICAZIONE.aggiornamento}</p>}
      </div>

      <div className="border-t border-bordo p-3">
        <TileProfilo onNaviga={onNaviga} />
        {erroreUscita && <p role="alert" className="text-sm text-negativo">{erroreUscita}</p>}
        <button type="button" onClick={esci} className={voceUscita()}>
          <LogOut aria-hidden="true" className="size-icona shrink-0" />
          <span>Esci</span>
        </button>
      </div>
    </div>
  );
}
