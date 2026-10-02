import concurrent.futures

import pytest
from fastapi import HTTPException
from sqlalchemy import select, func, text
from starlette.websockets import WebSocketDisconnect

from src.chat_pratiche import socket, socket_nativo
from src.chat_pratiche.models import Messaggio
from src.chat_pratiche.partecipanti import autorizza
from src.chat_pratiche.chiavi import ChiaviConversazione
from src.chat_pratiche.cifratura import cifra
from src.database import SessionLocal
from src.security.browser import nome_cookie, token_csrf
from tests.support.chat import chat, pratica  # noqa: F401
from tests.support import factories as f

pytestmark = pytest.mark.mariadb


def preparato(client, pratica_id, client_id="messaggio-1", testo="Buongiorno, documento ricevuto."):
    risposta = client.post(f"/pratiche/{pratica_id}/messaggi/prepara", json={"testo": testo, "clientMessageId": client_id})
    assert risposta.status_code == 200, risposta.text
    return dict(tipo="invia", **risposta.json())


def collega(client, pratica_id):
    token = client.cookies.get(nome_cookie())
    return client.websocket_connect(f"wss://test.example.org/pratiche/{pratica_id}/messaggi/socket",
        subprotocols=[socket.PROTOCOLLO, "csrf." + token_csrf(token)], headers={"Origin": "https://test.example.org"})


def ricevi_messaggio(ws):
    for _ in range(10):
        frame = ws.receive_json()
        if frame["tipo"] != "presenza":
            return frame
    pytest.fail("Messaggio non ricevuto")


def test_invio_storico_e_retry_senza_java(client, db, chat, monkeypatch):
    import httpx
    monkeypatch.setattr(httpx.Client, "request", lambda *a, **k: pytest.fail("Richiesta HTTP esterna"))
    p, _, _ = chat
    comando = preparato(client, p.pratica_id)
    with collega(client, p.pratica_id) as ws:
        assert ws.receive_json() == {"tipo": "connesso"}
        ws.send_json(comando)
        evento = ricevi_messaggio(ws)
        assert evento["clientMessageId"] == "messaggio-1"
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    assert socket_nativo.invia(token, ctx, comando)["id"] == evento["id"]
    assert db.scalar(select(func.count()).select_from(Messaggio)) == 1
    assert db.scalar(select(Messaggio.messaggio_testo)).startswith("u3.")
    storico = client.get(f"/pratiche/{p.pratica_id}/messaggi").json()
    assert storico["elementi"][0]["testo"] == "Buongiorno, documento ricevuto."


def test_concorrenza_stesso_comando_una_scrittura(client, db, chat):
    p, _, _ = chat
    comando = preparato(client, p.pratica_id)
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        risultati = list(executor.map(lambda _: socket_nativo.invia(token, ctx, comando), range(4)))
    assert len({r["id"] for r in risultati}) == 1
    assert db.scalar(select(func.count()).select_from(Messaggio)) == 1


def test_logout_chiude_socket_aperta(client, chat):
    p, _, _ = chat
    with collega(client, p.pratica_id) as ws:
        assert ws.receive_json()["tipo"] == "connesso"
        client.post("/auth/logout")
        with pytest.raises(WebSocketDisconnect) as exc:
            ricevi_messaggio(ws)
        assert exc.value.code == 4401


def test_socket_origine_non_autorizzata(client, chat):
    p, _, _ = chat
    token = client.cookies.get(nome_cookie())
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"wss://test.example.org/pratiche/{p.pratica_id}/messaggi/socket",
                subprotocols=[socket.PROTOCOLLO, "csrf." + token_csrf(token)], headers={"Origin": "https://estraneo.invalid"}):
            pytest.fail("Origine estranea accettata")


def test_utente_estraneo_e_account_ambiguo_non_partecipano(client, db, chat):
    p, account, _ = chat
    estraneo = f.crea_attuatore(db, email="estraneo@example.org", ruolo=5)
    with pytest.raises(HTTPException) as exc:
        autorizza(db, estraneo.utente_id, p.pratica_id)
    assert exc.value.status_code == 403
    f.crea_cliente(db, utente_id=account.utente_id, email="duplicato@example.org")
    assert client.get(f"/pratiche/{p.pratica_id}/messaggi").status_code == 403


def test_invio_falsificato_non_scrive(client, db, chat):
    p, _, _ = chat
    comando = preparato(client, p.pratica_id)
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    with pytest.raises(ValueError):
        socket_nativo.invia(token, ctx, {**comando, "from": "999"})
    alterato = {**comando, "cifrato": comando["cifrato"][:-4] + "AAAA"}
    with pytest.raises(HTTPException):
        socket_nativo.invia(token, ctx, alterato)
    assert db.scalar(select(func.count()).select_from(Messaggio)) == 0


def test_stesso_id_con_testo_diverso_conflitto(client, chat):
    p, _, _ = chat
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    socket_nativo.invia(token, ctx, preparato(client, p.pratica_id))
    with pytest.raises(HTTPException) as exc:
        socket_nativo.invia(token, ctx, preparato(client, p.pratica_id, testo="Altro messaggio"))
    assert exc.value.status_code == 409


def test_eventi_tra_connessioni_e_revoca_partecipante(client, db, chat):
    p, account, _ = chat
    token = client.cookies.get(nome_cookie())
    ctx, prima = socket_nativo.avvia(token, p.pratica_id)
    with collega(client, p.pratica_id) as ws:
        assert ws.receive_json()["tipo"] == "connesso"
        # Scrittura da una sessione SQL distinta dal lettore socket.
        evento = socket_nativo.invia(token, ctx, preparato(client, p.pratica_id))
        assert ricevi_messaggio(ws)["id"] == evento["id"]
    assert socket_nativo.aggiorna(token, ctx, prima)[0]["id"] == evento["id"]
    p.utente_id = None
    p.cliente_emittente_aderente_id = p.cliente_id
    db.commit()
    with pytest.raises(HTTPException):
        socket_nativo.aggiorna(token, ctx, prima)


def test_limite_persistente_retry_e_notifiche_senza_duplicati(client, db, chat):
    p, account, studente = chat
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    primo = preparato(client, p.pratica_id, "retry-limite")
    evento = socket_nativo.invia(token, ctx, primo)
    for numero in range(19):
        socket_nativo.invia(token, ctx, preparato(client, p.pratica_id, f"limite-{numero}"))
    with pytest.raises(HTTPException) as exc:
        socket_nativo.invia(token, ctx, preparato(client, p.pratica_id, "oltre-limite"))
    assert exc.value.status_code == 429
    assert socket_nativo.invia(token, ctx, primo) == evento
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche WHERE cliente_id=:c"), dict(c=studente.cliente_id)) == 20
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche_parameters WHERE notifica_parameter_operation='messaggioPratiche' AND notifica_parameter_message LIKE 'u3.%'")) == 20
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche WHERE cliente_id=:c"), dict(c=account.cliente_id)) == 0


def test_rollback_atomico_se_fallisce_la_notifica(client, db, chat, monkeypatch):
    from src.realtime import notifiche_scrittura as scrittura
    p, _, _ = chat
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    def guasto(*args):
        raise RuntimeError("Guasto simulato")
    monkeypatch.setattr(scrittura, "dal_messaggio", guasto)
    with pytest.raises(RuntimeError):
        socket_nativo.invia(token, ctx, preparato(client, p.pratica_id))
    for tabella in ("messaggi", "chat_pratica_comando", "chat_pratica_limite", "realtime_message_time", "realtime_message_key_grant", "realtime_delivery"):
        assert db.scalar(text(f"SELECT COUNT(*) FROM {tabella}")) == 0


def test_grant_storici_e_cursori_legati_alla_conversazione(client, db, chat):
    from dataclasses import replace
    from src.chat_pratiche.storico import cursore, confine
    import time
    p, account, studente = chat
    ctx, _ = autorizza(db, account.utente_id, p.pratica_id)
    ora = int(time.time()) // 3600 - 1
    with pytest.raises(HTTPException) as exc:
        ChiaviConversazione(db, ctx).chiave(1, ora)
    assert exc.value.status_code == 403
    db.execute(text("INSERT INTO realtime_message_key_grant VALUES (:u,:c,1,:e,UTC_TIMESTAMP())"),
               dict(u=account.utente_id,c=f"PRACTICE:{p.pratica_id}:GROUP",e=ora))
    db.commit()
    assert ChiaviConversazione(db, ctx).chiave(1, ora)["keyVersion"] == 1
    cursor = cursore(ctx, 42)
    assert confine(ctx, cursor) == 42
    for altro in (replace(ctx, utente_id=studente.utente_id), replace(ctx, pratica_id=p.pratica_id+1)):
        with pytest.raises(HTTPException):
            confine(altro, cursor)


def test_retry_dopo_cambio_ora_e_pulizia_coda_non_duplica(client, db, chat, monkeypatch):
    from src.realtime import crypto as scrittura
    p, _, _ = chat
    token = client.cookies.get(nome_cookie())
    ctx, _ = socket_nativo.avvia(token, p.pratica_id)
    comando = preparato(client, p.pratica_id)
    primo = socket_nativo.invia(token, ctx, comando)
    originale = scrittura.time.time()
    monkeypatch.setattr(scrittura.time, "time", lambda: originale+3600)
    assert socket_nativo.invia(token, ctx, comando) == primo
    db.execute(text("DELETE FROM realtime_delivery"))
    db.commit()
    assert socket_nativo.invia(token, ctx, comando) == primo
