"""Scritture nei tre archivi legacy nella stessa transazione dell'outbox."""

import uuid
from datetime import timezone
from zoneinfo import ZoneInfo

from src.realtime.dati import esegui, ora
from src.realtime.errori import richiedi


def nome(c, uid):
    return next(p.nome or f"Utente {uid}" for p in c.persone if p.utente_id == uid)


def documento_personale(db, c):
    a, b = sorted(p.utente_id for p in c.persone)
    # Conserva anche una vecchia conversazione priva della tabella di mapping.
    vecchio = esegui(
        db,
        """SELECT messaggio_doc_id FROM {ticket}messaggio
        WHERE (utente_mitt_id=:a AND utente_dest_id=:b) OR (utente_mitt_id=:b AND utente_dest_id=:a)
        ORDER BY messaggio_id LIMIT 1""",
        dict(a=a, b=b),
    ).scalar()
    candidato = vecchio or str(uuid.uuid4()).upper()
    esegui(
        db,
        """INSERT INTO realtime_person_conversation VALUES (:a,:b,:d,:now)
        ON DUPLICATE KEY UPDATE document_id=document_id""",
        dict(a=a, b=b, d=candidato, now=ora()),
    )
    return esegui(
        db,
        "SELECT document_id FROM realtime_person_conversation WHERE utente_low_id=:a AND utente_high_id=:b",
        dict(a=a, b=b),
    ).scalar_one()


def inserisci(db, c, utente):
    adesso = ora().replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Europe/Rome")).replace(tzinfo=None)
    valori = dict(now=adesso, u=utente, nome=nome(c, utente), id=c.risorsa)
    if c.tipo == "PERSON":
        doc = documento_personale(db, c)
        valori.update(doc=doc, destinatario=nome(c, int(c.risorsa)))
        sql = """INSERT INTO {ticket}messaggio (messaggio_data_creazione,messaggio_testo,
            utente_dest_id,utente_dest_denominazione,utente_mitt_id,utente_mitt_denominazione,messaggio_doc_id,messaggio_lettoSN)
            VALUES (:now,'',:id,:destinatario,:u,:nome,:doc,0)"""
        return esegui(db, sql, valori).lastrowid, doc
    if c.tipo == "TICKET":
        valori["pubblico"] = -1 if c.pubblico else 0
        sql = """INSERT INTO {ticket}ticket_messaggio (ticket_messaggio_data_creazione,ticket_messagglio_testo,
            utente_id,utente_denomazione,ticket_id,ticket_messaggio_is_public) VALUES (:now,'',:u,:nome,:id,:pubblico)"""
        return esegui(db, sql, valori).lastrowid, c.risorsa
    return inserisci_pratica(db, c, (utente, valori)), c.codice


def inserisci_pratica(db, c, dati):
    utente, valori = dati
    stati = (
        esegui(db, "SELECT messaggio_stato_id FROM messaggi_stati WHERE messaggio_stato_codice='NUOVO'")
        .scalars()
        .all()
    )
    richiedi(len(stati) == 1, "message_state_unavailable", 503)
    valori.update(
        stato=stati[0],
        codice=c.codice,
        mittente=next(p.cliente_id for p in c.persone if p.utente_id == utente),
        destinatario=min(p.cliente_id for p in c.persone if p.utente_id != utente),
    )
    return esegui(
        db,
        """INSERT INTO messaggi (messaggio_testo,messaggio_oggetto,messaggio_dataInvio,
        cliente_mittente_id,cliente_destinatario_id,messaggio_stato_id,messaggio_codice,pratica_id)
        VALUES ('','-',:now,:mittente,:destinatario,:stato,:codice,:id)""",
        valori,
    ).lastrowid


def aggiorna(db, tipo, mid, cifrato):
    tabella, pk, campo = {
        "PERSON": ("{ticket}messaggio", "messaggio_id", "messaggio_testo"),
        "PRACTICE": ("messaggi", "messaggio_id", "messaggio_testo"),
        "TICKET": ("{ticket}ticket_messaggio", "ticket_messaggio_id", "ticket_messagglio_testo"),
    }[tipo]
    esegui(db, f"UPDATE {tabella} SET {campo}=:testo WHERE {pk}=:id", dict(testo=cifrato, id=mid))
