import { useId } from "react";
import { ChevronRight, Check, ICONE_CAMPI_ELENCO } from "../../config/icone.js";
import AvvisoTooltip from "./AvvisoTooltip.jsx";
import IndicatoriStato from "./IndicatoriStato.jsx";
import { campoIndicatori, idIndicatori } from "../../lib/righeElenco.js";
import { TESTI_ELENCO } from "../../config/testi/elenco.js";

const RILIEVI_TECNICI = ["codice", "stato", "indicatori"];
const vuoto = (valore) =>
  Array.isArray(valore) ? valore.length === 0 : !valore || valore === "-";

export default function ListaElenco({ dati, modello, onApri }) {
  const base = useId();
  const indicatori = campoIndicatori(modello.mobile);
  const campoPrincipale =
    modello.mobile.find((c) => ["principale", "persona"].includes(c.rilievo)) ||
    modello.mobile[0];
  const campiTecnici = modello.mobile.filter(
    (c) => c.id !== campoPrincipale?.id && RILIEVI_TECNICI.includes(c.rilievo),
  );
  const campiMetadati = modello.mobile.filter(
    (c) => c.id !== campoPrincipale?.id && !RILIEVI_TECNICI.includes(c.rilievo),
  );

  return (
    <ul
      className="elenco-adattivo__lista"
      aria-label={modello.etichetta}
      role="list"
    >
      {dati.map((riga) => (
        <li
          key={riga.id}
          onClick={() => onApri(riga.id)}
          onKeyDown={(evento) => {
            if (evento.key === "Enter" || evento.key === " ") {
              evento.preventDefault();
              onApri(riga.id);
            }
          }}
          tabIndex={0}
          role="button"
          aria-label={TESTI_ELENCO.visualizza(riga.nomeAzione)}
          aria-describedby={idIndicatori(base, riga, indicatori)}
        >
          <dl className="elenco-adattivo__corpo">
            {campoPrincipale &&
              (() => {
                const valoreGrezzo = riga.campi[campoPrincipale.id];
                const valoreMostrato =
                  valoreGrezzo && valoreGrezzo !== "-"
                    ? valoreGrezzo
                    : modello.id === "pratiche"
                      ? TESTI_ELENCO.praticaSenzaNumero(riga.id)
                      : riga.nomeAzione && riga.nomeAzione !== "-"
                        ? riga.nomeAzione
                        : TESTI_ELENCO.elementoSenzaNome;
                const avviso = riga.campi.avviso;
                return (
                  <div className="elenco-adattivo__principale">
                    <dt className="sr-only">{campoPrincipale.etichetta}</dt>
                    {campoPrincipale.rilievo === "persona" && riga.iniziali && (
                      <span className="elenco-adattivo__iniziali" aria-hidden="true">
                        {riga.iniziali}
                      </span>
                    )}
                    <dd className="elenco-adattivo__valore-principale">
                      {valoreMostrato}
                    </dd>
                    {avviso?.length > 0 && <AvvisoTooltip messaggi={avviso} />}
                  </div>
                );
              })()}

            {campiTecnici.length > 0 && (
              <div className="elenco-adattivo__fascia-tecnica">
                {campiTecnici.map((campo) => {
                  const valore = riga.campi[campo.id];
                  if (vuoto(valore)) return null;
                  return (
                    <div
                      key={campo.id}
                      className="elenco-adattivo__tecnico-item"
                    >
                      <dt className="sr-only">{campo.etichetta}</dt>
                      {campo.rilievo === "indicatori" ? (
                        <dd>
                          <IndicatoriStato
                            indicatori={valore}
                            id={idIndicatori(base, riga, indicatori)}
                          />
                        </dd>
                      ) : campo.rilievo === "stato" ? (
                        <dd
                          className="elenco-adattivo__badge"
                          data-tono={riga.tonoStato}
                        >
                          {campo.puntino !== false ? (
                            <span
                              className="elenco-adattivo__badge-punto"
                              aria-hidden="true"
                            />
                          ) : (
                            riga.tonoStato === "positivo" && (
                              <Check className="elenco-adattivo__badge-spunta" />
                            )
                          )}
                          <span>{valore}</span>
                        </dd>
                      ) : (
                        <dd className="elenco-adattivo__codice">{valore}</dd>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {campiMetadati.length > 0 && (
              <div className="elenco-adattivo__metadati">
                {campiMetadati.map((campo) => {
                  const valore = riga.campi[campo.id];
                  if (vuoto(valore)) return null;
                  const Icona = campo.icona
                    ? ICONE_CAMPI_ELENCO[campo.icona]
                    : null;
                  return (
                    <div key={campo.id} className="elenco-adattivo__metadato">
                      <dt className="sr-only">{campo.etichetta}</dt>
                      {Icona && (
                        <Icona
                          className="elenco-adattivo__metadato-icona"
                          aria-hidden="true"
                        />
                      )}
                      <dd className="elenco-adattivo__metadato-testo">
                        {valore}
                      </dd>
                    </div>
                  );
                })}
              </div>
            )}
          </dl>
          <div className="elenco-adattivo__azione-mobile" aria-hidden="true">
            <ChevronRight className="elenco-adattivo__chevron" />
          </div>
        </li>
      ))}
    </ul>
  );
}
