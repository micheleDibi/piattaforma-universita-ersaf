import { campo, etichetta } from "../../config/styles/campo.js";
import { pulsante } from "../../config/styles/pulsante.js";

export default function CampoContatto({ tipo, valore, onChange, verifica }) {
  const salvato = verifica?.stato?.valore === valore;
  const verificato = salvato && verifica?.stato?.verificato;
  const verificatoIl = verifica?.stato?.verificato_il;
  const titolo = tipo === "email" ? "Email" : "Cellulare";
  return (
    <div className="space-y-2">
      <label htmlFor={`contatto-${tipo}`} className={etichetta()}>
        {titolo}
      </label>
      <div className="flex items-start gap-2">
        <input
          id={`contatto-${tipo}`}
          type={tipo === "email" ? "email" : "tel"}
          name={tipo}
          value={valore}
          onChange={onChange}
          className={`${campo("comodo")} min-w-0 flex-1`}
        />
        {verifica?.disponibile && (
          <button
            type="button"
            disabled={!salvato || !valore || verificato}
            className={pulsante("secondario")}
            onClick={verifica.apri}
          >
            {verificato ? "Verificato" : "Verifica"}
          </button>
        )}
      </div>
      {verificato && verificatoIl && (
        <p className="text-sm text-testo-tenue">
          Verificato il{" "}
          {new Date(verificatoIl).toLocaleDateString("it-IT", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      )}
      {verifica?.disponibile && !salvato && valore && (
        <p className="text-sm text-testo-tenue">
          Salva le modifiche per verificare questo contatto.
        </p>
      )}
    </div>
  );
}
