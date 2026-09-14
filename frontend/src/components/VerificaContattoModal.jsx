import { useEffect, useMemo, useRef, useState } from "react";
import { apiFetch, leggiJson, messaggioErrore } from "../lib/api";

const NUMERO_CIFRE = 6;

function calcolaSecondi(scadenzaIso) {
  if (!scadenzaIso) return 0;
  const diff = Math.floor(
    (new Date(scadenzaIso).getTime() - Date.now()) / 1000,
  );
  return Math.max(diff, 0);
}

function useSecondiRimanenti(scadenzaIso) {
  const [secondi, setSecondi] = useState(() => calcolaSecondi(scadenzaIso));
  useEffect(() => {
    setSecondi(calcolaSecondi(scadenzaIso));
    const id = setInterval(() => setSecondi(calcolaSecondi(scadenzaIso)), 1000);
    return () => clearInterval(id);
  }, [scadenzaIso]);
  return secondi;
}

/** Modale generico di verifica OTP per un contatto (oggi email; cellulare
 * userà lo stesso componente cambiando `tipo` quando sarà pronto). */
function VerificaContattoModal({
  clienteId,
  tipo,
  etichetta,
  onVerificato,
  onChiudi,
}) {
  const [sfida, setSfida] = useState(null); // { logOtpId, scadenza }
  const [cifre, setCifre] = useState(Array(NUMERO_CIFRE).fill(""));
  const [errore, setErrore] = useState("");
  const [avviso, setAvviso] = useState("");
  const [caricando, setCaricando] = useState(true);
  const [verificando, setVerificando] = useState(false);
  const [rigenerando, setRigenerando] = useState(false);
  const inputRefs = useRef([]);
  const avviato = useRef(false);

  const secondiRimanenti = useSecondiRimanenti(sfida?.scadenza);
  const codiceCompleto = useMemo(() => cifre.join(""), [cifre]);

  async function generaOtp(rigenerazione) {
    if (rigenerazione) setRigenerando(true);
    setErrore("");
    try {
      const risposta = await apiFetch(
        `/clienti/${clienteId}/contatti/${tipo}/genera-otp`,
        {
          method: "POST",
        },
      );
      const dati = await leggiJson(risposta);
      if (!risposta.ok)
        throw new Error(
          await messaggioErrore(
            risposta,
            "Non è stato possibile inviare il codice.",
          ),
        );

      setSfida({ logOtpId: dati.log_otp_id, scadenza: dati.otp_scadenza });
      setCifre(Array(NUMERO_CIFRE).fill(""));
      setAvviso(
        rigenerazione
          ? "Nuovo codice inviato."
          : `Codice inviato a ${etichetta}.`,
      );
      inputRefs.current[0]?.focus();
    } catch (err) {
      setErrore(err.message);
    } finally {
      setCaricando(false);
      setRigenerando(false);
    }
  }

  useEffect(() => {
    if (avviato.current) return;
    avviato.current = true;
    generaOtp(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function aggiornaCifra(indice, valore) {
    const pulito = valore.replace(/\D/g, "").slice(-1);
    setCifre((precedenti) => {
      const nuove = [...precedenti];
      nuove[indice] = pulito;
      return nuove;
    });
    if (pulito && indice < NUMERO_CIFRE - 1)
      inputRefs.current[indice + 1]?.focus();
  }

  function gestisciTastoIndietro(indice, e) {
    if (e.key === "Backspace" && !cifre[indice] && indice > 0) {
      inputRefs.current[indice - 1]?.focus();
    }
  }

  async function verifica() {
    setErrore("");
    setAvviso("");
    if (codiceCompleto.length !== NUMERO_CIFRE) {
      setErrore("Inserisci tutte le 6 cifre del codice.");
      return;
    }
    setVerificando(true);
    try {
      const risposta = await apiFetch(
        `/clienti/${clienteId}/contatti/${tipo}/verifica-otp`,
        {
          method: "POST",
          gestisci401: false,
          body: JSON.stringify({
            log_otp_id: sfida.logOtpId,
            otp_codice: codiceCompleto,
          }),
        },
      );
      const dati = await leggiJson(risposta);
      if (!risposta.ok)
        throw new Error(
          await messaggioErrore(risposta, "Codice OTP non valido."),
        );

      onVerificato(dati);
    } catch (err) {
      setErrore(err.message);
      setCifre(Array(NUMERO_CIFRE).fill(""));
      inputRefs.current[0]?.focus();
    } finally {
      setVerificando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="relative w-full max-w-md overflow-hidden rounded-2xl bg-white px-8 py-8 text-left shadow-xl border-2 border-blue-900">
        <div className="mb-6 text-center">
          <h5 className="text-2xl tracking-tight text-blue-900">
            Verifica {etichetta}
          </h5>
          <p className="mt-2 text-sm text-gray-600">
            {caricando
              ? "Invio del codice in corso..."
              : `Abbiamo inviato un codice a ${etichetta}.`}
          </p>
        </div>

        {avviso && (
          <div
            role="status"
            className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700 border border-green-200"
          >
            {avviso}
          </div>
        )}
        {errore && (
          <div
            role="alert"
            className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200"
          >
            {errore}
          </div>
        )}

        {!caricando && sfida && (
          <div className="space-y-4">
            <div className="flex justify-center gap-2">
              {cifre.map((cifra, indice) => (
                <input
                  key={indice}
                  ref={(el) => (inputRefs.current[indice] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={cifra}
                  onChange={(e) => aggiornaCifra(indice, e.target.value)}
                  onKeyDown={(e) => {
                    gestisciTastoIndietro(indice, e);
                    // Invio dall'ultimo campo verifica direttamente, comodo da
                    // tastiera visto che non c'e' piu' un form da sottomettere.
                    if (
                      e.key === "Enter" &&
                      codiceCompleto.length === NUMERO_CIFRE
                    ) {
                      verifica();
                    }
                  }}
                  className="h-12 w-10 rounded-lg border border-gray-300 text-center text-lg text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              ))}
            </div>

            <p className="text-center text-sm text-gray-500">
              {secondiRimanenti > 0
                ? `Il codice scade tra ${Math.floor(secondiRimanenti / 60)}:${String(secondiRimanenti % 60).padStart(2, "0")}`
                : "Il codice è scaduto: richiedine uno nuovo."}
            </p>

            <button
              type="button"
              onClick={verifica}
              disabled={verificando || codiceCompleto.length !== NUMERO_CIFRE}
              className="w-full rounded-full bg-indigo-600 py-2.5 px-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 transition-colors disabled:opacity-50"
            >
              {verificando ? "Verifica in corso..." : "Verifica"}
            </button>

            <button
              type="button"
              onClick={() => generaOtp(true)}
              disabled={rigenerando}
              className="w-full rounded-full border border-blue-900 py-2 px-4 text-sm font-semibold text-blue-900 hover:bg-blue-50 transition-colors disabled:opacity-50"
            >
              {rigenerando ? "Invio in corso..." : "Invia di nuovo il codice"}
            </button>
          </div>
        )}

        <button
          type="button"
          onClick={onChiudi}
          className="w-full mt-4 text-center text-sm text-gray-500 underline underline-offset-2 hover:text-indigo-600"
        >
          Chiudi
        </button>
      </div>
    </div>
  );
}

export default VerificaContattoModal;
