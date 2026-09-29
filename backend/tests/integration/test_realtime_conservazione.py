"""Compatibilita del produttore e confini della pulizia dei metadati."""

import json
import uuid
from datetime import timedelta

import pytest
from sqlalchemy import text
from src.database import SessionLocal
from src.realtime import accesso, api_notifiche, attenzione, manutenzione, socket_operazioni
from src.realtime.dati import ora
from src.realtime.errori import ErroreRealtime
from src.realtime.identita import carica
from tests.integration.test_realtime_completo import comando, domini  # noqa: F401
from tests.support import factories as f
from tests.support.realtime import chat, pratica, universo  # noqa: F401

pytestmark = pytest.mark.mariadb


def richiesta(target, autore):
    return dict(
        producerEventId=str(uuid.uuid1()).upper(),
        target=float(target),
        createdBy=autore,
        operation="aggiornamento",
        idRef="123",
        title=" Titolo ",
        message=" Testo\nprova ",
    )


def test_produttore_accetta_autore_attivo_senza_cliente_e_normalizza_evento(db, universo, domini):
    autore = f.crea_utente_orfano(db)
    _, target, _, _ = domini
    dati = richiesta(target.utente_id, autore.utente_id)
    primo = api_notifiche.invia(dati)
    assert primo.status_code == 201
    risposta = json.loads(primo.body)
    assert risposta["producerEventId"] == dati["producerEventId"].lower()
    retry = api_notifiche.invia(dict(dati, title="Titolo", message="Testo\nprova"))
    assert retry.status_code == 200
    assert json.loads(retry.body)["notificationId"] == risposta["notificationId"]
    db.expire_all()
    assert db.scalar(text("SELECT COUNT(*) FROM notifiche")) == 1


@pytest.mark.parametrize("non_valido", ["destinatario_orfano", "autore_disattivo"])
def test_produttore_verifica_identita_prima_di_scrivere(db, universo, domini, non_valido):
    _, target, autore, _ = domini
    orfano = f.crea_utente_orfano(db, attivo=0 if non_valido == "autore_disattivo" else -1)
    dati = richiesta(
        orfano.utente_id if non_valido == "destinatario_orfano" else target.utente_id,
        orfano.utente_id if non_valido == "autore_disattivo" else autore.utente_id,
    )
    with pytest.raises(ErroreRealtime) as errore:
        api_notifiche.invia(dati)
    assert errore.value.status_code == 422
    db.expire_all()
    for tabella in (
        "notifiche",
        "notifiche_parameters",
        "realtime_notification_command",
        "realtime_delivery",
    ):
        assert db.scalar(text("SELECT COUNT(*) FROM " + tabella)) == 0


def test_pulizia_sessioni_attende_sia_retention_revoca_sia_scadenza_refresh(db, universo):
    identita = carica(db, universo[1]["sub"])
    adesso = ora()
    casi = ((-40, 50, True), (-1, -40, True), (-40, -1, False))
    attesi = {}
    for revoca, scadenza, conserva in casi:
        s, _ = accesso.nuova_sessione(db, identita, str(uuid.uuid4()))
        attesi[s["session_id"]] = conserva
        db.execute(
            text("""UPDATE realtime_auth_session SET revoked_at=:r,revocation_reason='LOGOUT',
                 refresh_expires_at=:e WHERE session_id=:s"""),
            dict(r=adesso + timedelta(days=revoca), e=adesso + timedelta(days=scadenza), s=s["session_id"]),
        )
    db.commit()
    with SessionLocal.begin() as tx:
        manutenzione.pulisci(tx)
    presenti = set(db.execute(text("SELECT session_id FROM realtime_auth_session")).scalars())
    assert all((sid in presenti) == conserva for sid, conserva in attesi.items())


def test_scadenza_ricevute_non_cancella_messaggi_chiavi_o_stati(client, db, universo, domini):
    _, mittente, destinatario, _ = domini
    dati = comando(client, universo[0], mittente.utente_id, "PERSON", destinatario.utente_id)
    payload = socket_operazioni.elabora(universo[0], dati)["payload"]
    attenzione.leggi_messaggio(db, carica(db, destinatario.utente_id), "PERSON", int(payload["messaggioId"]))
    db.commit()
    protette = ("messaggio", "realtime_message_key_grant", "realtime_message_state", "notifiche")
    prima = {nome: db.scalar(text("SELECT COUNT(*) FROM " + nome)) for nome in protette}
    assert all(prima.values())
    for nome in ("realtime_delivery", "realtime_message_command"):
        db.execute(text("UPDATE " + nome + " SET expires_at=UTC_TIMESTAMP()-INTERVAL 1 DAY"))
    db.commit()
    with SessionLocal.begin() as tx:
        manutenzione.pulisci(tx)
    assert prima == {nome: db.scalar(text("SELECT COUNT(*) FROM " + nome)) for nome in protette}
    for nome in ("realtime_delivery", "realtime_message_command"):
        assert db.scalar(text("SELECT COUNT(*) FROM " + nome)) == 0
