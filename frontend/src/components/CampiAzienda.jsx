import {
  campo as classiCampo,
  etichetta as classiEtichetta,
} from "../config/styles/campo";

export const OBBLIGATORI = [
  ["azienda_ragione_sociale", "Ragione sociale"],
  ["azienda_partitaIVA", "Partita IVA"],
  ["azienda_codiceFiscale", "Codice fiscale"],
  ["azienda_via", "Via"],
  ["azienda_citta", "Città"],
  ["azienda_CAP", "CAP"],
  ["azienda_provincia", "Provincia"],
];

export const FACOLTATIVI = [
  ["azienda_civico", "Civico"],
  ["azienda_fatturazioneSDI", "Codice SDI"],
  ["azienda_email", "Email"],
  ["azienda_pec", "PEC"],
  ["azienda_telefono", "Telefono"],
  ["azienda_sitoWeb", "Sito web"],
  ["azienda_iban", "IBAN"],
  ["azienda_codice_bic", "Codice BIC"],
  ["azienda_codice_nazionale", "Codice nazionale"],
];

export const VUOTO_AZIENDA = Object.fromEntries(
  [...OBBLIGATORI, ...FACOLTATIVI].map(([campo]) => [campo, ""]),
);

export default function CampiAzienda({ dati, onChange, disabilita = {} }) {
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
      {FACOLTATIVI.map((c) => campo(c, false))}
    </div>
  );
}
