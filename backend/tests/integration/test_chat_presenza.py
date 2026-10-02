"""Presenza fra socket cookie e Bearer sul solo dataset sintetico locale."""

import uuid
from dataclasses import replace

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from starlette.websockets import WebSocketDisconnect

from src.chat_pratiche import presenza as cookie
from src.chat_pratiche.socket_nativo import avvia
from src.database import SessionLocal
from src.realtime import presenza, socket_operazioni
from src.security.browser import nome_cookie
from src.security.sessioni import crea_sessione
from tests.integration.test_chat_nativa import collega, preparato
from tests.integration.test_realtime_completo import token_per
from tests.support import factories as f
from tests.support.realtime import chat, pratica, universo  # noqa: F401

pytestmark = pytest.mark.mariadb


def socket_cookie(client, db, chat, studente=False):
    p, account, studentessa = chat
    token = client.cookies.get(nome_cookie())
    if studente:
        token, _ = crea_sessione(db, studentessa.utente_id, None, "browser locale")
        db.commit()
    ctx, _ = avvia(token, p.pratica_id)
    conn = str(uuid.uuid4())
    cookie.apri(token, ctx, conn)
    return token, ctx, conn


def test_cookie_e_bearer_condividono_presenza_e_ids_distinti(client, db, chat, universo):
    a = socket_cookie(client, db, chat)
    b = socket_operazioni.avvia(token_per(db, chat[2].utente_id))
    try:
        assert cookie.aggiorna(*a) == {chat[1].utente_id, chat[2].utente_id}
        with SessionLocal() as check:
            assert chat[1].utente_id in presenza.online(check, b[0])
        socket_operazioni.chiudi(b[1])
        assert cookie.aggiorna(*a) == {chat[1].utente_id}
    finally:
        socket_operazioni.chiudi(a[2])
        socket_operazioni.chiudi(b[1])


def test_ultima_connessione_cookie_chiusa_rende_offline(client, db, chat, universo):
    a = socket_cookie(client, db, chat)
    b = socket_cookie(client, db, chat)
    try:
        socket_operazioni.chiudi(a[2])
        with SessionLocal() as check:
            assert chat[1].utente_id in presenza.online_utenti(check)
        socket_operazioni.chiudi(b[2])
        with SessionLocal() as check:
            assert chat[1].utente_id not in presenza.online_utenti(check)
    finally:
        socket_operazioni.chiudi(a[2])
        socket_operazioni.chiudi(b[2])


@pytest.mark.parametrize("invalidazione", ["logout", "scadenza", "durata", "password", "disattivato", "lease", "ambiguo"])
def test_presenza_cookie_esclude_sessioni_non_valide(client, db, chat, universo, invalidazione):
    a = socket_cookie(client, db, chat)
    uid = chat[1].utente_id
    try:
        if invalidazione == "logout":
            client.post("/auth/logout")
        elif invalidazione == "ambiguo":
            f.crea_cliente(db, utente_id=uid, email="elena.bianchi@example.org")
        else:
            query = {
                "scadenza": "UPDATE auth_sessione SET sess_expires_at=NOW()-INTERVAL 1 SECOND WHERE utente_id=:u",
                "durata": "UPDATE auth_sessione SET sess_created_at=NOW()-INTERVAL 400 DAY WHERE utente_id=:u",
                "password": "UPDATE utenti SET utente_password_changed_at=NOW()+INTERVAL 1 SECOND WHERE utente_id=:u",
                "disattivato": "UPDATE utenti SET utente_attivoSN=0 WHERE utente_id=:u",
                "lease": "UPDATE realtime_presenza SET scadenza=UTC_TIMESTAMP()-INTERVAL 1 SECOND WHERE utente_id=:u",
            }[invalidazione]
            db.execute(text(query), dict(u=uid)); db.commit()
        with SessionLocal() as check:
            assert uid not in presenza.online_utenti(check)
    finally:
        socket_operazioni.chiudi(a[2])


def test_presenza_limitata_ai_partecipanti_e_revocata_al_cambio_pratica(client, db, chat, universo):
    a = socket_cookie(client, db, chat)
    estraneo = f.crea_attuatore(db, ruolo=2, email="giorgio.moretti@example.org")
    b = socket_operazioni.avvia(token_per(db, estraneo.utente_id))
    try:
        assert estraneo.utente_id not in cookie.aggiorna(*a)
        with pytest.raises(HTTPException) as exc:
            cookie.aggiorna(a[0], replace(a[1], utente_id=estraneo.utente_id), a[2])
        assert exc.value.status_code == 403
        p = chat[0]
        p.utente_id = None; p.cliente_emittente_aderente_id = p.cliente_id; db.commit()
        with pytest.raises(HTTPException) as exc:
            cookie.aggiorna(*a)
        assert exc.value.status_code == 403
    finally:
        socket_operazioni.chiudi(a[2]); socket_operazioni.chiudi(b[1])


def test_socket_cookie_applica_quote_comuni(client, db, chat, universo, monkeypatch):
    from src.chat_pratiche.configurazione import configurazione
    monkeypatch.setenv("REALTIME_MAX_CONNECTIONS_PER_AUTH_SESSION", "1")
    configurazione.cache_clear()
    a = socket_cookie(client, db, chat)
    try:
        with pytest.raises(HTTPException) as exc:
            socket_cookie(client, db, chat)
        assert exc.value.status_code == 429
    finally:
        socket_operazioni.chiudi(a[2])
        configurazione.cache_clear()


def test_socket_invia_presenza_pulisce_lease_e_storico_espone_autore_id(client, db, chat, universo):
    p, account, _ = chat
    with collega(client, p.pratica_id) as ws:
        assert ws.receive_json() == {"tipo": "connesso"}
        assert ws.receive_json() == {"tipo": "presenza", "utenti": [str(account.utente_id)]}
        ws.send_json(preparato(client, p.pratica_id))
        assert ws.receive_json()["tipo"] == "messaggio"
        # Aspetta la chiusura del server, che completa prima il cleanup SQL.
        ws.close()
        with pytest.raises(WebSocketDisconnect):
            ws.receive_json()
    with SessionLocal() as check:
        assert account.utente_id not in presenza.online_utenti(check)
    m = client.get(f"/pratiche/{p.pratica_id}/messaggi").json()["elementi"][0]
    assert m["autoreId"] == str(account.utente_id)
    assert m["mio"] is True


def test_cookie_non_blocca_quorum_ack_del_trasporto_bearer(client, db, chat, universo):
    a = socket_cookie(client, db, chat)
    b = socket_operazioni.avvia(universo[0])
    try:
        comando = preparato(client, chat[0].pratica_id)
        from src.chat_pratiche.socket_nativo import invia
        invia(a[0], a[1], comando)
        frames, _, _ = socket_operazioni.aggiorna(universo[0], (b[1], b[2]), b[3], True)
        ricevuti = [f for f in frames if f["payload"].get("deliveryId")]
        assert ricevuti
        for frame in ricevuti:
            did = frame["payload"]["deliveryId"]
            assert socket_operazioni.prepara(universo[0], (b[1], did))
            socket_operazioni.conferma(universo[0], (b[1], did))
        with SessionLocal() as check:
            assert check.scalar(text("SELECT COUNT(*) FROM realtime_delivery_connessione WHERE connessione=:c"), dict(c=a[2])) == 0
            assert check.scalar(text("SELECT COUNT(*) FROM realtime_delivery WHERE recipient_user_id=:u AND acknowledged_at IS NULL"), dict(u=chat[1].utente_id)) == 0
    finally:
        socket_operazioni.chiudi(a[2]); socket_operazioni.chiudi(b[1])
