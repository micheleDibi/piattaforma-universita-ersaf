"""Chi puo' fare cosa.

Fino a ieri l'autorizzazione non esisteva: c'era l'autenticazione (sei un
utente valido?) e nulla dopo. Il risultato era che qualunque utente loggato
poteva disattivare l'amministratore con `PUT /utenti/1`, e che chiunque -
anche senza token - poteva impersonare un attuatore.

Qui stanno le due regole che servono adesso, in un punto solo perche' il
difetto ricorrente di questo backend e' la regola scritta a mano in cinque
copie e corretta in due.
"""

from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.auth.servizio_login import cliente_principale, codice_ruolo
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.auth")

# Ruoli che amministrano gli altri utenti: modificano schede altrui e possono
# impersonare. Si confrontano i codici in minuscolo, come fa il gate 2FA del
# login, perche' nel database sono capitalizzati ("Regionale").
#
# "nazionale" e' in elenco pur non potendo fare login oggi: il gate 2FA lo
# ferma prima. Resta qui perche' il giorno in cui il 2FA esistera' non ci sara'
# nulla da cambiare, e perche' toglierlo direbbe il falso su chi comanda.
RUOLI_AMMINISTRATIVI = frozenset({"nazionale", "regionale"})

# Ruoli che non accedono alla piattaforma: 0 Utente, 4 Consulente, 6 Operatore.
RUOLI_SENZA_ACCESSO = frozenset({0, 4, 6})


def ruolo_di(db: Session, utente_id: int) -> str | None:
    """Il codice di ruolo di un utente, o None se non ha una riga `clienti`.

    Passa da cliente_principale e non da Utente.clienti: 869 utenti non hanno
    alcuna riga e 4 ne hanno due, quindi la relazione non e' deterministica.
    """
    cliente = cliente_principale(db, utente_id)
    if cliente is None:
        return None
    return codice_ruolo(db, cliente.cliente_ruolo)


def e_amministrativo(db: Session, utente_id: int) -> bool:
    return (ruolo_di(db, utente_id) or "").lower() in RUOLI_AMMINISTRATIVI


def richiedi_ruolo_amministrativo(
    db: Session, utente: Utente, operazione: str
) -> str:
    """Solleva 403 se l'utente non amministra. Restituisce il suo ruolo.

    `operazione` finisce solo nel log: il messaggio all'utente resta uguale per
    tutte, perche' distinguerlo descriverebbe la mappa dei permessi a chi non
    ne ha.
    """
    ruolo = ruolo_di(db, utente.utente_id)
    if (ruolo or "").lower() not in RUOLI_AMMINISTRATIVI:
        logger.warning(
            "%s negata: utente_id=%s con ruolo=%s non e' amministrativo",
            operazione,
            utente.utente_id,
            ruolo,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai i permessi per questa operazione.",
        )
    return ruolo
