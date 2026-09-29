import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import text
from src.database import SessionLocal
from src.realtime import accesso, bridge_notifiche, manutenzione, socket_operazioni
from src.realtime.identita import carica
from src.realtime.token import emetti
from tests.support import factories as f
from tests.support.realtime import (  # noqa: F401
    chat,
    cifra,
    frame_chat,
    header,
    pratica,
    universo,
)

pytestmark = pytest.mark.mariadb


@pytest.fixture
def domini(chat, universo, db):
    p, a, s = chat
    auditor = f.crea_attuatore(db, ruolo=f.RUOLO_NAZIONALE, email="auditor@example.org")
    db.execute(
        text("INSERT INTO realtime_person_contact_acl VALUES (:a,:b,'test',UTC_TIMESTAMP(),NULL)"),
        dict(a=min(a.utente_id, s.utente_id), b=max(a.utente_id, s.utente_id)),
    )
    db.execute(text("INSERT INTO ticket VALUES (70,:u,'TK-70')"), dict(u=s.utente_id))
    for u in (a.utente_id, auditor.utente_id):
        db.execute(text("INSERT INTO ticket_uditore VALUES (70,:u,-1)"), dict(u=u))
    db.commit()
    return p, a, s, auditor


def token_per(db, utente):
    s, r = accesso.nuova_sessione(db, carica(db, utente), "altro-browser")
    db.commit()
    return emetti(s, r)["accessToken"]


def comando(client, token, identita, tipo, risorsa, cid="comando1", pubblico=None, codice=None):
    key = dict(destinationType=tipo)
    if tipo == "PERSON":
        key["peerUserId"] = str(risorsa)
        a, b = sorted((identita, risorsa))
        dominio = f"PERSON:{a}:{b}"
    else:
        key["resourceId"] = str(risorsa)
        key["resourceCode" if tipo == "PRACTICE" else "isPublic"] = codice if tipo == "PRACTICE" else pubblico
        dominio = (
            f"PRACTICE:{risorsa}:GROUP"
            if tipo == "PRACTICE"
            else f"TICKET:{risorsa}:" + ("PUBLIC" if pubblico else "PRIVATE")
        )
    response = client.post("/realtime/crypto/key", json=key, headers=header(token))
    assert response.status_code == 200, response.text
    d = dict(
        type="CHAT",
        destinationType=tipo,
        to=str(risorsa),
        clientMessageId=cid,
        content=cifra(response.json(), dominio, identita, cid, privato=pubblico is False),
    )
    if tipo != "PERSON":
        d["destinationId"] = str(risorsa)
    if tipo == "PRACTICE":
        d["codice"] = codice
    if tipo == "TICKET":
        d["isPublic"] = pubblico
    return dict(channel="chat", payload=d)


@pytest.mark.parametrize(
    "tipo,pubblico", [("PERSON", None), ("PRACTICE", None), ("TICKET", True), ("TICKET", False)]
)
def test_invio_cifrato_storico_conversazioni_notifiche(client, db, universo, domini, tipo, pubblico):
    p, a, s, _ = domini
    risorsa = s.utente_id if tipo == "PERSON" else p.pratica_id if tipo == "PRACTICE" else 70
    d = comando(client, universo[0], a.utente_id, tipo, risorsa, pubblico=pubblico, codice=p.pratica_numero)
    risultato = socket_operazioni.elabora(universo[0], d)["payload"]
    assert risultato["content"].startswith("u3.")
    retry = socket_operazioni.elabora(universo[0], d)["payload"]
    assert retry["messaggioId"] == risultato["messaggioId"]
    conversazioni = client.get(
        "/realtime/api/v1/conversations",
        params=dict(destinationType=tipo, includeReadState="1"),
        headers=header(universo[0]),
    )
    assert conversazioni.status_code == 200, conversazioni.text
    item = conversazioni.json()["items"][0]
    assert item["lastMessageId"] == int(risultato["messaggioId"]) and item["lastMessageRead"] is True
    params = dict(destinationType=tipo, conversationId=item["conversationId"])
    if tipo == "TICKET":
        params["isPublic"] = str(pubblico).lower()
    response = client.get("/realtime/api/v1/messages", params=params, headers=header(universo[0]))
    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["content"] == risultato["content"]
    assert db.scalar(text("SELECT COUNT(*) FROM realtime_message_command")) == 1
    expected = 2 if tipo == "TICKET" and pubblico else 1
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche")) == expected


def test_ticket_privato_non_visibile_al_proprietario(client, db, universo, domini):
    _, a, s, _ = domini
    d = comando(client, universo[0], a.utente_id, "TICKET", 70, pubblico=False)
    socket_operazioni.elabora(universo[0], d)
    token = token_per(db, s.utente_id)
    key = client.post(
        "/realtime/crypto/key",
        json=dict(destinationType="TICKET", resourceId="70", isPublic=False),
        headers=header(token),
    )
    assert key.status_code == 403
    response = client.get(
        "/realtime/api/v1/messages",
        params=dict(destinationType="TICKET", conversationId="70", isPublic="false"),
        headers=header(token),
    )
    assert response.status_code == 403
    response = client.get(
        "/realtime/api/v1/conversations", params=dict(destinationType="TICKET"), headers=header(token)
    )
    assert response.json()["items"] == []
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche WHERE cliente_id=:c"), dict(c=s.cliente_id)) == 0


def test_revoca_contatto_blocca_invii_chiavi_storico_e_outbox(client, db, universo, domini):
    from src.realtime.consegne import pendenti

    _, a, s, _ = domini
    d = comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)
    socket_operazioni.elabora(universo[0], d)
    db.execute(text("UPDATE realtime_person_contact_acl SET revoked_at=UTC_TIMESTAMP()"))
    db.commit()
    with pytest.raises(Exception) as exc:
        socket_operazioni.elabora(universo[0], d)
    assert exc.value.status_code == 403
    response = client.get(
        "/realtime/api/v1/conversations", params=dict(destinationType="PERSON"), headers=header(universo[0])
    )
    assert response.json()["items"] == []
    with SessionLocal.begin() as check:
        assert not [d for d in pendenti(check, s.utente_id) if d["channel"] == "chat"]


def test_retry_concorrenti_producono_un_solo_record(client, db, universo, domini):
    _, a, s, _ = domini
    d = comando(client, universo[0], a.utente_id, "PERSON", s.utente_id)
    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(
            pool.map(lambda _: socket_operazioni.elabora(universo[0], d)["payload"]["messaggioId"], range(4))
        )
    assert len(set(ids)) == 1
    assert db.scalar(text("SELECT COUNT(*) FROM messaggio")) == 1
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche")) == 1


def test_notifiche_lette_e_snapshot_non_consumano_nuovi_arrivi(client, db, universo, domini):
    _, a, s, _ = domini
    token = token_per(db, s.utente_id)

    def invia(cid):
        return socket_operazioni.elabora(
            universo[0], comando(client, universo[0], a.utente_id, "PERSON", s.utente_id, cid)
        )

    primo = invia("primo")["payload"]
    snapshots = {d: str(uuid.uuid4()) for d in ("messages", "notifications")}
    for dominio, sid in snapshots.items():
        url = "/realtime/api/v1/" + dominio + "/attention"
        assert client.get(url, headers=header(token)).json() == dict(unreadCount=1, unseenCount=1)
        assert (
            client.post(url, params=dict(action="prepare", snapshotId=sid), headers=header(token)).status_code
            == 200
        )
    # Arrivo successivo: stessa conversazione ma ID diversi, non presenti nello snapshot.
    secondo = invia("secondo")["payload"]
    for dominio, sid in snapshots.items():
        response = client.post(
            "/realtime/api/v1/" + dominio + "/attention",
            params=dict(action="seen", snapshotId=sid),
            headers=header(token),
        )
        assert response.status_code == 200, response.text
        assert response.json()["unseenCount"] == 1
    page = client.get("/realtime/api/v1/notifications", headers=header(token))
    assert page.status_code == 200, page.text
    assert len(page.json()["items"]) == 1
    nid = page.json()["items"][0]["notificationId"]
    assert page.json()["items"][0]["messageContext"]["destinationType"] == "PERSON"
    assert (
        client.post(
            "/realtime/api/v1/notifications", params=dict(notificationId=nid), headers=header(token)
        ).status_code
        == 200
    )
    for d in (primo, secondo):
        response = client.post(
            "/realtime/api/v1/messages/read",
            params=dict(destinationType="PERSON", messageId=d["messaggioId"]),
            headers=header(token),
        )
        assert response.status_code == 200, response.text
    assert client.get("/realtime/api/v1/messages/attention", headers=header(token)).json() == dict(
        unreadCount=0, unseenCount=0
    )
    ids = client.get(
        "/realtime/api/v1/messages/read",
        params=dict(destinationType="PERSON", ids=primo["messaggioId"] + "," + secondo["messaggioId"]),
        headers=header(token),
    ).json()["readIds"]
    assert sorted(ids) == sorted([int(primo["messaggioId"]), int(secondo["messaggioId"])])


def test_login_refresh_replay_logout_e_recovery(client, db, universo, domini):
    _, a, _, _ = domini
    from src.utenti.models import Utente

    u = db.get(Utente, a.utente_id)
    u.utente_password_hash = None
    u.utente_password = "Sintetica!2026"
    db.commit()
    body = dict(username=u.utente_username, password="Sintetica!2026", deviceId="browser-test")
    response = client.post("/realtime/auth/login", json=body)
    assert response.status_code == 200, response.text
    login = response.json()
    response = client.post("/realtime/auth/refresh", json=dict(refreshToken=login["refreshToken"]))
    assert response.status_code == 200, response.text
    nuovo = response.json()
    assert nuovo["refreshToken"] != login["refreshToken"]
    assert (
        client.post("/realtime/auth/refresh", json=dict(refreshToken=login["refreshToken"])).status_code
        == 401
    )
    assert (
        client.get("/realtime/api/v1/notifications", headers=header(nuovo["accessToken"])).status_code == 401
    )
    secondo = client.post("/realtime/auth/login", json=body).json()
    db.execute(
        text(
            "UPDATE realtime_auth_session SET last_used_at=UTC_TIMESTAMP()-INTERVAL 2 DAY WHERE device_id='browser-test'"
        )
    )
    db.commit()
    assert (
        client.post("/realtime/auth/refresh", json=dict(refreshToken=secondo["refreshToken"])).status_code
        == 401
    )
    assert (
        client.post(
            "/realtime/auth/recover", json=dict(refreshToken=secondo["refreshToken"], deviceId="altro")
        ).status_code
        == 401
    )
    recovered = client.post(
        "/realtime/auth/recover", json=dict(refreshToken=secondo["refreshToken"], deviceId="browser-test")
    )
    assert recovered.status_code == 200, recovered.text
    assert (
        client.post("/realtime/auth/logout", headers=header(recovered.json()["accessToken"])).status_code
        == 204
    )
    assert (
        client.post(
            "/realtime/auth/recover",
            json=dict(refreshToken=recovered.json()["refreshToken"], deviceId="browser-test"),
        ).status_code
        == 401
    )


def test_produttore_idempotente_e_bridge_legacy(client, db, universo, domini, tmp_path, monkeypatch):
    from src.chat_pratiche.configurazione import configurazione

    _, a, s, _ = domini
    secret = "producer-sintetico-" + ("t" * 40)
    file = tmp_path / "producer.txt"
    file.write_text(secret, encoding="ascii")
    monkeypatch.setenv("REALTIME_PRODUCER_TOKEN_FILE", str(file))
    configurazione.cache_clear()
    d = dict(
        producerEventId=str(uuid.uuid4()),
        target=s.utente_id,
        createdBy=a.utente_id,
        operation="avviso",
        idRef="prova",
        title="Titolo",
        message="Test",
    )
    url = "/realtime/internal/notifications"
    assert client.post(url, json=d).status_code == 401
    response = client.post(url, json=d, headers=header(secret))
    assert response.status_code == 201, response.text
    assert client.post(url, json=d, headers=header(secret)).json()["status"] == "duplicate"
    assert client.post(url, json={**d, "message": "Altro"}, headers=header(secret)).status_code == 409
    with SessionLocal.begin() as check:
        bridge_notifiche.inizializza(check)
    parametro = db.execute(
        text("""INSERT INTO notifiche_parameters
        (notifica_parameter_operation,notifica_parameter_id_ref,notifica_parameter_message)
        VALUES ('avviso','r','nuovo')""")
    ).lastrowid
    db.execute(
        text("""INSERT INTO notifiche (notifica_title,notifica_body,notifica_created_by,
        notifica_created_at,notifica_updated_by,notifica_updated_at,notifica_parameter_id,notifica_letta,cliente_id)
        VALUES ('Legacy','nuovo',:u,NOW(),:u,NOW(),:p,0,:c)"""),
        dict(u=a.utente_id, c=s.cliente_id, p=parametro),
    )
    db.commit()
    with SessionLocal.begin() as check:
        assert bridge_notifiche.importa(check) == 1
    with SessionLocal.begin() as check:
        assert bridge_notifiche.importa(check, True) == 0
    assert db.scalar(text("SELECT COUNT(*) FROM realtime_delivery WHERE channel='notification'")) == 2


def test_preflight_intero_servizio_e_cleanup(client, db, universo, domini):
    from src.realtime.avvio import passo, verifica

    verifica()
    passo(True)
    db.execute(text("UPDATE realtime_auth_session SET last_used_at=UTC_TIMESTAMP()-INTERVAL 2 DAY"))
    db.commit()
    with SessionLocal.begin() as check:
        manutenzione.pulisci(check)
    assert db.scalar(text("SELECT revocation_reason FROM realtime_auth_session LIMIT 1")) == "IDLE"


def test_presenza_typing_acl_e_canale_notifiche_non_scrivibile(client, db, universo, domini):
    from src.realtime.presenza import online

    _, a, s, _ = domini
    token = token_per(db, s.utente_id)
    primo = socket_operazioni.avvia(universo[0])
    secondo = socket_operazioni.avvia(token)
    with SessionLocal() as check:
        assert s.utente_id in online(check, primo[0])
    d = dict(
        channel="chat",
        payload=dict(type="TYPING", destinationType="PERSON", to=str(s.utente_id), content=True),
    )
    assert socket_operazioni.elabora(universo[0], d) is None
    frames, _, _ = socket_operazioni.aggiorna(token, (secondo[1], secondo[2]), secondo[3], False)
    assert any(f["payload"].get("type") == "TYPING" for f in frames)
    with pytest.raises(Exception) as exc:
        socket_operazioni.elabora(universo[0], dict(channel="notification", payload={}))
    assert exc.value.status_code == 403
    socket_operazioni.chiudi(primo[1])
    socket_operazioni.chiudi(secondo[1])


def test_backend_avvia_api_socket_e_lavori(universo, domini, realtime_configurato, monkeypatch):
    import time

    from fastapi.testclient import TestClient
    from src.main import app
    from src.realtime import avvio

    monkeypatch.setattr(avvio, "ciclo", realtime_configurato)
    with TestClient(app, base_url="https://test.example.org") as browser:
        assert browser.get("/realtime/health").json() == {"status": "ok"}
        termine = time.monotonic() + 3
        while time.monotonic() < termine:
            risposta = browser.get("/realtime/ready")
            if risposta.status_code == 200:
                break
            time.sleep(0.05)
        assert risposta.status_code == 200
        assert risposta.json() == {"status": "ready"}
        assert browser.get("/realtime/api/v1/conversations").status_code == 401
        _, mittente, destinatario, _ = domini
        invio = comando(browser, universo[0], mittente.utente_id, "PERSON", destinatario.utente_id)
        with browser.websocket_connect(
            "/realtime/ws", subprotocols=["universo.realtime.v1", "jwt." + universo[0]]
        ) as ws:
            assert ws.receive_json()["payload"]["type"] == "connected"
            ws.send_json(invio)
            assert frame_chat(ws)["payload"]["content"].startswith("u3.")


@pytest.mark.parametrize("campo", ["CHAT_CHIAVI_FILE", "CHAT_UNIVERSO_JWT_FILE"])
def test_avvio_rifiuta_chiavi_mancanti(realtime_configurato, monkeypatch, campo):
    from fastapi import HTTPException
    from fastapi.testclient import TestClient
    from src.chat_pratiche.configurazione import chiavi, configurazione
    from src.main import app

    monkeypatch.setenv(campo, "")
    configurazione.cache_clear()
    chiavi.cache_clear()
    with pytest.raises(HTTPException) as errore, TestClient(app):
        pytest.fail("Il backend non deve partire con chiavi mancanti")
    assert errore.value.status_code == 503
