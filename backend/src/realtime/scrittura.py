"""ACL, cifratura, comando idempotente, notifiche e outbox: commit unico."""

import hashlib
import hmac
import json
from datetime import timedelta

from src.realtime import archivio, comandi, crypto
from src.realtime.conversazioni import autorizza
from src.realtime.dati import esegui, iso, json_compatibile, ora
from src.realtime.errori import richiedi
from src.realtime.limiti import budget_messaggi

ORDINE = (
    "type",
    "destinationType",
    "to",
    "destinationId",
    "codice",
    "isPublic",
    "content",
    "clientMessageId",
    "from",
)


def salva(db, identita, payload, limite=None):
    from src.realtime.consegne import accoda
    from src.realtime.notifiche_scrittura import dal_messaggio

    d = comandi.valida(payload, identita.utente_id)
    finestra, numero = budget_messaggi(db, identita.utente_id)
    c = autorizza(db, identita.utente_id, comandi.destinazione(d), blocca=True)
    richiedi(c.tipo != "PRACTICE" or d["codice"] == c.codice, "practice_reference_mismatch", 403)
    digest = hashlib.sha256(json_compatibile({k: d[k] for k in ORDINE if k in d}).encode()).digest()
    precedente = ricevuta(db, identita.utente_id, d["clientMessageId"], digest)
    if precedente:
        return precedente
    richiedi(limite is None or numero < limite, "rate_limited", 429)
    materiale = archivia(db, c, d)
    metadati(db, c, (d, digest, materiale))
    conferma = d
    for p in c.persone:
        evento = accoda(db, p.utente_id, "chat", d)
        if p.utente_id == identita.utente_id:
            conferma = evento
    dal_messaggio(db, c, d)
    esegui(
        db,
        "UPDATE chat_pratica_limite SET finestra=:f,tentativi=:n WHERE utente_id=:u",
        dict(f=finestra, n=numero + 1, u=identita.utente_id),
    )
    return conferma


def archivia(db, conversazione, comando):
    mittente = int(comando["from"])
    materiale = crypto.apri(conversazione, mittente, comando)
    try:
        mid, documento = archivio.inserisci(db, conversazione, mittente)
        comando.update(
            content=crypto.conserva(conversazione, mittente, mid, materiale),
            messaggioId=str(mid),
            timestamp=iso(ora()),
        )
    finally:
        crypto.cancella(materiale[0])
    if conversazione.tipo == "PERSON":
        comando["codice"] = documento
    archivio.aggiorna(db, conversazione.tipo, mid, comando["content"])
    return None, materiale[1], materiale[2]


def ricevuta(db, uid, cid, digest):
    r = esegui(
        db,
        """SELECT request_hash,canonical_payload FROM realtime_message_command
        WHERE sender_user_id=:u AND client_message_id=:c FOR UPDATE""",
        dict(u=uid, c=cid),
    ).first()
    if r is None:
        return None
    richiedi(hmac.compare_digest(r.request_hash, digest), "client_message_conflict", 409)
    richiedi(r.canonical_payload is not None, "command_incomplete", 503)
    return json.loads(r.canonical_payload)


def metadati(db, c, dati):
    d, digest, materiale = dati
    adesso = ora()
    esegui(
        db,
        """INSERT INTO realtime_message_command VALUES (:u,:cid,:hash,:tipo,:mid,:payload,:now,:exp)""",
        dict(
            u=int(d["from"]),
            cid=d["clientMessageId"],
            hash=digest,
            tipo=c.tipo,
            mid=int(d["messaggioId"]),
            payload=json_compatibile(d),
            now=adesso,
            exp=adesso + timedelta(days=30),
        ),
    )
    esegui(
        db,
        "INSERT INTO realtime_message_time VALUES (:tipo,:mid,:now)",
        dict(tipo=c.tipo, mid=int(d["messaggioId"]), now=adesso),
    )
    for p in c.persone:
        esegui(
            db,
            """INSERT IGNORE INTO realtime_message_key_grant VALUES (:u,:dominio,:v,:e,:now)""",
            dict(u=p.utente_id, dominio=c.dominio, v=materiale[1], e=materiale[2], now=adesso),
        )
