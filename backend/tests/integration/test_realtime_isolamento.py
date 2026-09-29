import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import text
from src.database import SessionLocal
from src.realtime import api_notifiche, consegne, socket_operazioni
from src.realtime.errori import ErroreRealtime
from tests.integration.test_realtime_completo import (  # noqa: F401
    comando,
    domini,
    token_per,
)
from tests.support import factories as f
from tests.support.realtime import (  # noqa: F401
    chat,
    frame_chat,
    header,
    pratica,
    universo,
)

pytestmark = pytest.mark.mariadb


@pytest.mark.parametrize(
    "campo,modifica,ripristino",
    [
        ("utente_attivoSN", "0", "-1"),
        ("utente_password_changed_at", "UTC_TIMESTAMP()+INTERVAL 1 SECOND", "NULL"),
    ],
)
def test_revoca_identita_persistente(client, db, universo, campo, modifica, ripristino):
    uid = int(universo[1]["sub"])
    db.execute(text(f"UPDATE utenti SET {campo}={modifica} WHERE utente_id=:u"), dict(u=uid))
    db.commit()
    url = "/realtime/api/v1/notifications"
    assert client.get(url, headers=header(universo[0])).status_code == 401
    db.execute(text(f"UPDATE utenti SET {campo}={ripristino} WHERE utente_id=:u"), dict(u=uid))
    db.commit()
    assert client.get(url, headers=header(universo[0])).status_code == 401
    assert db.scalar(text("SELECT revocation_reason FROM realtime_auth_session")) == "IDENTITY"


@pytest.mark.parametrize("percorso", ["notifications", "messages/read", "messages/attention"])
def test_post_senza_body_rifiuta_contenuto(client, universo, percorso):
    risposta = client.post(
        "/realtime/api/v1/" + percorso, json={"inatteso": True}, headers=header(universo[0])
    )
    assert risposta.status_code == 400


def test_produttore_concorrente_non_duplica_ne_cambia_destinatario(db, universo, domini):
    _, a, s, altro = domini
    evento = dict(
        producerEventId=str(uuid.uuid4()),
        target=s.utente_id,
        createdBy=a.utente_id,
        operation="avviso",
        idRef="r",
        title="Aggiornamento",
        message="Test",
    )

    def invia(destinatario):
        try:
            return api_notifiche.invia({**evento, "target": destinatario}).status_code
        except ErroreRealtime as errore:
            return errore.status_code

    with ThreadPoolExecutor(max_workers=4) as pool:
        codici = list(pool.map(invia, [s.utente_id, altro.utente_id] * 2))
    assert sorted(codici) == [200, 201, 409, 409]
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche")) == 1


def test_cursor_legato_a_utente_e_dominio(client, db, universo, domini):
    _, a, s, _ = domini
    for cid in ("primo", "secondo"):
        socket_operazioni.elabora(
            universo[0], comando(client, universo[0], a.utente_id, "PERSON", s.utente_id, cid)
        )
    url = "/realtime/api/v1/messages"
    cid = db.scalar(text("SELECT document_id FROM realtime_person_conversation"))
    params = dict(destinationType="PERSON", conversationId=cid, limit="1")
    prima = client.get(url, params=params, headers=header(universo[0])).json()
    assert prima["hasMore"]
    params["cursor"] = prima["nextCursor"]
    seconda = client.get(url, params=params, headers=header(universo[0])).json()
    assert not seconda["hasMore"]
    assert seconda["items"][0]["messageId"] < prima["items"][0]["messageId"]
    assert client.get(url, params=params, headers=header(token_per(db, s.utente_id))).status_code == 400
    params.update(destinationType="PRACTICE", conversationId=str(domini[0].pratica_id))
    assert client.get(url, params=params, headers=header(universo[0])).status_code == 400


def test_storico_lettura_snapshot_e_chiavi_non_escono_dall_account(client, db, universo, domini):
    _, a, s, _ = domini
    d = socket_operazioni.elabora(
        universo[0], comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)
    )["payload"]
    esterno = f.crea_attuatore(db, email="esterno@example.org")
    headers = header(token_per(db, esterno.utente_id))
    url = "/realtime/api/v1/"
    assert (
        client.get(
            url + "messages",
            params=dict(destinationType="PERSON", conversationId=d["codice"]),
            headers=headers,
        ).status_code
        == 404
    )
    assert (
        client.post(
            url + "messages/read",
            params=dict(destinationType="PERSON", messageId=d["messaggioId"]),
            headers=headers,
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/realtime/crypto/key",
            json=dict(destinationType="PERSON", peerUserId=str(a.utente_id)),
            headers=headers,
        ).status_code
        == 403
    )
    assert client.get(url + "messages/attention", headers=headers).json() == dict(
        unreadCount=0, unseenCount=0
    )
    sid = str(uuid.uuid4())
    assert (
        client.post(
            url + "messages/attention",
            params=dict(action="prepare", snapshotId=sid),
            headers=header(universo[0]),
        ).status_code
        == 200
    )
    assert (
        client.post(
            url + "messages/attention", params=dict(action="seen", snapshotId=sid), headers=headers
        ).status_code
        == 404
    )


def test_pratica_incompleta_non_interrompe_presenza_o_elenco(client, db, universo, domini):
    p, a, _, _ = domini
    socket_operazioni.elabora(
        universo[0],
        comando(client, universo[0], a.utente_id, "PRACTICE", p.pratica_id, codice=p.pratica_numero),
    )
    db.execute(text("UPDATE pratiche SET pratica_numero='' WHERE pratica_id=:p"), dict(p=p.pratica_id))
    db.commit()
    result = client.get(
        "/realtime/api/v1/conversations", params=dict(destinationType="PRACTICE"), headers=header(universo[0])
    )
    assert result.status_code == 200 and result.json()["items"] == []
    avvio = socket_operazioni.avvia(universo[0])
    socket_operazioni.aggiorna(universo[0], (avvio[1], avvio[2]), avvio[3], True)
    socket_operazioni.chiudi(avvio[1])


def test_chiavi_storiche_personali_richiedono_grant(client, db, universo, domini):
    _, a, s, _ = domini
    epoca = int(time.time()) // 3600 - 1
    dati = dict(destinationType="PERSON", peerUserId=str(s.utente_id), keyVersion=1, epochHour=epoca)
    url = "/realtime/crypto/key"
    assert client.post(url, json=dati, headers=header(universo[0])).status_code == 403
    dominio = f"PERSON:{min(a.utente_id, s.utente_id)}:{max(a.utente_id, s.utente_id)}"
    db.execute(
        text("INSERT INTO realtime_message_key_grant VALUES (:u,:c,1,:e,UTC_TIMESTAMP())"),
        dict(u=a.utente_id, c=dominio, e=epoca),
    )
    db.commit()
    assert client.post(url, json=dati, headers=header(universo[0])).status_code == 200
    dati["peerUserId"] = str(a.utente_id)
    assert client.post(url, json=dati, headers=header(token_per(db, s.utente_id))).status_code == 403


def test_ack_non_puo_confermare_la_consegna_di_un_altro(db, universo, domini, client):
    _, a, s, _ = domini
    d = socket_operazioni.elabora(
        universo[0], comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)
    )["payload"]
    with SessionLocal.begin() as check:
        consegne.conferma(check, s.utente_id, d["deliveryId"])
    assert (
        db.scalar(
            text("SELECT acknowledged_at FROM realtime_delivery WHERE delivery_id=:id"),
            dict(id=d["deliveryId"]),
        )
        is None
    )


def test_socket_recupera_consegne_non_confermate(client, db, universo, domini):
    _, a, s, _ = domini
    d = socket_operazioni.elabora(
        universo[0], comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)
    )["payload"]
    sub = ["universo.realtime.v1", "jwt." + universo[0]]
    with client.websocket_connect("/realtime/ws", subprotocols=sub) as ws:
        ricevuto = frame_chat(ws)["payload"]
        assert ricevuto["messaggioId"] == d["messaggioId"]
    db.execute(text("UPDATE realtime_delivery SET next_attempt_at=UTC_TIMESTAMP()"))
    db.commit()
    with client.websocket_connect("/realtime/ws", subprotocols=sub) as ws:
        retry = frame_chat(ws)["payload"]
        assert retry["deliveryId"] == ricevuto["deliveryId"]
        ws.send_json(
            dict(channel="system", payload=dict(type="DELIVERY_ACK", deliveryId=retry["deliveryId"]))
        )
        ws.send_json(dict(channel="chat", payload=dict(type="LIST_USERS")))
        while ws.receive_json()["payload"].get("type") != "LIST_USERS":
            pass
    assert (
        db.scalar(
            text("SELECT acknowledged_at FROM realtime_delivery WHERE delivery_id=:id"),
            dict(id=d["deliveryId"]),
        )
        is not None
    )


def test_socket_rifiuta_ack_mai_ricevuto_senza_fermare_comandi_successivi(client, universo):
    with client.websocket_connect(
        "/realtime/ws", subprotocols=["universo.realtime.v1", "jwt." + universo[0]]
    ) as ws:
        assert ws.receive_json()["payload"]["type"] == "connected"
        ws.send_json(dict(channel="system", payload=dict(type="DELIVERY_ACK", deliveryId=str(uuid.uuid4()))))
        for _ in range(20):
            frame = ws.receive_json()
            if frame["payload"].get("type") == "error":
                assert frame["payload"]["code"] == "delivery_not_received"
                break
        else:
            pytest.fail("ACK non rifiutato")
        ws.send_json(dict(channel="chat", payload=dict(type="LIST_USERS")))
        for _ in range(20):
            if ws.receive_json()["payload"].get("type") == "LIST_USERS":
                break
        else:
            pytest.fail("La socket non accetta comandi dopo l'ACK non valido")


def test_revoca_inattivita_non_sovrascrive_logout(db, universo):
    from src.realtime.sessioni import revoca

    sid = universo[1]["sid"]
    with SessionLocal.begin() as check:
        revoca(check, sid, "LOGOUT")
    # Un controllo avviato prima del logout termina in ritardo.
    with SessionLocal.begin() as check:
        revoca(check, sid, "IDLE")
    assert db.scalar(text("SELECT revocation_reason FROM realtime_auth_session")) == "LOGOUT"


def test_scrittura_rilegge_account_dopo_snapshot_precedente(client, db, universo, domini):
    from src.realtime.identita import carica
    from src.realtime.scrittura import salva

    _, a, s, _ = domini
    payload = comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)["payload"]
    with SessionLocal.begin() as check:
        identita = carica(check, a.utente_id)
        assert carica(check, s.utente_id).utente_id == s.utente_id
        db.execute(text("UPDATE utenti SET utente_attivoSN=0 WHERE utente_id=:u"), dict(u=s.utente_id))
        db.commit()
        with pytest.raises(ErroreRealtime) as errore:
            salva(check, identita, payload)
        assert errore.value.status_code == 403
    assert db.scalar(text("SELECT COUNT(*) FROM messaggio")) == 0
