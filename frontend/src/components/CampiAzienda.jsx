import {
  campo as classiCampo,
  erroreCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";
import { FACOLTATIVI, OBBLIGATORI } from "../config/campiAzienda.js";

const ETICHETTE = Object.fromEntries([...OBBLIGATORI, ...FACOLTATIVI]);
const OBBLIGATORIO = new Set(OBBLIGATORI.map(([nome]) => nome));

// Classi statiche perche' Tailwind non vede quelle composte a runtime.
const SPAN = {
  1: "col-span-6 sm:col-span-1",
  2: "col-span-6 sm:col-span-2",
  3: "col-span-6 sm:col-span-3",
  4: "col-span-6 sm:col-span-4",
  5: "col-span-6 sm:col-span-5",
  6: "col-span-6",
};

/**
 * Campi del modulo azienda. Senza `gruppo` mostra tutti i campi su due
 * colonne; con `gruppo` ([nome, colonne su 6]) solo quelli indicati, pensati
 * per la griglia di SezioneModulo.
 */
export default function CampiAzienda({
  dati,
  onChange,
  disabilita = {},
  nascondi = {},
  gruppo,
}) {
  const campo = (nome, colonne) => {
    const etichetta = ETICHETTE[nome];
    const obbligatorio = OBBLIGATORIO.has(nome);
    const isPartitaIVA = nome === "azienda_partitaIVA";
    const pivaNonConforme =
      isPartitaIVA && dati[nome] !== "" && !/^\d{11}$/.test(dati[nome]);
    return (
      <div
        key={nome}
        className={colonne ? `flex flex-col ${SPAN[colonne]}` : "flex flex-col"}
      >
        <label htmlFor={nome} className={classiEtichetta()}>
          {etichetta.toUpperCase()}
          {obbligatorio && <span className="text-negativo"> *</span>}
        </label>
        <input
          id={nome}
          name={nome}
          type="text"
          required={obbligatorio}
          disabled={Boolean(disabilita[nome])}
          value={dati[nome]}
          onChange={onChange}
          maxLength={isPartitaIVA ? 11 : undefined}
          inputMode={isPartitaIVA ? "numeric" : undefined}
          pattern={isPartitaIVA ? "[0-9]*" : undefined}
          aria-invalid={pivaNonConforme || undefined}
          aria-describedby={pivaNonConforme ? `${nome}-nota` : undefined}
          className={classiCampo("comodo", { errore: pivaNonConforme })}
        />
        {pivaNonConforme && (
          <p id={`${nome}-nota`} className={erroreCampo()}>
            Deve contenere 11 cifre numeriche
          </p>
        )}
      </div>
    );
  };

  if (gruppo)
    return gruppo
      .filter(([nome]) => !nascondi[nome])
      .map(([nome, colonne]) => campo(nome, colonne));

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      {OBBLIGATORI.map(([nome]) => campo(nome))}
      {FACOLTATIVI.filter(([nome]) => !nascondi[nome]).map(([nome]) =>
        campo(nome),
      )}
    </div>
  );
}
