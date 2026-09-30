import base64

import pytest
from sqlalchemy import delete, text

from src.chat_pratiche.configurazione import configurazione, chiavi
from src.chat_pratiche.models import Messaggio, StatoMessaggio
from src.clienti.models import Cliente
from src.utenti.models import Utente
from src.security.browser import nome_cookie, token_csrf
from tests.integration.test_documento_pratica import pratica  # noqa: F401
from tests.support import factories as f
from tests.support.archivi_realtime import NOTIFICHE


@pytest.fixture
def chat(client, db, pratica, tmp_path, monkeypatch):
    client.headers["X-CSRF-Token"] = token_csrf(client.cookies.get(nome_cookie()))
    key = tmp_path / "chiave-test.txt"
    key.write_text(base64.b64encode(bytes(range(32))).decode(), encoding="ascii")
    monkeypatch.setenv("CHAT_CHIAVI_FILE", f"1={key}")
    configurazione.cache_clear()
    chiavi.cache_clear()
    # Sottoinsieme sintetico dei due archivi legacy usati dalle notifiche.
    for sql in NOTIFICHE:
        db.execute(text(sql))
    db.execute(delete(Messaggio))
    db.execute(delete(StatoMessaggio))
    for tabella in ("realtime_notification_bridge", "realtime_notification_seen", "realtime_message_command", "realtime_notification_command", "realtime_evento", "realtime_presenza", "realtime_flusso_utente", "realtime_limite", "notifiche", "notifiche_parameters", "realtime_message_state", "chat_pratica_comando", "chat_pratica_limite", "realtime_message_time", "realtime_message_key_grant", "realtime_delivery"):
        db.execute(text(f"DELETE FROM {tabella}"))
    db.add(StatoMessaggio(messaggio_stato_id=1, messaggio_stato_codice="NUOVO"))
    # La fixture PDF riusa l'utente del referente: qui servono due identità distinte.
    studente = db.get(Cliente, pratica.cliente_id)
    studente.utente_id = f.crea_utente(db, username="studentessa.chat").utente_id
    db.commit()
    account = db.get(Cliente, pratica.cliente_emittente_aderente_id)
    pratica.utente_id = account.utente_id
    db.commit()
    yield pratica, account, studente
    db.execute(delete(Messaggio))
    db.commit()
    configurazione.cache_clear()
    chiavi.cache_clear()
