import { campo as classiCampo } from "../config/styles/campo";
import { STILI_AZIENDA as stili } from "../config/styles/azienda.js";
import { TESTI_AZIENDA } from "../config/testi/azienda.js";
import {
  FACOLTATIVI,
  OBBLIGATORI,
  PROPRIETA_CAMPI,
} from "../config/campiAzienda.js";
import { noteCampiAzienda, pivaNonConforme } from "../lib/schedaAzienda.js";
import CampoModulo from "./shared/CampoModulo.jsx";

const OBBLIGATORIO = new Set(OBBLIGATORI);

/**
 * Campi del modulo azienda. Con `gruppo` ([nome, colonne su 6]) mostra solo
 * quelli indicati, dentro la griglia di SezioneModulo; senza `gruppo` mostra
 * tutti i campi, due per riga (finestra di creazione rapida), salvo quelli
 * con `colonneFinestra` in PROPRIETA_CAMPI (IBAN e BIC).
 *
 * Le note sotto i campi sono avvisi: le anomalie del server sui campi non
 * ancora modificati (`anomalie`, confrontate con i valori `salvati`) e il
 * controllo in tempo reale della partita IVA.
 *
 * @param {{
 *   dati: Record<string, string>,
 *   onChange: (evento: Event) => void,
 *   anomalie?: string[],
 *   salvati?: Record<string, string>,
 *   soloLettura?: Record<string, boolean>,
 *   nascondi?: Record<string, boolean>,
 *   gruppo?: [string, number][],
 * }} props
 *   soloLettura: campi bloccati oltre al codice nazionale (la partita IVA
 *   cercata, nella creazione rapida).
 */
export default function CampiAzienda({
  dati,
  onChange,
  anomalie,
  salvati,
  soloLettura = {},
  nascondi = {},
  gruppo,
}) {
  const note = noteCampiAzienda(anomalie, dati, salvati ?? dati);

  const campo = (nome, colonne) => {
    const proprieta = PROPRIETA_CAMPI[nome] ?? {};
    const obbligatorio = OBBLIGATORIO.has(nome);
    const noteCampo = note[nome] ?? [];
    const conNota = noteCampo.length > 0;
    const classi = classiCampo("comodo", { avviso: conNota, fuocoAvviso: "ambra" });
    return (
      <CampoModulo
        key={nome}
        per={nome}
        etichetta={TESTI_AZIENDA.campi[nome]}
        obbligatorio={obbligatorio}
        colonne={colonne}
        nota={noteCampo}
        tonoNota="avviso"
      >
        <input
          id={nome}
          name={nome}
          type="text"
          required={obbligatorio}
          readOnly={Boolean(proprieta.solaLettura || soloLettura[nome])}
          value={dati[nome]}
          onChange={onChange}
          placeholder={TESTI_AZIENDA.segnaposti[nome]}
          {...proprieta.input}
          aria-invalid={
            (nome === "azienda_partitaIVA" && pivaNonConforme(dati[nome])) ||
            undefined
          }
          aria-describedby={conNota ? `${nome}-nota` : undefined}
          className={
            proprieta.monospazio ? `${classi} ${stili.monospazio}` : classi
          }
        />
      </CampoModulo>
    );
  };

  if (gruppo)
    return gruppo
      .filter(([nome]) => !nascondi[nome])
      .map(([nome, colonne]) => campo(nome, colonne));

  return (
    <div className={stili.grigliaFinestra}>
      {[...OBBLIGATORI, ...FACOLTATIVI]
        .filter((nome) => !nascondi[nome])
        .map((nome) => campo(nome, PROPRIETA_CAMPI[nome]?.colonneFinestra ?? 3))}
    </div>
  );
}
