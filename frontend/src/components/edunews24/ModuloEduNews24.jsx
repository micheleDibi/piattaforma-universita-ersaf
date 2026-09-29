import { useRef, useState } from "react";
import { Link } from "react-router";
import { SEZIONE_PREDEFINITA } from "../../config/edunews24.js";
import { ChevronLeft, ChevronRight } from "../../config/icone.js";
import { LOGO_EDUNEWS24 } from "../../config/identita.js";
import {
  collegamentoInterno,
  frecciaFascia,
  iconaCollegamentoInterno,
  involucroModulo,
} from "../../config/styles/edunews24.js";
import { STILI_LOGO } from "../../config/styles/identita.js";
import { TESTI_EDUNEWS24 as testi } from "../../config/testi/edunews24.js";
import { useFasciaScorrevole } from "../../hooks/useFasciaScorrevole.js";
import { useModuloEduNews24 } from "../../hooks/useModuloEduNews24.js";
import { annuncioEsitoModulo, chiaveVoce, percorsoPaginaEduNews24, voceInEvidenza } from "../../lib/edunews24.js";
import AperturaNotizia from "./AperturaNotizia.jsx";
import FasciaMiniature from "./FasciaMiniature.jsx";
import FolioEduNews24 from "./FolioEduNews24.jsx";
import SelettoreSezioneEduNews24 from "./SelettoreSezioneEduNews24.jsx";
import SocialEduNews24 from "./SocialEduNews24.jsx";
import StatoModuloEduNews24 from "./StatoModuloEduNews24.jsx";
import TabelloneOpportunita from "./TabelloneOpportunita.jsx";
import VocePrincipale from "./VocePrincipale.jsx";

/**
 * Modulo EduNews24 della Dashboard, autosufficiente: si sposta con una riga
 * di JSX dentro .dashboard__moduli. Una sezione alla volta, sempre dalla
 * prima pagina condivisa. Con la funzione spenta (o finche' l'esito e' ignoto
 * e la risposta non tarda) non disegna nulla.
 *
 * - Testata: logo nel titolo h2 e social; barra: selettore e folio (dopo un
 *   caricamento fallito "Contenuti non aggiornati", come nella pagina).
 * - Corpo (altezza minima uguale per sezioni e stati): Notizie con apertura e
 *   fascia; Interpelli e Selezione con voce principale e tabellone; oppure
 *   scheletro, errore o vuoto.
 * - Piede: frecce della fascia (solo Notizie) e il link "Tutte le ...".
 * - Regione aria-live: "In evidenza: ..." dopo la scelta di una miniatura;
 *   dopo "Riprova", l'esito del nuovo tentativo quando arriva
 *   (annuncioEsitoModulo). Svuotata al cambio di sezione.
 *
 * La scelta di una miniatura (`scelta`) vale per la sezione corrente: il
 * cambio di sezione la azzera, cosi' al ritorno l'apertura riparte dalla voce
 * piu' recente e il sipario non parte.
 */
export default function ModuloEduNews24() {
  const [sezione, setSezione] = useState(SEZIONE_PREDEFINITA);
  const [scelta, setScelta] = useState(null);
  const [annuncio, setAnnuncio] = useState("");
  const [annunciaEsito, setAnnunciaEsito] = useState(false);
  const rifFascia = useRef(null);
  const rifCorpo = useRef(null);
  const modulo = useModuloEduNews24(sezione);
  const notizie = sezione === "notizie" && modulo.stato === "pronto";
  const fascia = useFasciaScorrevole(rifFascia, notizie ? modulo.voci.map(chiaveVoce).join(" ") : "");

  if (modulo.stato === "nascosto") return null;

  const evidenza = notizie ? voceInEvidenza(modulo.voci, scelta) : null;
  const cambio = scelta !== null;

  function cambiaSezione(nuova) {
    if (nuova === sezione) return;
    setSezione(nuova);
    setScelta(null);
    setAnnuncio("");
    setAnnunciaEsito(false);
  }

  // La voce gia' in evidenza non cambia nulla: niente sipario sullo stesso
  // media e niente annuncio ripetuto.
  function scegli(voce) {
    const chiave = chiaveVoce(voce);
    if (evidenza && chiave === chiaveVoce(evidenza)) return;
    setScelta(chiave);
    setAnnuncio(testi.inEvidenza(voce.titolo));
    setAnnunciaEsito(false);
  }

  // "Riprova" sparisce con lo scheletro: il fuoco passa prima al corpo, come
  // nella pagina passa al tabpanel, e chi usa la tastiera non torna all'inizio.
  // L'esito del nuovo tentativo si annuncia quando arriva: durante lo
  // scheletro il testo e' vuoto, cosi' anche lo stesso esito si ripete.
  function riprova() {
    setAnnuncio("");
    setAnnunciaEsito(true);
    rifCorpo.current?.focus();
    modulo.riprova();
  }

  return (
    <section className={[involucroModulo(), "edunews24 edunews24-modulo dashboard__modulo"].join(" ")}
      data-ampiezza="piena" aria-labelledby="edunews24-modulo-titolo">
      <div className="edunews24-modulo__testata">
        <h2 id="edunews24-modulo-titolo" className="edunews24-modulo__titolo">
          <img {...LOGO_EDUNEWS24} className={STILI_LOGO.edunews24Modulo} />
        </h2>
        <SocialEduNews24 variante="modulo" className="edunews24-modulo__social" />
      </div>

      <div className="edunews24-modulo__barra">
        <SelettoreSezioneEduNews24 sezione={sezione} onCambia={cambiaSezione} />
        <FolioEduNews24 aggiornatoIl={modulo.aggiornatoIl} stantio={modulo.stantio}
          errore={modulo.stato === "errore"} adesso={modulo.adesso} />
      </div>

      <div ref={rifCorpo} id="edunews24-modulo-corpo" className="edunews24-modulo__corpo" data-sezione={sezione}
        data-stato={modulo.stato} tabIndex={-1}>
        {evidenza && (
          <>
            <AperturaNotizia key={chiaveVoce(evidenza)} voce={evidenza} adesso={modulo.adesso} cambio={cambio} />
            <FasciaMiniature rif={rifFascia} voci={modulo.voci} chiaveEvidenza={chiaveVoce(evidenza)}
              cambio={cambio} scorrevole={fascia.scorrevole} onScegli={scegli} />
          </>
        )}
        {modulo.stato === "pronto" && sezione !== "notizie" && (
          <>
            <VocePrincipale voce={modulo.voci[0]} adesso={modulo.adesso} />
            {modulo.voci.length > 1 && (
              <TabelloneOpportunita sezione={sezione} voci={modulo.voci.slice(1)} adesso={modulo.adesso} />
            )}
          </>
        )}
        {modulo.stato !== "pronto" && (
          <StatoModuloEduNews24 stato={modulo.stato} sezione={sezione} errore={modulo.errore}
            bloccato={modulo.bloccato} onRiprova={riprova} />
        )}
      </div>

      <p className="sr-only" aria-live="polite">
        {annunciaEsito ? annuncioEsitoModulo(modulo.stato, sezione) : annuncio}
      </p>

      <div className="edunews24-modulo__piede">
        {evidenza && (
          <div className="edunews24-modulo__frecce" data-scorrevole={fascia.scorrevole ? "true" : "false"}>
            <button type="button" className={frecciaFascia()} aria-controls="edunews24-fascia"
              aria-label={testi.precedenti} aria-disabled={fascia.allInizio}
              onClick={() => {
                if (!fascia.allInizio) fascia.scorri(-1);
              }}>
              <ChevronLeft aria-hidden="true" className="size-icona" />
            </button>
            <button type="button" className={frecciaFascia()} aria-controls="edunews24-fascia"
              aria-label={testi.successive} aria-disabled={fascia.allaFine}
              onClick={() => {
                if (!fascia.allaFine) fascia.scorri(1);
              }}>
              <ChevronRight aria-hidden="true" className="size-icona" />
            </button>
          </div>
        )}
        <Link to={percorsoPaginaEduNews24(sezione)} className={collegamentoInterno()}>
          {testi.vediTutto[sezione]}
          <ChevronRight aria-hidden="true" className={iconaCollegamentoInterno()} />
        </Link>
      </div>
    </section>
  );
}
