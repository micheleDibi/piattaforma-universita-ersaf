import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { apiFetch, leggiJson } from "../lib/api";
import { leggiTokenDallUrl, ripulisciUrlDalToken } from "../lib/resetToken";
import { regoleDaCodiciServer, robustezza, valutaPassword } from "../lib/passwordPolicy";

const SIMBOLO = { ok: "✓", ko: "✕", neutro: "•", non_verificabile: "•" };
const COLORE = {
  ok: "text-green-600",
  ko: "text-red-600",
  neutro: "text-gray-300",
  non_verificabile: "text-gray-300",
};
const LETTURA = {
  ok: "requisito soddisfatto",
  ko: "requisito non soddisfatto",
  neutro: "requisito da soddisfare",
  non_verificabile: "verificato al salvataggio",
};

// Qui distinguere i motivi non e' un oracolo: chi apre questa pagina ha gia' il
// link in mano, non c'e' nulla da enumerare. Sapere che e' scaduto invece di un
// generico "non valido" evita una richiesta di assistenza.
const MOTIVI = {
  scaduto: "Il link è scaduto: era valido per 60 minuti dalla richiesta.",
  gia_usato: "Questo link è già stato usato: la password è già stata cambiata.",
  non_valido:
    "Il link non è valido. Può essere stato copiato male, oppure una richiesta più recente lo ha sostituito.",
  rete: "Non è stato possibile verificare il link. Controlla la connessione e riprova.",
};

const COLORI_BARRA = [
  "bg-red-500",
  "bg-red-400",
  "bg-amber-400",
  "bg-lime-500",
  "bg-green-600",
];

// Non esportato: eslint-plugin-react-refresh segnala i file che esportano sia
// componenti sia altro, e un guscio usato in tre rami dello stesso file non
// giustifica un modulo separato.
function Guscio({ titolo, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white px-14 py-5 text-left shadow-xl transition-all border-2 border-blue-900">
        <div className="mb-6 text-center">
          <h5 className="text-2xl tracking-tight text-blue-900">{titolo}</h5>
        </div>
        {children}
      </div>
    </div>
  );
}

function ReimpostaPassword() {
  const navigate = useNavigate();

  // Memoizzato a livello di modulo: la doppia invocazione dell'initializer
  // sotto StrictMode restituisce lo stesso valore anche dopo che l'effetto
  // qui sotto ha ripulito l'URL.
  const [token] = useState(() => leggiTokenDallUrl());

  // Lo stato iniziale dipende gia' dal token: cosi' l'effetto non deve
  // chiamare setState in modo sincrono per il caso "token assente", che
  // provocherebbe un rendering a cascata.
  const [stato, setStato] = useState(() =>
    leggiTokenDallUrl() ? "verifica" : "non_valido",
  ); // verifica | valido | non_valido
  const [motivo, setMotivo] = useState("non_valido");
  const [password, setPassword] = useState("");
  const [conferma, setConferma] = useState("");
  const [invioInCorso, setInvioInCorso] = useState(false);
  const [errore, setErrore] = useState("");
  const [regoleRifiutate, setRegoleRifiutate] = useState([]);
  const [annuncio, setAnnuncio] = useState("");

  useEffect(() => {
    ripulisciUrlDalToken();
  }, []);

  useEffect(() => {
    if (!token) return; // lo stato iniziale e' gia' "non_valido"
    let annullato = false;

    (async () => {
      try {
        // validate e' in sola lettura e non marca nulla: la doppia chiamata di
        // StrictMode non brucia il token, esattamente come non lo brucia il
        // prefetch di un client di posta.
        const risposta = await apiFetch(
          `/auth/password-reset/validate?token=${encodeURIComponent(token)}`,
          { auth: false, gestisci401: false },
        );
        const dati = await leggiJson(risposta);
        if (annullato) return;

        if (dati?.valido === true) {
          setStato("valido");
        } else {
          setStato("non_valido");
          setMotivo(dati?.motivo ?? "non_valido");
        }
      } catch {
        if (annullato) return;
        setStato("non_valido");
        setMotivo("rete");
      }
    })();

    return () => {
      annullato = true;
    };
  }, [token]);

  // Un aria-live su ogni riga dell'elenco sarebbe illeggibile con uno screen
  // reader: annuncerebbe a ogni battitura. Si annuncia un riepilogo, una volta
  // sola, dopo una pausa.
  useEffect(() => {
    const attesa = setTimeout(() => {
      if (password === "") {
        setAnnuncio("");
        return;
      }
      const { regole } = valutaPassword(password);
      const verificabili = regole.filter((r) => r.stato !== "non_verificabile");
      const soddisfatte = verificabili.filter((r) => r.stato === "ok").length;
      setAnnuncio(
        `${soddisfatte} requisiti su ${verificabili.length} soddisfatti. Robustezza: ${robustezza(password).etichetta}.`,
      );
    }, 700);
    return () => clearTimeout(attesa);
  }, [password]);

  // Niente useMemo: il compilatore React e' attivo e queste funzioni scorrono
  // quattro elementi.
  const { regole, valida } = valutaPassword(password);
  const forza = robustezza(password);
  const coincidono = conferma !== "" && password === conferma;
  const puoInviare = valida && coincidono && !invioInCorso;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!puoInviare) return;
    setErrore("");
    setRegoleRifiutate([]);
    setInvioInCorso(true);

    try {
      const risposta = await apiFetch("/auth/password-reset/confirm", {
        method: "POST",
        auth: false,
        gestisci401: false,
        body: JSON.stringify({
          token,
          password,
          password_conferma: conferma,
        }),
      });

      if (!risposta.ok) {
        const dati = await leggiJson(risposta);
        const dettaglio = dati?.detail;
        if (dettaglio?.regole_violate) {
          setRegoleRifiutate(regoleDaCodiciServer(dettaglio.regole_violate));
        }
        setErrore(
          dettaglio?.messaggi?.join(" ") ??
            (typeof dettaglio === "string"
              ? dettaglio
              : "Non è stato possibile cambiare la password. Richiedi un nuovo link."),
        );
        setInvioInCorso(false);
        return;
      }

      // Il banner di conferma viaggia nello stato della navigazione: l'URL
      // resta pulito e un link copiato a un collega non gli mostra un
      // "Password aggiornata" che non lo riguarda.
      navigate("/", { replace: true, state: { passwordAggiornata: true } });
    } catch {
      setErrore("Connessione non riuscita. Riprova.");
      setInvioInCorso(false);
    }
  };

  if (stato === "verifica") {
    return (
      <Guscio titolo="Reimposta la password">
        <p role="status" aria-live="polite" className="text-sm text-gray-600">
          Verifica del link in corso...
        </p>
      </Guscio>
    );
  }

  // Nessun form, in nessuna forma, quando il token non e' valido. Il return
  // anticipato e' la garanzia strutturale: non c'e' un ramo di JSX piu' sotto
  // che possa disegnarlo per sbaglio.
  if (stato === "non_valido") {
    return (
      <Guscio titolo="Link non valido">
        <div
          role="alert"
          className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200"
        >
          {MOTIVI[motivo] ?? MOTIVI.non_valido}
        </div>
        <p className="mb-4 text-sm text-gray-600">
          Puoi richiedere un nuovo link: quello precedente verrà annullato. Se
          hai ricaricato questa pagina, riapri il link dalla mail — per
          sicurezza non viene conservato.
        </p>
        <div className="flex flex-col items-center gap-2 text-sm">
          <Link
            to="/password-dimenticata"
            className="w-full text-center rounded-full bg-indigo-600 py-2.5 px-4 font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
          >
            Richiedi un nuovo link
          </Link>
          <Link
            to="/"
            className="text-blue-900 underline underline-offset-2 hover:text-indigo-600"
          >
            Torna al login
          </Link>
        </div>
      </Guscio>
    );
  }

  return (
    <Guscio titolo="Reimposta la password">
      {errore && (
        <div
          role="alert"
          className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200"
        >
          {errore}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <label htmlFor="nuova-password" className="block text-sm text-blue-900">
            Nuova password
          </label>
          <input
            id="nuova-password"
            name="nuova-password"
            type="password"
            autoComplete="new-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-describedby="regole-password"
            className="mt-1 block w-full rounded-full border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        {/* Indicatore indicativo: non blocca mai l'invio. */}
        <div>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Robustezza</span>
            <span>{forza.etichetta}</span>
          </div>
          <div className="mt-1 h-1.5 w-full rounded-full bg-gray-200 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${COLORI_BARRA[forza.livello]}`}
              style={{ width: `${(forza.livello / 4) * 100}%` }}
            />
          </div>
        </div>

        <ul id="regole-password" className="space-y-1">
          {regole.map((regola) => {
            const stato =
              regoleRifiutate.includes(regola.id) && regola.stato !== "ok"
                ? "ko"
                : regola.stato;
            return (
              <li key={regola.id} className="flex items-start gap-2 text-sm">
                <span aria-hidden="true" className={`leading-5 ${COLORE[stato]}`}>
                  {SIMBOLO[stato]}
                </span>
                <span className={stato === "ko" ? "text-red-600" : "text-gray-600"}>
                  {regola.testo}
                  {stato === "non_verificabile" && (
                    <span className="text-gray-400"> — verificata al salvataggio</span>
                  )}
                  <span className="sr-only">: {LETTURA[stato]}</span>
                </span>
              </li>
            );
          })}
        </ul>

        <div>
          <label htmlFor="conferma-password" className="block text-sm text-blue-900">
            Conferma password
          </label>
          <input
            id="conferma-password"
            name="conferma-password"
            type="password"
            autoComplete="new-password"
            required
            value={conferma}
            onChange={(e) => setConferma(e.target.value)}
            aria-invalid={conferma !== "" && !coincidono}
            aria-describedby="esito-conferma"
            className={`mt-1 block w-full rounded-full border px-3 py-2 text-gray-900 shadow-sm focus:outline-none focus:ring-1 sm:text-sm ${
              conferma !== "" && !coincidono
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:border-indigo-500 focus:ring-indigo-500"
            }`}
          />
          {/* Lo spazio unificatore tiene l'altezza costante: senza, il pulsante
              saltella mentre si digita. */}
          <p
            id="esito-conferma"
            className={`mt-1 text-sm ${coincidono ? "text-green-600" : "text-red-600"}`}
          >
            {conferma === ""
              ? " "
              : coincidono
                ? "✓ Le password coincidono"
                : "✕ Le password non coincidono"}
          </p>
        </div>

        <button
          type="submit"
          disabled={!puoInviare}
          className="w-full mt-2 rounded-full bg-indigo-600 py-2.5 px-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 transition-colors disabled:opacity-50"
        >
          {invioInCorso ? "Salvataggio..." : "Salva la nuova password"}
        </button>

        <div className="flex items-center justify-center text-sm pt-1">
          <Link
            to="/"
            className="text-blue-900 underline underline-offset-2 hover:text-indigo-600"
          >
            Torna al login
          </Link>
        </div>
      </form>

      {/* Unica regione annunciata: un riepilogo, non quattro righe che cambiano
          a ogni battitura. */}
      <p aria-live="polite" className="sr-only">
        {annuncio}
      </p>
    </Guscio>
  );
}

export default ReimpostaPassword;
