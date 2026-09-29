import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
from sqlalchemy import text
from src.database import SessionLocal
from src.realtime import accesso, consegne, sessioni, socket_operazioni
from src.realtime.dati import ora
from src.realtime.errori import ErroreRealtime
from src.realtime.identita import carica
from tests.integration.test_realtime_completo import (  # noqa: F401
    comando,
    domini,
    token_per,
)
from tests.support.realtime import chat, header, pratica, universo  # noqa: F401

pytestmark = pytest.mark.mariadb


def consegna_personale(client, universo, domini):
    _, a, s, _ = domini
    return socket_operazioni.elabora(
        universo[0], comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)
    )["payload"]


def confermata(db, did):
    db.expire_all()
    return (
        db.scalar(text("SELECT acknowledged_at FROM realtime_delivery WHERE delivery_id=:id"), dict(id=did))
        is not None
    )


def test_ack_attende_tutti_i_socket_anche_con_transazioni_distinte(client, db, universo, domini):
    primo, secondo = [socket_operazioni.avvia(universo[0]) for _ in range(2)]
    did = consegna_personale(client, universo, domini)["deliveryId"]
    for conn in (primo, secondo):
        assert socket_operazioni.prepara(universo[0], (conn[1], did))
    socket_operazioni.conferma(universo[0], (primo[1], did))
    assert not confermata(db, did)
    socket_operazioni.conferma(universo[0], (secondo[1], did))
    assert confermata(db, did)
    for conn in (primo, secondo):
        socket_operazioni.chiudi(conn[1])


def test_nuovo_socket_partecipa_al_quorum_e_chiusura_non_fa_perdere_consegne(client, db, universo, domini):
    primo, secondo = [socket_operazioni.avvia(universo[0]) for _ in range(2)]
    did = consegna_personale(client, universo, domini)["deliveryId"]
    assert socket_operazioni.prepara(universo[0], (primo[1], did))
    socket_operazioni.conferma(universo[0], (primo[1], did))
    socket_operazioni.chiudi(secondo[1])
    nuovo = socket_operazioni.avvia(universo[0])
    frames, _, _ = socket_operazioni.aggiorna(universo[0], (nuovo[1], nuovo[2]), nuovo[3], False)
    assert any(f["payload"].get("deliveryId") == did for f in frames)
    assert not confermata(db, did)
    assert socket_operazioni.prepara(universo[0], (nuovo[1], did))
    socket_operazioni.conferma(universo[0], (nuovo[1], did))
    assert confermata(db, did)
    for conn in (primo, nuovo):
        socket_operazioni.chiudi(conn[1])


def test_ack_parziale_non_blocca_nuove_consegne_e_chiusura_completa_quorum(client, db, universo, domini):
    primo, secondo = [socket_operazioni.avvia(universo[0]) for _ in range(2)]
    with SessionLocal.begin() as tx:
        for n in range(30):
            d = consegne.accoda(tx, primo[0].utente_id, "notification", dict(notificationId=1000 + n))
            # Isoliamo la pianificazione dalla ACL notifiche, provata separatamente.
            tx.execute(
                text(
                    "INSERT INTO realtime_delivery_connessione VALUES (:id,:c,UTC_TIMESTAMP(),UTC_TIMESTAMP(),1,UTC_TIMESTAMP())"
                ),
                dict(id=d["deliveryId"], c=primo[1]),
            )
    did = consegna_personale(client, universo, domini)["deliveryId"]
    frames, _, _ = socket_operazioni.aggiorna(universo[0], (primo[1], primo[2]), primo[3], False)
    assert any(f["payload"].get("deliveryId") == did for f in frames)
    assert socket_operazioni.prepara(universo[0], (primo[1], did))
    socket_operazioni.conferma(universo[0], (primo[1], did))
    socket_operazioni.chiudi(secondo[1])
    socket_operazioni.aggiorna(universo[0], (primo[1], primo[2]), primo[3], False)
    assert confermata(db, did)
    socket_operazioni.chiudi(primo[1])


def test_ack_non_puo_anticipare_invii_a_un_altro_socket(client, db, universo, domini):
    primo, secondo = [socket_operazioni.avvia(universo[0]) for _ in range(2)]
    did = consegna_personale(client, universo, domini)["deliveryId"]
    assert socket_operazioni.prepara(universo[0], (primo[1], did))
    with pytest.raises(ErroreRealtime, match="delivery_not_received"):
        socket_operazioni.conferma(universo[0], (secondo[1], did))
    assert not confermata(db, did)
    for conn in (primo, secondo):
        socket_operazioni.chiudi(conn[1])


def test_comandi_non_estendono_inattivita_ma_http_si(client, db, universo):
    sid = universo[1]["sid"]
    prima = ora() - timedelta(hours=1)
    db.execute(
        text("UPDATE realtime_auth_session SET last_used_at=:n WHERE session_id=:sid"), dict(n=prima, sid=sid)
    )
    db.commit()
    socket_operazioni.elabora(universo[0], dict(channel="chat", payload=dict(type="LIST_USERS")))
    assert (
        db.scalar(text("SELECT last_used_at FROM realtime_auth_session WHERE session_id=:sid"), dict(sid=sid))
        == prima
    )
    assert (
        client.get("/realtime/api/v1/notifications/attention", headers=header(universo[0])).status_code == 200
    )
    assert (
        db.scalar(text("SELECT last_used_at FROM realtime_auth_session WHERE session_id=:sid"), dict(sid=sid))
        > prima
    )


@pytest.mark.parametrize("recupero", [False, True])
def test_tetto_rotazioni_revoca_famiglia_anche_nel_recovery(client, db, universo, recupero):
    s, refresh = accesso.nuova_sessione(db, carica(db, int(universo[1]["sub"])), "browser-test")
    db.execute(
        text("UPDATE realtime_auth_session SET refresh_generation=10000 WHERE session_id=:sid"),
        dict(sid=s["session_id"]),
    )
    if recupero:
        db.execute(
            text(
                "UPDATE realtime_auth_session SET last_used_at=UTC_TIMESTAMP()-INTERVAL 2 DAY WHERE session_id=:sid"
            ),
            dict(sid=s["session_id"]),
        )
    db.commit()
    with pytest.raises(ErroreRealtime):
        sessioni.ruota(refresh, "browser-test" if recupero else None)
    assert (
        db.scalar(
            text("SELECT revocation_reason FROM realtime_auth_session WHERE session_id=:sid"),
            dict(sid=s["session_id"]),
        )
        == "ROTATION_LIMIT"
    )
    assert (
        db.scalar(
            text("SELECT COUNT(*) FROM realtime_auth_refresh_history WHERE session_id=:sid"),
            dict(sid=s["session_id"]),
        )
        == 0
    )


def test_refresh_concorrente_rileva_replay_e_revoca_vincitore(db, universo):
    s, refresh = accesso.nuova_sessione(db, carica(db, int(universo[1]["sub"])), "browser-test")
    db.commit()

    def prova(_):
        try:
            return sessioni.ruota(refresh)
        except ErroreRealtime as errore:
            return errore.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        risultati = list(pool.map(prova, range(2)))
    assert sum(isinstance(r, dict) for r in risultati) == 1 and 401 in risultati
    with pytest.raises(ErroreRealtime):
        with sessioni.transazione(next(r for r in risultati if isinstance(r, dict))["accessToken"]):
            pass


def test_snapshot_visti_ricontrolla_appartenenza_al_momento_dell_applicazione(client, db, universo, domini):
    _, _, destinatario, _ = domini
    did = consegna_personale(client, universo, domini)
    h = header(token_per(db, destinatario.utente_id))
    url = "/realtime/api/v1/messages/attention"
    sid = str(uuid.uuid4())
    assert client.post(url, params=dict(action="prepare", snapshotId=sid), headers=h).status_code == 200
    db.execute(text("UPDATE realtime_person_contact_acl SET revoked_at=UTC_TIMESTAMP()"))
    db.commit()
    assert client.post(url, params=dict(action="seen", snapshotId=sid), headers=h).status_code == 200
    assert (
        db.scalar(
            text("SELECT COUNT(*) FROM realtime_message_state WHERE utente_id=:u AND item_id=:id"),
            dict(u=destinatario.utente_id, id=int(did["messaggioId"]) * 4),
        )
        == 0
    )


def test_limiti_socket_per_sessione_utente_e_globali(client, db, universo, monkeypatch):
    from src.chat_pratiche.configurazione import configurazione

    c = configurazione()
    monkeypatch.setattr(c, "realtime_max_connections_per_auth_session", 1)
    primo = socket_operazioni.avvia(universo[0])
    with pytest.raises(ErroreRealtime, match="too_many_connections"):
        socket_operazioni.avvia(universo[0])
    altro = token_per(db, primo[0].utente_id)
    monkeypatch.setattr(c, "realtime_max_connections_per_user", 1)
    with pytest.raises(ErroreRealtime, match="too_many_connections"):
        socket_operazioni.avvia(altro)
    monkeypatch.setattr(c, "realtime_max_connections_per_user", 8)
    monkeypatch.setattr(c, "realtime_max_connections", 1)
    with pytest.raises(ErroreRealtime, match="too_many_connections"):
        socket_operazioni.avvia(altro)
    socket_operazioni.chiudi(primo[1])
    ammesso = socket_operazioni.avvia(altro)
    socket_operazioni.chiudi(ammesso[1])


@pytest.mark.parametrize("pubblico", [True, False])
def test_storico_ticket_segue_membri_correnti_senza_grant(client, db, universo, domini, pubblico):
    _, _, _, auditor = domini
    h = header(token_per(db, auditor.utente_id))
    dati = dict(
        destinationType="TICKET",
        resourceId="70",
        isPublic=pubblico,
        keyVersion=1,
        epochHour=int(time.time()) // 3600 - 1,
    )
    assert db.scalar(text("SELECT COUNT(*) FROM realtime_message_key_grant")) == 0
    assert client.post("/realtime/crypto/key", json=dati, headers=h).status_code == 200
    db.execute(
        text("UPDATE ticket_uditore SET ticket_uditore_attivoSN=0 WHERE utente_id=:u"),
        dict(u=auditor.utente_id),
    )
    db.commit()
    assert client.post("/realtime/crypto/key", json=dati, headers=h).status_code == 403


def test_storico_personale_esige_grant_e_versione_disponibile(client, universo, domini):
    _, _, studente, _ = domini
    dati = dict(
        destinationType="PERSON",
        peerUserId=str(studente.utente_id),
        keyVersion=1,
        epochHour=int(time.time()) // 3600 - 1,
    )
    assert client.post("/realtime/crypto/key", json=dati, headers=header(universo[0])).status_code == 403
    dati["keyVersion"] = 2
    assert client.post("/realtime/crypto/key", json=dati, headers=header(universo[0])).status_code == 400
