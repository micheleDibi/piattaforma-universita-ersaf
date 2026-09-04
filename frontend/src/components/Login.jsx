import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { apiFetch, leggiJson } from "../lib/api";
import { pulisciSessione, salvaSessione } from "../lib/sessione";

function messaggioErrore(dati) {
  if (Array.isArray(dati?.detail)) {
    return dati.detail
      .map((errore) => `${errore.loc.join(".")}: ${errore.msg}`)
      .join(", ");
  }
  return typeof dati?.detail === "string" ? dati.detail : "Credenziali non valide";
}

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [avviso, setAvviso] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Catturato una volta sola al montaggio: il banner deve restare finche'
  // l'utente e' su questa pagina, anche dopo che lo stato di navigazione e'
  // stato ripulito.
  const [passwordAggiornata] = useState(
    () => location.state?.passwordAggiornata === true,
  );
  const statoRipulito = useRef(false);

  useEffect(() => {
    if (!passwordAggiornata || statoRipulito.current) return;
    statoRipulito.current = true;
    // Toglie lo stato dalla cronologia: un Indietro non deve rimostrare
    // "Password aggiornata". Il ref regge la doppia esecuzione di StrictMode.
    navigate(location.pathname, { replace: true, state: null });
  }, [passwordAggiornata, navigate, location.pathname]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setAvviso("");
    setLoading(true);
    // Qualunque residuo di una sessione precedente sparisce prima di provarne
    // una nuova: niente utente_id orfano se questo tentativo fallisce.
    pulisciSessione();

    try {
      const risposta = await apiFetch("/auth/login", {
        method: "POST",
        auth: false,
        // Qui un 401 significa "credenziali errate", non "sessione scaduta":
        // reindirizzare cancellerebbe il messaggio che l'utente deve leggere.
        gestisci401: false,
        body: JSON.stringify({
          utente_username: username,
          utente_password: password,
        }),
      });

      // Il corpo puo' non essere JSON (un 502 di un proxy restituisce HTML):
      // la .json() secca mostrava all'utente "Unexpected token <" nel banner.
      const dati = await leggiJson(risposta);

      if (!risposta.ok) {
        throw new Error(messaggioErrore(dati));
      }

      // Il ramo della verifica in due passaggi torna HTTP 200 e SENZA
      // utente_id: prima !response.ok era falso e il codice proseguiva
      // scrivendo la stringa "undefined" in localStorage. Va intercettato
      // prima di qualunque scrittura.
      if (dati?.requires_2fa === true) {
        setAvviso(
          "Il tuo account richiede la verifica in due passaggi, non ancora " +
            "disponibile su questa piattaforma. Contatta il tuo referente ERSAF.",
        );
        return;
      }

      // Contratto minimo: senza token o senza utente_id non si prosegue, invece
      // di navigare verso una pagina che non potrebbe funzionare.
      if (!dati?.token || !dati?.utente_id) {
        throw new Error("Risposta del server non valida. Riprova.");
      }

      // Nessun console.log della risposta: da ora contiene il token di sessione.
      salvaSessione({
        token: dati.token,
        utenteId: dati.utente_id,
        ruoloCodice: dati.ruolo_codice,
      });

      // La vecchia navigate("/nazionale") puntava a una rotta mai registrata,
      // quindi a una pagina bianca — ed era per giunta irraggiungibile: per il
      // ruolo Nazionale il backend esce prima con requires_2fa, quindi
      // ruolo_codice === "nazionale" non poteva mai essere vero. Era codice
      // morto e viene rimosso: destinazione unica, la homepage introdotta da
      // VinMan99.
      navigate("/home");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white px-14 py-5 text-left shadow-xl transition-all border-2 border-blue-900">
          <div className="mb-6 text-center">
            <h5 className="text-2xl  tracking-tight text-blue-900">Accedi</h5>
          </div>

          {passwordAggiornata && (
            <div
              role="status"
              className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700 border border-green-200"
            >
              Password aggiornata. Accedi con le nuove credenziali.
            </div>
          )}

          {avviso && (
            <div
              role="status"
              className="mb-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800 border border-amber-200"
            >
              {avviso}
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="username"
                className="block text-sm  text-blue-900"
              >
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="janesmith"
                className="mt-1 block w-full rounded-full border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm  text-blue-900"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 block w-full rounded-full border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 rounded-full bg-indigo-600 py-2.5 px-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 transition-colors disabled:opacity-50"
            >
              {loading ? "Accesso in corso..." : "Entra"}
            </button>
            <div className="flex items-center justify-center text-sm pt-1">
              <Link
                to="/password-dimenticata"
                className="rounded-full px-1 text-blue-900 underline underline-offset-2 transition-colors hover:text-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                Hai dimenticato la password?
              </Link>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}

export default Login;
