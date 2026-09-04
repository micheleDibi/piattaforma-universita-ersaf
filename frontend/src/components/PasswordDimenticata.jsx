import { useState } from "react";
import { Link } from "react-router";
import { apiFetch } from "../lib/api";

// Identico al messaggio del backend. Se il server e' irraggiungibile l'utente
// deve leggere ESATTAMENTE la stessa frase: prenderla dalla risposta
// significherebbe non averla proprio quando la risposta non arriva.
const MESSAGGIO_GENERICO =
  "Se l'indirizzo è associato a un account riceverai una mail";

function PasswordDimenticata() {
  const [email, setEmail] = useState("");
  const [invioInCorso, setInvioInCorso] = useState(false);
  const [inviato, setInviato] = useState(false);
  // In questa pagina NON esiste uno stato di errore, ed e' deliberato: un ramo
  // visibile che compare solo in certi casi e' esso stesso un oracolo su quali
  // indirizzi esistono.

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (inviato || invioInCorso) return;
    setInvioInCorso(true);

    try {
      // Non si guarda response.ok e non si legge il corpo: 200, 500, DNS
      // fallito, offline e CORS bloccato devono produrre lo stesso schermo.
      await apiFetch("/auth/password-reset/request", {
        method: "POST",
        auth: false,
        gestisci401: false,
        body: JSON.stringify({ email }),
      });
    } catch {
      // Volutamente vuoto, e volutamente senza console: l'indirizzo e' un dato
      // personale e non va nei log del browser.
    } finally {
      // L'unico punto attraversato sia dal successo sia dal fallimento.
      setInviato(true);
      setInvioInCorso(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white px-14 py-5 text-left shadow-xl transition-all border-2 border-blue-900">
        <div className="mb-6 text-center">
          <h5 className="text-2xl tracking-tight text-blue-900">
            Password dimenticata
          </h5>
        </div>

        {inviato ? (
          <div
            role="status"
            aria-live="polite"
            className="mb-4 rounded-lg bg-blue-50 p-3 text-sm text-blue-800 border border-blue-200"
          >
            {MESSAGGIO_GENERICO}
          </div>
        ) : (
          <p className="mb-4 text-sm text-gray-600">
            Inserisci l'indirizzo email associato al tuo account: riceverai un
            link per reimpostare la password. Il link scade dopo 60 minuti e
            può essere usato una sola volta.
          </p>
        )}

        {/* noValidate: senza, il browser blocca l'invio di un indirizzo
            malformato e la pagina resta con il pulsante attivo — proprio
            l'oracolo che si sta evitando. Il server si aspetta di ricevere
            anche gli indirizzi malformati e di trattarli come sconosciuti.
            type="email" resta per la tastiera dei dispositivi mobili. */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div>
            <label
              htmlFor="email-recupero"
              className="block text-sm text-blue-900"
            >
              Email
            </label>
            <input
              id="email-recupero"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              disabled={inviato}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="nome@esempio.it"
              className="mt-1 block w-full rounded-full border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-500 sm:text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={invioInCorso || inviato}
            className="w-full mt-2 rounded-full bg-indigo-600 py-2.5 px-4 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 transition-colors disabled:opacity-50"
          >
            {invioInCorso
              ? "Invio in corso..."
              : inviato
                ? "Richiesta inviata"
                : "Invia"}
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
      </div>
    </div>
  );
}

export default PasswordDimenticata;
