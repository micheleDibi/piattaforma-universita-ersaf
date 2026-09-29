"""Readiness dei contratti e ciclo di vita dei lavori realtime."""

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from src.chat_pratiche.avvio import verifica as verifica_chat
from src.chat_pratiche.avvio import verifica_schema
from src.chat_pratiche.configurazione import (
    chiavi,
    configurazione,
    leggi_segreto,
    svuota_chiavi,
)
from src.database import SessionLocal
from src.realtime import bridge_notifiche, manutenzione
from src.realtime.dati import esegui
from src.realtime.risorse import Risorse

logger = logging.getLogger("ersaf.realtime")


@asynccontextmanager
async def servizio(app):
    try:
        verifica()
    except Exception:
        svuota_chiavi()
        raise
    app.state.realtime = {}
    app.state.realtime_risorse = risorse = Risorse()
    lavoro = asyncio.create_task(ciclo(app.state.realtime))
    try:
        yield
    finally:
        lavoro.cancel()
        await asyncio.gather(lavoro, return_exceptions=True)
        await risorse.chiudi()
        svuota_chiavi()


def verifica():
    verifica_chat()
    c = configurazione()
    chiavi()
    leggi_segreto(c.chat_universo_jwt_file, massimo=128)
    if not (
        60 <= c.realtime_accesso_secondi <= 3600
        and 1 <= c.realtime_refresh_giorni <= 90
        and c.realtime_accesso_secondi
        < c.chat_universo_inattivita_secondi
        <= min(604800, c.realtime_refresh_giorni * 86400)
        and 10 <= c.realtime_manutenzione_secondi <= 3600
    ):
        raise ValueError("Scadenze realtime non valide.")
    with SessionLocal.begin() as db:
        verifica_schema(db)
        verifica_archivi(db)
        for sql in CONTRATTI:
            esegui(db, sql + " LIMIT 0")
        bridge_notifiche.inizializza(db)


def verifica_archivi(db):
    for tabella, colonna in (
        ("messaggio", "messaggio_testo"),
        ("ticket_messaggio", "ticket_messagglio_testo"),
    ):
        capienza = esegui(
            db,
            """SELECT CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=:s AND TABLE_NAME=:t AND COLUMN_NAME=:c""",
            dict(s=configurazione().realtime_schema_ticket, t=tabella, c=colonna),
        ).scalar()
        if capienza is None or capienza < 1403:
            raise ValueError("Archivio personale/ticket assente o colonna testo insufficiente.")


CONTRATTI = (
    "SELECT refresh_token_hash,refresh_generation,revocation_reason,created_at FROM realtime_auth_session",
    "SELECT token_hash,session_id,expires_at FROM realtime_auth_refresh_history",
    "SELECT delivery_id,connessione,inviata_at,confermata_at,prossimo_at FROM realtime_delivery_connessione",
    "SELECT messaggio_id,messaggio_doc_id,messaggio_testo,utente_mitt_id,utente_dest_id,messaggio_lettoSN FROM {ticket}messaggio",
    "SELECT ticket_id,ticket_codice,utente_id FROM {ticket}ticket",
    "SELECT ticket_id,utente_id,ticket_uditore_attivoSN FROM {ticket}ticket_uditore",
    "SELECT ticket_messaggio_id,ticket_messagglio_testo,utente_id,ticket_messaggio_is_public FROM {ticket}ticket_messaggio",
    "SELECT utente_low_id,utente_high_id,revoked_at FROM realtime_person_contact_acl",
    "SELECT document_id FROM realtime_person_conversation",
    "SELECT canonical_payload,request_hash FROM realtime_message_command",
    "SELECT canonical_payload,request_hash FROM realtime_notification_command",
    "SELECT notification_id,seen_at FROM realtime_notification_seen",
    "SELECT snapshot_id,notification_ids,applied_at FROM realtime_notification_seen_snapshot",
    "SELECT snapshot_id,item_ids,applied_at FROM realtime_message_seen_snapshot",
    "SELECT connessione,session_id,scadenza FROM realtime_presenza",
    "SELECT utente_id,payload,scadenza FROM realtime_evento",
    "SELECT utente_id,revisione FROM realtime_flusso_utente",
    "SELECT chiave,conteggio,scadenza FROM realtime_limite",
    "SELECT notification_id,bridge_status,error_code FROM realtime_notification_bridge",
    "SELECT baseline_id,scan_floor_id,initialized FROM realtime_notification_bridge_state",
)


def passo(audit):
    with SessionLocal.begin() as db:
        bridge_notifiche.importa(db, audit=audit)
        if audit:
            manutenzione.pulisci(db)


async def ciclo(stato):
    prossimo = 0
    while True:
        try:
            adesso = time.monotonic()
            audit = adesso >= prossimo
            lavoro = asyncio.create_task(asyncio.to_thread(passo, audit))
            try:
                await asyncio.shield(lavoro)
            except asyncio.CancelledError:
                # La transazione deve finire prima del teardown delle risorse.
                await lavoro
                raise
            stato["ultimo_successo"] = time.monotonic()
            if audit:
                prossimo = adesso + configurazione().realtime_manutenzione_secondi
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Lavoro realtime non riuscito; nuovo tentativo al ciclo successivo")
        await asyncio.sleep(1)
