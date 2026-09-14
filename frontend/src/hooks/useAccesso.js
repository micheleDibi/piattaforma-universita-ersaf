import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router";
import { accedi } from "../lib/accesso.js";
import { destinazioneDopoAccesso } from "../lib/ritornoAccesso.js";
import { ROTTA_INIZIALE } from "../config/routes/rotte.js";

export function useAccesso() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [avviso, setAvviso] = useState("");
  const [loading, setLoading] = useState(false);
  const [attesa, setAttesa] = useState(0);
  const [limiteRaggiunto, setLimiteRaggiunto] = useState(false);
  const invio = useRef(false);
  const navigate = useNavigate();
  const bloccato = attesa > 0;

  useEffect(() => {
    if (!bloccato) return undefined;
    const timer = setInterval(() => setAttesa((n) => Math.max(0, n - 1)), 1000);
    return () => clearInterval(timer);
  }, [bloccato]);

  const handleSubmit = async (evento) => {
    evento.preventDefault();
    if (invio.current || bloccato) return;
    invio.current = true;
    setLoading(true);
    setError("");
    setAvviso("");
    setLimiteRaggiunto(false);
    try {
      if (await accedi(username, password)) {
        setPassword("");
        navigate(destinazioneDopoAccesso(ROTTA_INIZIALE), { replace: true });
      } else {
        setAvviso("Il tuo account richiede la verifica in due passaggi, non ancora disponibile su questa piattaforma. Contatta il tuo referente ERSAF.");
      }
    } catch (errore) {
      setLimiteRaggiunto(errore.stato === 429);
      setError(errore.stato === 429 ? "Troppi tentativi di accesso. Attendi prima di riprovare." : errore.message);
      setAttesa(errore.attesaSecondi || 0);
    } finally {
      invio.current = false;
      setLoading(false);
    }
  };

  return { username, setUsername, password, setPassword, error, avviso, loading, attesa, limiteRaggiunto, handleSubmit };
}
