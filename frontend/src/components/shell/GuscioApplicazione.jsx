import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router";
import { Menu, X } from "lucide-react";
import MenuNavigazione from "./MenuNavigazione";
import { NOME_APPLICAZIONE } from "../../config/routes/rotte";
import { pulsanteIcona } from "../../config/styles/pulsante";
import {
  areaContenuto,
  barraLaterale,
  barraSuperiore,
  cassettoMenu,
  veloCassetto,
} from "../../config/styles/guscio";
import { marchio, nomeApplicazione } from "../../config/styles/navigazione";

/**
 * Guscio comune a tutte le pagine autenticate: barra laterale fissa da
 * desktop, barra superiore con menu a scomparsa da mobile, contenuto nel
 * mezzo. Le pagine vengono disegnate nell'Outlet.
 */
export default function GuscioApplicazione() {
  const { pathname } = useLocation();

  // Il menu ricorda la pagina in cui e' stato aperto: cambiando pagina risulta
  // chiuso da solo, senza un effetto che reimposti lo stato a ogni navigazione.
  const [apertoSu, setApertoSu] = useState(null);
  const aperto = apertoSu === pathname;
  const chiudi = () => setApertoSu(null);

  // Con il menu aperto: Esc lo chiude e la pagina sotto non scorre.
  useEffect(() => {
    if (!aperto) return undefined;
    const suTasto = (evento) => {
      if (evento.key === "Escape") setApertoSu(null);
    };
    const overflowPrecedente = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", suTasto);
    return () => {
      window.removeEventListener("keydown", suTasto);
      document.body.style.overflow = overflowPrecedente;
    };
  }, [aperto]);

  return (
    <div className="min-h-screen bg-tela">
      <aside className={barraLaterale()}>
        <MenuNavigazione />
      </aside>

      <header className={barraSuperiore()}>
        <button
          type="button"
          onClick={() => setApertoSu(pathname)}
          className={pulsanteIcona()}
          aria-label="Apri il menu"
          aria-expanded={aperto}
          aria-controls="menu-mobile"
        >
          <Menu aria-hidden="true" className="size-icona" />
        </button>
        <span className={marchio()} aria-hidden="true">
          PU
        </span>
        <span className={nomeApplicazione()}>{NOME_APPLICAZIONE}</span>
      </header>

      {aperto && (
        <div className="lg:hidden">
          <div className={veloCassetto()} onClick={chiudi} aria-hidden="true" />
          <div
            id="menu-mobile"
            role="dialog"
            aria-modal="true"
            aria-label="Menu"
            className={cassettoMenu()}
          >
            <button
              type="button"
              onClick={chiudi}
              aria-label="Chiudi il menu"
              className={`${pulsanteIcona()} absolute right-3 top-2.5`}
            >
              <X aria-hidden="true" className="size-icona" />
            </button>
            <MenuNavigazione onNaviga={chiudi} />
          </div>
        </div>
      )}

      <div className={areaContenuto()}>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
