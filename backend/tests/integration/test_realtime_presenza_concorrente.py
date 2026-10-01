"""Due sessioni dello stesso utente rinnovano lease e confermano il quorum."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import text
from src.realtime import socket_operazioni
from tests.integration.test_realtime_completo import comando, domini, token_per  # noqa: F401
from tests.support.realtime import chat, pratica, universo  # noqa: F401

pytestmark = pytest.mark.mariadb


def test_rinnovo_presenza_e_ack_su_sessioni_distinte(client, db, universo, domini):
    _, mittente, destinatario, _ = domini
    tokens = [token_per(db, destinatario.utente_id) for _ in range(2)]
    connessioni = [socket_operazioni.avvia(t) for t in tokens]
    inviati = {
        socket_operazioni.elabora(
            universo[0],
            comando(client, universo[0], mittente.utente_id, "PERSON", destinatario.utente_id, cid=f"concorrenza{n}"),
        )["payload"]["messaggioId"]
        for n in range(8)
    }
    insieme = Barrier(2)

    def ricevi(t, c):
        ricevuti = set()
        for _ in range(8):
            insieme.wait(timeout=15)
            frames, _, _ = socket_operazioni.aggiorna(t, (c[1], c[2]), c[3], True)
            for frame in frames:
                p = frame["payload"]
                if socket_operazioni.prepara(t, (c[1], p["deliveryId"])):
                    socket_operazioni.conferma(t, (c[1], p["deliveryId"]))
                    if frame["channel"] == "chat":
                        ricevuti.add(p["messaggioId"])
        return ricevuti

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            lavori = [pool.submit(ricevi, t, c) for t, c in zip(tokens, connessioni)]
            assert [r.result(timeout=60) for r in lavori] == [inviati, inviati]
        db.expire_all()
        assert db.scalar(text(
            "SELECT COUNT(*) FROM realtime_delivery WHERE recipient_user_id=:u AND acknowledged_at IS NULL"
        ), dict(u=destinatario.utente_id)) == 0
    finally:
        for c in connessioni:
            socket_operazioni.chiudi(c[1])
