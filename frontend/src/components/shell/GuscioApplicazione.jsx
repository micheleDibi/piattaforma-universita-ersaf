import { useState } from "react";
import Dialogo from "../shared/Dialogo.jsx";
import { useSchermoCompatto } from "../../hooks/useSchermoCompatto.js";
import { useIngresso } from "../../hooks/useIngresso.js";
import { movimentoPagina } from "../../config/styles/movimento.js";
import { NavLink, Outlet, useLocation } from "react-router";
import { CircleUserRound, Menu, X } from "../../config/icone.js";
import { ROTTE } from "../../config/routes/rotte.js";
import { TESTI_PROFILO } from "../../config/testi/profilo.js";
import { accessoProfiloMobile, STILI_PROFILO } from "../../config/styles/profilo.js";
import MenuNavigazione from "./MenuNavigazione";
import { LOGO_UNIVERSITA } from "../../config/identita.js";
import { STILI_LOGO } from "../../config/styles/identita.js";
import { pulsanteIcona } from "../../config/styles/pulsante";
import {
  areaContenuto,
  barraLaterale,
  barraSuperiore,
} from "../../config/styles/guscio";

/**
 * Guscio comune a tutte le pagine autenticate: barra laterale fissa da
 * desktop, barra superiore con menu a scomparsa da mobile, contenuto nel
 * mezzo. Le pagine vengono disegnate nell'Outlet.
 */
export default function GuscioApplicazione() {
  const { pathname } = useLocation();
  const compatto = useSchermoCompatto();
  const contenuto = useIngresso(pathname);

  // Il menu ricorda la pagina in cui e' stato aperto: cambiando pagina risulta
  // chiuso da solo, senza un effetto che reimposti lo stato a ogni navigazione.
  const [apertoSu, setApertoSu] = useState(null);
  const aperto = compatto && apertoSu === pathname;
  const chiudi = () => setApertoSu(null);

  return (
    <div className="min-h-screen bg-tela">
      <aside className={barraLaterale()}>
        <MenuNavigazione />
      </aside>

      <header className={barraSuperiore()}>
        <button
          type="button"
          onClick={() => setApertoSu(pathname)}
          className={pulsanteIcona("neutro", "grande")}
          aria-label="Apri il menu"
          aria-expanded={aperto}
          aria-controls="menu-mobile"
        >
          <Menu aria-hidden="true" className="size-icona" />
        </button>
        <img {...LOGO_UNIVERSITA} className={STILI_LOGO.barraMobile} />
        <NavLink to={ROTTE.profilo} aria-label={TESTI_PROFILO.titolo}
          className={({ isActive }) => accessoProfiloMobile(isActive)}>
          <CircleUserRound aria-hidden="true" className={STILI_PROFILO.icona} />
        </NavLink>
      </header>

      <Dialogo id="menu-mobile" aperto={aperto} onChiudi={chiudi} etichetta="Menu" variante="menu">
            <button
              type="button"
              onClick={chiudi}
              aria-label="Chiudi il menu"
              className={`${pulsanteIcona()} absolute right-3 top-2.5`}
            >
              <X aria-hidden="true" className="size-icona" />
            </button>
            <MenuNavigazione onNaviga={chiudi} />
      </Dialogo>

      <div className={areaContenuto()}>
        <main ref={contenuto} className={movimentoPagina(pathname)}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
