"""Paginazione legata a utente/pratica; dati legacy invariati."""
import hashlib
import hmac
from datetime import timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import text

from src.config import get_impostazioni
from src.chat_pratiche.cifratura import decifra
from src.chat_pratiche.chiavi import ChiaviConversazione

SELECT = """SELECT m.messaggio_id AS messageId, m.messaggio_testo AS content,
    COALESCE(s.utente_id,0) AS senderUserId, r.utente_id AS recipientUserId,
    COALESCE(NULLIF(TRIM(CONCAT_WS(' ',s.cliente_nome,s.cliente_cognome)),''),
             'Utente non disponibile') AS senderName,
    m.messaggio_dataInvio AS legacyTime, t.sent_at_utc AS utcTime,
    c.client_id AS clientMessageId
    FROM messaggi m LEFT JOIN clienti s ON s.cliente_id=m.cliente_mittente_id
    LEFT JOIN clienti r ON r.cliente_id=m.cliente_destinatario_id
    LEFT JOIN realtime_message_time t ON t.destination_type='PRACTICE' AND t.message_id=m.messaggio_id
    LEFT JOIN chat_pratica_comando c ON c.messaggio_id=m.messaggio_id
    WHERE m.pratica_id=:p """


def cursore(contesto, valore):
    payload = f"{contesto.utente_id}:{contesto.pratica_id}:{valore}"
    mac = hmac.new(get_impostazioni().session_token_pepper.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{valore}.{mac}"


def confine(contesto, valore):
    if not valore:
        return 2147483648
    try:
        identificativo = int(valore.split(".")[0])
        if identificativo < 1 or not hmac.compare_digest(valore, cursore(contesto, identificativo)):
            raise ValueError()
        return identificativo
    except (ValueError, TypeError):
        raise HTTPException(422, "Cursore non valido per questa conversazione.") from None


def data_record(riga):
    valore = riga["utcTime"] or riga["legacyTime"]
    if valore is None:
        return None
    zona = timezone.utc if riga["utcTime"] else ZoneInfo("Europe/Rome")
    return valore.replace(tzinfo=zona).astimezone(timezone.utc).isoformat()


def elemento(db, contesto, riga):
    try:
        testo = decifra(ChiaviConversazione(db, contesto), riga)
    except HTTPException as errore:
        if errore.status_code != 403:
            raise
        testo = "Messaggio non disponibile per questo account"
    except Exception:
        testo = "Messaggio non decifrabile"
    return dict(id=str(riga["messageId"]), autore=riga["senderName"], autoreId=str(riga["senderUserId"]),
                mio=riga["senderUserId"] == contesto.utente_id, testo=testo, data=data_record(riga))


def pagina(db, contesto, cursor=None, limite=30):
    righe = db.execute(text(SELECT + " AND m.messaggio_id < :prima ORDER BY m.messaggio_id DESC LIMIT :n"),
        dict(p=contesto.pratica_id, prima=confine(contesto, cursor), n=limite + 1)).mappings().all()
    altri = len(righe) > limite
    righe = righe[:limite]
    return dict(elementi=[elemento(db, contesto, r) for r in reversed(righe)], altri=altri,
                cursore=cursore(contesto, righe[-1]["messageId"]) if altri else None)


def eventi(db, contesto, dopo):
    righe = db.execute(text(SELECT + " AND m.messaggio_id > :dopo ORDER BY m.messaggio_id LIMIT 100"),
                       dict(p=contesto.pratica_id, dopo=dopo)).mappings().all()
    return [dict(tipo="messaggio", id=str(r["messageId"]),
        **({"clientMessageId": r["clientMessageId"]} if r["senderUserId"] == contesto.utente_id and r["clientMessageId"] else {}))
        for r in righe]
