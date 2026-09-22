import {
  campo as classiCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";
import { FACOLTATIVI, OBBLIGATORI } from "../config/campiAzienda.js";

export default function CampiAzienda({
  dati,
  onChange,
  disabilita = {},
  nascondi = {},
}) {
  const campo = ([nome, etichetta], obbligatorio) => {
    const isPartitaIVA = nome === "azienda_partitaIVA";
    return (
      <div key={nome} className="flex flex-col">
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
          className={classiCampo("comodo")}
        />
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      {OBBLIGATORI.map((c) => campo(c, true))}
      {FACOLTATIVI.filter(([nome]) => !nascondi[nome]).map((c) => campo(c, false))}
    </div>
  );
}
