"""Lavori limitati per batch, senza cancellare messaggi e storico applicativo."""

from datetime import timedelta

from src.chat_pratiche.configurazione import configurazione
from src.realtime.dati import esegui, ora


def pulisci(db):
    adesso = ora()
    esegui(
        db,
        """UPDATE realtime_auth_session SET revoked_at=:now,revocation_reason='EXPIRED'
        WHERE revoked_at IS NULL AND refresh_expires_at<=:now LIMIT 500""",
        dict(now=adesso),
    )
    esegui(
        db,
        """UPDATE realtime_auth_session SET revoked_at=:now,revocation_reason='IDLE'
        WHERE revoked_at IS NULL AND last_used_at<=:idle LIMIT 500""",
        dict(now=adesso, idle=adesso - timedelta(seconds=configurazione().chat_universo_inattivita_secondi)),
    )
    for tabella, campo in (
        ("realtime_auth_refresh_history", "expires_at"),
        ("realtime_delivery", "expires_at"),
        ("realtime_message_command", "expires_at"),
        ("realtime_notification_command", "expires_at"),
        ("realtime_presenza", "scadenza"),
        ("realtime_evento", "scadenza"),
        ("realtime_limite", "scadenza"),
    ):
        esegui(db, f"DELETE FROM {tabella} WHERE {campo}<:now LIMIT 500", dict(now=adesso))
    esegui(
        db,
        """DELETE FROM realtime_auth_session WHERE revoked_at IS NOT NULL
        AND revoked_at<=:old AND refresh_expires_at<=:now LIMIT 500""",
        dict(now=adesso, old=adesso - timedelta(days=30)),
    )
    for dominio, colonna in (("notification", "notification_ids"), ("message", "item_ids")):
        tabella = "realtime_" + dominio + "_seen_snapshot"
        esegui(
            db,
            f"UPDATE {tabella} SET {colonna}='[]' WHERE expires_at<:now AND {colonna}<>'[]' LIMIT 500",
            dict(now=adesso),
        )
        esegui(
            db,
            f"DELETE FROM {tabella} WHERE expires_at<:old LIMIT 500",
            dict(old=adesso - timedelta(days=30)),
        )
