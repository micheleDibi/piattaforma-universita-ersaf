import { useState } from "react";
import { Link } from "react-router";
import { apiFetch } from "../lib/api";
import { campo, etichetta } from "../config/styles/campo";
import { pulsante } from "../config/styles/pulsante";
import { paginaCentrata, scheda } from "../config/styles/superficie";

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
    <div className={paginaCentrata()}>
      <div className={`${scheda()} relative w-full max-w-md transform overflow-hidden px-14 py-5 text-left transition-all`}>
        <div className="mb-6 text-center">
          <h5 className="text-2xl tracking-tight text-testo-forte">
            Password dimenticata
          </h5>
        </div>

        {inviato ? (
          <div
            role="status"
            aria-live="polite"
            className="mb-4 rounded-controllo bg-primario-tenue p-3 text-sm text-testo border border-bordo"
          >
            {MESSAGGIO_GENERICO}
          </div>
        ) : (
          <p className="mb-4 text-sm text-testo-tenue">
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
              className={etichetta()}
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
              className={`${campo()} mt-1 block disabled:bg-superficie-alta disabled:text-testo-tenue`}
            />
          </div>

          <button
            type="submit"
            disabled={invioInCorso || inviato}
            className={`${pulsante("primario", "grande", { larghezzaPiena: true })} mt-2`}
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
              className="text-testo underline underline-offset-2 hover:text-primario"
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
