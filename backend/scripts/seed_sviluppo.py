"""Popola il database di SVILUPPO con i casi che il recupero password deve
distinguere, cosi' si possono provare a mano senza scrivere SQL.

    cd backend && .venv/bin/python scripts/seed_sviluppo.py

NON e' uno script di migrazione e non tocca nessuna riga esistente: cancella e
ricrea solo le righe che ha creato lui, riconoscibili dal suffisso `.prova`.

Rifiuta di partire se il nome del database non contiene "dev" o "test": e' la
sola cosa che impedisce di eseguirlo per sbaglio contro `admin_entedb`.

Le password in chiaro qui sotto sono deliberate: servono a provare il rehash
pigro, cioe' la conversione della singola riga al primo accesso riuscito.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.main  # noqa: F401  registra tutti i mapper
from sqlalchemy import delete, select
from src.clienti.models import Cliente
from src.database import SessionLocal, engine
from src.security.password import hash_password
from src.utenti.models import Utente

SUFFISSO = ".prova"
PASSWORD_LEGACY = "vecchia-password-in-chiaro"
PASSWORD_BCRYPT = "cavallo-batteria-graffetta"

# username, email, ruolo, attivo, in chiaro?, nome, a cosa serve
CASI = [
    ("attuatore.prova", "attuatore@example.org", 1, -1, True, "Giulia",
     "attuatore attivo con password legacy: prova il rehash pigro e il reset"),
    ("regionale.prova", "regionale@example.org", 2, -1, False, "Marco",
     "attuatore attivo gia' su bcrypt"),
    ("sottoscrittore.prova", "sottoscrittore@example.org", 0, -1, False, "Anna",
     "ruolo non abilitato: nessuna mail"),
    ("consulente.prova", "consulente@example.org", 4, -1, False, "Luca",
     "come i sottoscrittori: nessuna mail"),
    ("spento.prova", "spento@example.org", 3, 0, False, "Paolo",
     "attuatore disattivato: nessuna mail, e non puo' fare login"),
    ("ambiguo.uno.prova", "condivisa@example.org", 1, -1, False, "Elena",
     "email condivisa fra due attuatori: richiesta ambigua"),
    ("ambiguo.due.prova", "condivisa@example.org", 3, -1, False, "Sara",
     "il gemello del caso ambiguo"),
    ("nazionale.prova", "nazionale@example.org", 5, -1, False, "Chiara",
     "ruolo Nazionale: il login esce con requires_2fa"),
    ("omonimo.prova", "omonimo.uno@example.org", 1, -1, False, "Davide",
     "username duplicato: il login rifiuta"),
    ("omonimo.prova", "omonimo.due@example.org", 1, -1, False, "Fabio",
     "il gemello del caso omonimo"),
]

ORFANO = ("orfano.prova", -1, "utente senza riga clienti: login 401, non 500")


def main() -> None:
    nome = engine.url.database or ""
    if not any(parola in nome.lower() for parola in ("dev", "test")):
        sys.exit(
            f"Rifiuto di scrivere sul database '{nome}': il nome non contiene "
            "'dev' ne' 'test'. Questo script e' solo per lo sviluppo."
        )

    db = SessionLocal()
    try:
        # Ripulisce SOLO le righe create da questo script.
        vecchi = db.execute(
            select(Utente.utente_id).where(Utente.utente_username.like(f"%{SUFFISSO}"))
        ).scalars().all()
        if vecchi:
            db.execute(delete(Cliente).where(Cliente.utente_id.in_(vecchi)))
            db.execute(delete(Utente).where(Utente.utente_id.in_(vecchi)))
            db.commit()
            print(f"rimosse {len(vecchi)} righe di prova precedenti\n")

        larghezza = max(len(c[0]) for c in CASI)
        for username, email, ruolo, attivo, in_chiaro, nome_cliente, scopo in CASI:
            utente = Utente(
                utente_username=username,
                utente_password=PASSWORD_LEGACY if in_chiaro else "",
                utente_password_hash=None if in_chiaro else hash_password(PASSWORD_BCRYPT),
                utente_password_algo="legacy_plaintext" if in_chiaro else "bcrypt",
                utente_attivoSN=attivo,
                utente_padre=None,
                utente_created_by=None,
                utente_updated_by=None,
            )
            db.add(utente)
            db.flush()
            db.add(
                Cliente(
                    cliente_codice=f"COD{utente.utente_id:06d}",
                    cliente_nome=nome_cliente,
                    cliente_cognome="Prova",
                    cliente_email=email,
                    cliente_telefono="",
                    cliente_indirizzo="",
                    cliente_civico="",
                    cliente_citta="",
                    cliente_CAP="",
                    cliente_provincia="",
                    cliente_cellulare="",
                    utente_id=utente.utente_id,
                    cliente_luogoNascita="",
                    cliente_provinciaNascita="",
                    cliente_dataNascita="1999-12-31",
                    cliente_cittadinanza="",
                    cliente_tipoDocumento="",
                    cliente_documento="",
                    cliente_comuneRilascio="",
                    cliente_dataRilascio="1999-12-31",
                    cliente_dataScadenzaDocumento="1999-12-31",
                    cliente_sesso="",
                    cliente_ruolo=ruolo,
                )
            )
            print(f"  {username:<{larghezza}}  {email:<28}  {scopo}")

        db.add(
            Utente(
                utente_username=ORFANO[0],
                utente_password="",
                utente_password_hash=hash_password(PASSWORD_BCRYPT),
                utente_password_algo="bcrypt",
                utente_attivoSN=ORFANO[1],
                utente_padre=None,
                utente_created_by=None,
                utente_updated_by=None,
            )
        )
        print(f"  {ORFANO[0]:<{larghezza}}  {'(nessuna email)':<28}  {ORFANO[2]}")
        db.commit()

        print(f"\ndatabase: {nome}")
        print(f"password in chiaro (solo attuatore.prova): {PASSWORD_LEGACY}")
        print(f"password bcrypt (tutti gli altri):         {PASSWORD_BCRYPT}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

