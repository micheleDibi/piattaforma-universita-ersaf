"""ACL condivise da chiavi, storico, scritture e consegne."""

from dataclasses import dataclass

from fastapi import HTTPException
from src.chat_pratiche.partecipanti import autorizza as pratica
from src.realtime.dati import esegui
from src.realtime.errori import ErroreRealtime, richiedi
from src.realtime.identita import carica

RUOLI_PRIVATI = ("Aderente", "Regionale", "Provinciale", "Consulente", "Nazionale", "Operatore")


@dataclass(frozen=True)
class Conversazione:
    tipo: str
    risorsa: str
    codice: str | None
    pubblico: bool | None
    dominio: str
    persone: tuple

    @property
    def flags(self):
        return 1 if self.pubblico is False else 0

    def crypto(self, utente):
        d = dict(destinationType=self.tipo)
        if self.tipo == "PERSON":
            d["peerUserId"] = str(next(p.utente_id for p in self.persone if p.utente_id != utente))
        else:
            d["resourceId"] = self.risorsa
            d["resourceCode" if self.tipo == "PRACTICE" else "isPublic"] = (
                self.codice if self.tipo == "PRACTICE" else self.pubblico
            )
        return d


def persone(db, ids, blocca):
    risultati = []
    for uid in sorted(set(ids)):
        try:
            risultati.append(carica(db, uid, blocca))
        except Exception as e:
            if getattr(e, "detail", None) != "identity_not_current":
                raise
    richiedi(len(risultati) <= 256, "audience_too_large", 403)
    return tuple(risultati)


def personale(db, utente, peer, blocca):
    richiedi(peer != utente, "person_target_invalid", 403)
    a, b = sorted((utente, peer))
    acl = esegui(
        db,
        """SELECT revoked_at FROM realtime_person_contact_acl
        WHERE utente_low_id=:a AND utente_high_id=:b"""
        + (" FOR UPDATE" if blocca else ""),
        dict(a=a, b=b),
    ).first()
    richiedi(acl is not None and acl.revoked_at is None, "person_access_denied", 403)
    membri = persone(db, (a, b), blocca)
    richiedi(len(membri) == 2, "person_access_denied", 403)
    return Conversazione("PERSON", str(peer), None, None, f"PERSON:{a}:{b}", membri)


def del_ticket(db, utente, richiesta, blocca):
    tid, pubblico = richiesta
    richiedi(type(pubblico) is bool, "invalid_isPublic")
    r = esegui(
        db,
        "SELECT utente_id,ticket_codice FROM {ticket}ticket WHERE ticket_id=:id"
        + (" FOR UPDATE" if blocca else ""),
        {"id": tid},
    ).first()
    richiedi(r is not None, "ticket_access_denied", 403)
    auditor = uditori(db, (tid, pubblico), blocca)
    membri = persone(db, auditor + ([r.utente_id] if pubblico else []), blocca)
    richiedi(utente in {p.utente_id for p in membri}, "ticket_access_denied", 403)
    dominio = f"TICKET:{tid}:" + ("PUBLIC" if pubblico else "PRIVATE")
    return Conversazione("TICKET", str(tid), r.ticket_codice, pubblico, dominio, membri)


def uditori(db, richiesta, blocca):
    tid, pubblico = richiesta
    auditor = (
        esegui(
            db,
            """SELECT ud.utente_id FROM {ticket}ticket_uditore ud
        JOIN utenti u ON u.utente_id=ud.utente_id AND u.utente_attivoSN=-1
        JOIN clienti c ON c.utente_id=u.utente_id JOIN ruoli r ON r.ruolo_id=c.cliente_ruolo
        WHERE ud.ticket_id=:id AND ud.ticket_uditore_attivoSN=-1
        AND (SELECT COUNT(*) FROM clienti uc WHERE uc.utente_id=u.utente_id)=1"""
            + (
                ""
                if pubblico
                else " AND r.ruolo_codice IN (" + ",".join("'" + r + "'" for r in RUOLI_PRIVATI) + ")"
            )
            + " ORDER BY ud.utente_id LIMIT 257"
            + (" FOR UPDATE" if blocca else ""),
            {"id": tid},
        )
        .scalars()
        .all()
    )
    richiedi(len(auditor) <= 256, "audience_too_large", 403)
    return auditor


def autorizza(db, utente, richiesta, blocca=False):
    tipo, risorsa, pubblico = richiesta
    carica(db, utente)
    if tipo == "PERSON":
        return personale(db, utente, int(risorsa), blocca)
    if tipo == "TICKET":
        return del_ticket(db, utente, (int(risorsa), pubblico), blocca)
    richiedi(tipo == "PRACTICE", "invalid_destinationType")
    try:
        c, partecipanti = pratica(db, utente, int(risorsa), blocca=blocca)
    except HTTPException as errore:
        if errore.status_code not in (403, 404):
            raise
        raise ErroreRealtime("practice_access_denied", errore.status_code) from None
    membri = persone(db, [p.utente_id for p in partecipanti], blocca)
    return Conversazione(tipo, str(risorsa), c.numero, None, f"PRACTICE:{risorsa}:GROUP", membri)


def da_storico(db, utente, richiesta):
    tipo, cid, pubblico = richiesta
    if tipo != "PERSON":
        return autorizza(db, utente, richiesta)
    peer = esegui(
        db,
        """SELECT CASE WHEN utente_mitt_id=:u THEN utente_dest_id ELSE utente_mitt_id END
        FROM {ticket}messaggio WHERE messaggio_doc_id=:id AND (utente_mitt_id=:u OR utente_dest_id=:u)
        AND utente_mitt_id<>utente_dest_id ORDER BY messaggio_id DESC LIMIT 1""",
        dict(u=utente, id=cid),
    ).scalar()
    richiedi(peer is not None, "conversation_not_found", 404)
    return personale(db, utente, peer, False)
