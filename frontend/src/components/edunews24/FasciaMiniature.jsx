import { occhiello, titoloVoce } from "../../config/styles/edunews24.js";
import { TESTI_EDUNEWS24 as testi } from "../../config/testi/edunews24.js";
import { chiaveVoce, haVideo, titoloModulo, varianteRipiego } from "../../lib/edunews24.js";
import DistintivoVideo from "./DistintivoVideo.jsx";
import ImmagineArticolo from "./ImmagineArticolo.jsx";

// Con la tastiera la miniatura a fuoco viene portata in vista. Non al clic:
// la fascia scorrerebbe fra la pressione e il rilascio del puntatore e il
// clic finirebbe su un'altra miniatura.
function portaInVista(evento) {
  const miniatura = evento.currentTarget;
  if (miniatura.matches(":focus-visible")) miniatura.scrollIntoView({ block: "nearest", inline: "nearest" });
}

/**
 * Fascia delle miniature del modulo: tutte le notizie della prima pagina,
 * compresa quella in evidenza. Scorrimento solo manuale (swipe, trackpad,
 * frecce del piede), nativo con scroll-snap. Ogni miniatura e' un pulsante
 * aria-pressed (mai un link: link e "Fonte" stanno nell'apertura) che porta
 * la voce nell'apertura; la scelta si vede dai triangoli della cornice.
 *
 * Dentro il pulsante solo contenuto in linea (span): cornice, media e quadro
 * diventano blocchi nel CSS. Il nome del pulsante comincia con il testo
 * visibile (il titolo breve, o il titolo) e prosegue con il titolo completo
 * se diverso, il video e la durata (titoloModulo), in uno sr-only che resta
 * dentro il pulsante posizionato.
 *
 * `rif` e' il ref della ul che scorre (useFasciaScorrevole nel modulo).
 */
export default function FasciaMiniature({ rif, voci, chiaveEvidenza, cambio = false, scorrevole = true, onScegli }) {
  return (
    <ul ref={rif} id="edunews24-fascia" role="list" className="edunews24-fascia" aria-label={testi.fascia}
      data-scorrevole={scorrevole ? "true" : "false"} data-cambio={cambio ? "si" : "no"}>
      {voci.map((voce) => {
        const chiave = chiaveVoce(voce);
        const titolo = titoloModulo(voce, { conVideo: true });
        const categoria = voce.categoria?.nome ?? null;
        return (
          <li key={chiave}>
            <button type="button" className="edunews24-miniatura edunews24-anello-doppio group"
              aria-pressed={chiave === chiaveEvidenza} aria-controls="edunews24-apertura"
              onClick={() => onScegli(voce)} onFocus={portaInVista}>
              <span className="edunews24-cornice" data-misura="piccola">
                <span className="edunews24-media">
                  <span className="edunews24-media__quadro">
                    <ImmagineArticolo src={voce.immagine} categoria={categoria} campitura="velo"
                      variante={varianteRipiego(voce.id)} larghezza={640} altezza={360} />
                  </span>
                  {haVideo(voce) && <DistintivoVideo durataSecondi={voce.video?.durata_secondi} nascosto />}
                </span>
              </span>
              {categoria && (
                <span className={["edunews24-miniatura__occhiello", occhiello("categoria")].join(" ")}>{categoria}</span>
              )}
              <span className={["edunews24-miniatura__titolo", titoloVoce("miniatura", 2)].join(" ")}>
                {titolo.visibile}
              </span>
              {titolo.aggiunta && <span className="sr-only">{titolo.aggiunta}</span>}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
