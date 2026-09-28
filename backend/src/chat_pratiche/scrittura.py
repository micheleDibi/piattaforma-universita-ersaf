"""Una transazione per messaggio, ricevuta di retry, orario e grant."""
import hashlib
import hmac
import os
import struct
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException
from sqlalchemy import select, text

from src.chat_pratiche.cifratura import aad, codifica, decodifica
from src.chat_pratiche.chiavi import deriva
from src.chat_pratiche.configurazione import configurazione, chiavi
from src.chat_pratiche.models import Messaggio, StatoMessaggio
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.consegne import accoda
from src.chat_pratiche.notifiche import registra as registra_notifiche


def decifra_invio(contesto, client_id, cifrato):
    try:
        raw = decodifica(cifrato[3:])
        versione, ora, flags = struct.unpack(">BIB", raw[:6])
        tag = hashlib.sha256(client_id.encode()).digest()[:16]
        if not cifrato.startswith("u2.") or not 51 <= len(raw) <= 1050 or flags or not hmac.compare_digest(tag, raw[6:22]):
            raise ValueError()
        corrente = int(time.time()) // 3600
        if versione != configurazione().chat_chiave_versione or ora != corrente:
            raise HTTPException(409, "key_epoch_stale")
        chiave = deriva(versione, ora, f"PRACTICE:{contesto.pratica_id}:GROUP")
        valore = AESGCM(chiave).decrypt(raw[22:34], raw[34:],
            aad("u2", contesto.pratica_id, contesto.utente_id, codifica(tag), versione, ora))
        if not valore.decode("utf-8").strip() or len(valore) > 1000:
            raise ValueError()
        return valore, versione, ora
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422, "Messaggio non valido.") from None


def limite(db, utente_id):
    # Il lock per utente serializza anche invii su connessioni/worker diversi.
    db.execute(text("""INSERT INTO chat_pratica_limite VALUES (:u, 0, 0)
        ON DUPLICATE KEY UPDATE utente_id=VALUES(utente_id)"""), {"u": utente_id})
    riga = db.execute(text("SELECT finestra, tentativi FROM chat_pratica_limite WHERE utente_id=:u FOR UPDATE"),
                      {"u": utente_id}).one()
    ora = int(time.time())
    finestra, numero = (ora, 0) if ora - riga.finestra >= 60 else riga
    return finestra, numero


def ricevuta(db, contesto, comando):
    valori = dict(u=contesto.utente_id, p=contesto.pratica_id, c=comando["clientMessageId"])
    riga = db.execute(text("""SELECT messaggio_id, impronta FROM chat_pratica_comando
        WHERE utente_id=:u AND pratica_id=:p AND client_id=:c FOR UPDATE"""), valori).first()
    if riga and not hmac.compare_digest(riga.impronta, hashlib.sha256(comando["cifrato"].encode()).digest()):
        raise HTTPException(409, "L'identificativo è già associato a un altro messaggio.")
    return riga.messaggio_id if riga else None


def registra_metadati(db, contesto, dati):
    messaggio, comando, persone, versione, ora, adesso = dati
    db.execute(text("""INSERT INTO chat_pratica_comando VALUES (:u,:p,:c,:hash,:m,:ora)"""),
        dict(u=contesto.utente_id, p=contesto.pratica_id, c=comando["clientMessageId"],
             hash=hashlib.sha256(comando["cifrato"].encode()).digest(), m=messaggio.messaggio_id, ora=adesso))
    db.execute(text("INSERT INTO realtime_message_time VALUES ('PRACTICE',:m,:ora)"),
               dict(m=messaggio.messaggio_id, ora=adesso))
    for persona in persone:
        db.execute(text("""INSERT IGNORE INTO realtime_message_key_grant
            VALUES (:u,:d,:v,:e,:ora)"""), dict(u=persona.utente_id,
            d=f"PRACTICE:{contesto.pratica_id}:GROUP", v=versione, e=ora, ora=adesso))


def crea_record(db, contesto, dati):
    comando, persone = dati
    valore, versione, ora = decifra_invio(contesto, comando["clientMessageId"], comando["cifrato"])
    stati = list(db.scalars(select(StatoMessaggio.messaggio_stato_id)
        .where(StatoMessaggio.messaggio_stato_codice == "NUOVO")))
    if len(stati) != 1:
        raise HTTPException(503, "Stato iniziale dei messaggi non configurato.")
    adesso = datetime.now(timezone.utc)
    destinatario = min(p.cliente_id for p in persone if p.utente_id != contesto.utente_id)
    messaggio = Messaggio(messaggio_testo="", messaggio_oggetto="-",
        messaggio_dataInvio=adesso.astimezone(ZoneInfo("Europe/Rome")).replace(tzinfo=None),
        cliente_mittente_id=contesto.cliente_id, cliente_destinatario_id=destinatario,
        messaggio_stato_id=stati[0], messaggio_codice=contesto.numero, pratica_id=contesto.pratica_id)
    db.add(messaggio)
    db.flush()
    nonce = os.urandom(12)
    cifrato = AESGCM(deriva(versione, ora, f"PRACTICE:{contesto.pratica_id}:GROUP")).encrypt(nonce, valore,
        aad("u3", contesto.pratica_id, contesto.utente_id, str(messaggio.messaggio_id), versione, ora))
    messaggio.messaggio_testo = "u3." + codifica(struct.pack(">BIB", versione, ora, 0) + nonce + cifrato)
    registra_metadati(db, contesto, (messaggio, comando, persone, versione, ora, adesso.replace(tzinfo=None)))
    accoda(db, contesto, (messaggio, comando, persone, adesso.replace(tzinfo=None)))
    registra_notifiche(db, contesto, messaggio, persone)
    return messaggio.messaggio_id


def salva(db, contesto, comando):
    chiavi()
    finestra, numero = limite(db, contesto.utente_id)
    corrente, persone = autorizza(db, contesto.utente_id, contesto.pratica_id, blocca=True)
    if corrente != contesto:
        raise HTTPException(403, "I riferimenti della pratica sono cambiati.")
    precedente = ricevuta(db, corrente, comando)
    if precedente:
        return precedente
    if numero >= 20:
        raise HTTPException(429, "Troppi messaggi. Attendi un minuto.")
    identificativo = crea_record(db, corrente, (comando, persone))
    db.execute(text("UPDATE chat_pratica_limite SET finestra=:f, tentativi=:n WHERE utente_id=:u"),
               dict(f=finestra, n=numero + 1, u=contesto.utente_id))
    return identificativo
