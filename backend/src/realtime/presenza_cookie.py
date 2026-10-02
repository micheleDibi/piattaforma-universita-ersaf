"""Lease cookie nella presenza condivisa, senza creare sessioni Bearer."""

from sqlalchemy import Integer, String, func, select, text

from src.clienti.models import Cliente
from src.security.sessioni import sessioni_valide

PREFISSO = "cookie:"


def session_id(sess_id):
    # Solo l'ID interno, mai il cookie o la sua impronta.
    return PREFISSO + str(sess_id)


def online(db):
    lease = text(
        "SELECT session_id,utente_id FROM realtime_presenza WHERE scadenza>UTC_TIMESTAMP(6)"
    ).columns(session_id=String, utente_id=Integer).subquery()
    valide = sessioni_valide().subquery()
    query = select(valide.c.utente_id).join(
        lease,
        (lease.c.session_id == func.concat(PREFISSO, valide.c.sess_id))
        & (lease.c.utente_id == valide.c.utente_id),
    ).where(valide.c.utente_id.in_(select(Cliente.utente_id).group_by(Cliente.utente_id).having(func.count() == 1)))
    return set(db.scalars(query))
