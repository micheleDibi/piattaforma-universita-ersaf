import { NavLink, useLocation, useNavigate } from "react-router";
import { LogOut } from "lucide-react";
import {
  NOME_APPLICAZIONE,
  ROTTE,
  VOCI_MENU,
} from "../../config/routes/rotte";
import {
  iconaNavigazione,
  nomeApplicazione,
  testataMenu,
  voceNavigazione,
  voceUscita,
} from "../../config/styles/navigazione";
import { leggiRuolo } from "../../lib/sessione";
import { logout } from "../../lib/logout";

/**
 * Contenuto del menu: nome dell'applicazione, voci e uscita.
 *
 * Lo stesso contenuto serve la barra laterale da desktop e il cassetto da
 * mobile; `onNaviga` permette al cassetto di chiudersi quando si sceglie una
 * voce.
 */
export default function MenuNavigazione({ onNaviga }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const aderente = leggiRuolo() === "aderente";
  const voci = VOCI_MENU.filter((voce) => !voce.soloAderente || aderente);

  const esci = async () => {
    await logout();
    navigate(ROTTE.accesso, { replace: true });
  };

  const eAttiva = (voce, isActive) =>
    isActive ||
    (voce.prefissi ?? []).some((prefisso) => pathname.startsWith(prefisso));

  return (
    <div className="flex h-full flex-col">
      <div className={testataMenu()}>
        <span className={nomeApplicazione()}>{NOME_APPLICAZIONE}</span>
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
                voceNavigazione(eAttiva(voce, isActive))
              }
            >
              {({ isActive }) => (
                <>
                  <Icona
                    aria-hidden="true"
                    className={iconaNavigazione(eAttiva(voce, isActive))}
                  />
                  <span className="truncate">{voce.etichetta}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t border-bordo p-3">
        <button type="button" onClick={esci} className={voceUscita()}>
          <LogOut aria-hidden="true" className="size-icona shrink-0" />
          <span>Esci</span>
        </button>
      </div>
    </div>
  );
}
