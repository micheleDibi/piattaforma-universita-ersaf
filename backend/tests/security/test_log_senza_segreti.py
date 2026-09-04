"""Nei log non devono finire token, impronte, hash o indirizzi email."""

from __future__ import annotations

import logging
import re

import pytest

from src.logging_config import FiltroRedazione, FormatterRedatto, redigi
from src.security.password import hash_password
from src.security.tokens import TipoToken, genera_token, impronta
from tests.conftest import corpo_html
from tests.support import factories as f


def test_redazione_dei_valori_sensibili():
    token = genera_token()
    impronta_token = impronta(token, TipoToken.RESET)
    hash_bcrypt = hash_password("cavallo-batteria-graffetta")

    testo = (
        f"link https://x.it/reimposta-password?token={token} "
        f"impronta {impronta_token} hash {hash_bcrypt} "
        f"per mario.rossi@example.org"
    )
    redatto = redigi(testo)

    assert token not in redatto
    assert impronta_token not in redatto
    assert hash_bcrypt not in redatto
    assert "mario.rossi@example.org" not in redatto
    assert "[EMAIL-REDATTA]" in redatto


def test_redazione_delle_coppie_chiave_valore():
    redatto = redigi('utente_password="Segreto123" password_conferma=abc pepper: xyz')
    assert "Segreto123" not in redatto
    assert "abc" not in redatto
    assert "xyz" not in redatto


def test_le_righe_innocue_restano_leggibili():
    riga = "richiesta di reset elaborata, prr_id=42 esito=email_inviata"
    assert redigi(riga) == riga


def test_il_filtro_agisce_sul_record_gia_interpolato():
    token = genera_token()
    record = logging.LogRecord(
        "prova", logging.INFO, "x.py", 1, "token ricevuto: %s", (token,), None
    )
    FiltroRedazione().filter(record)
    assert token not in record.getMessage()
    assert "[TOKEN-REDATTO]" in record.getMessage()


def test_il_formatter_redige_anche_il_traceback():
    """logging.Filter agisce PRIMA che l'exc_info venga reso: un traceback di
    SQLAlchemy contiene "[parameters: (...)]", cioe' l'impronta del token."""
    impronta_token = impronta(genera_token(), TipoToken.RESET)
    try:
        raise ValueError(f"StatementError [parameters: ('{impronta_token}',)]")
    except ValueError:
        import sys

        record = logging.LogRecord(
            "prova", logging.ERROR, "x.py", 1, "errore", (), sys.exc_info()
        )
    reso = FormatterRedatto("%(message)s").format(record)
    assert impronta_token not in reso
    assert "[IMPRONTA-REDATTA]" in reso


@pytest.mark.mariadb
def test_il_flusso_completo_non_logga_segreti(client, db, mailer, caplog):
    """Il flusso reale, con la redazione attiva sull'handler di caplog."""
    caplog.handler.addFilter(FiltroRedazione())
    caplog.set_level(logging.DEBUG)

    email = "riservato@example.org"
    f.crea_attuatore(db, email=email)
    client.post("/auth/password-reset/request", json={"email": email})

    token = corpo_html(mailer.inviate[-1]).split("token=")[1].split('"')[0].split("<")[0]
    client.get("/auth/password-reset/validate", params={"token": token})
    client.post(
        "/auth/password-reset/confirm",
        json={
            "token": token,
            "password": "cavallo-batteria-graffetta",
            "password_conferma": "cavallo-batteria-graffetta",
        },
    )

    registrato = "\n".join(r.getMessage() for r in caplog.records)
    assert token not in registrato
    assert impronta(token, TipoToken.RESET) not in registrato
    assert email not in registrato
    assert "cavallo-batteria-graffetta" not in registrato
    # E resta comunque diagnosticabile.
    assert "prr_id=" in registrato


def test_nessun_valore_sensibile_sfugge_al_pattern_dei_token():
    """Il pattern del token e' ancorato ai 43 caratteri di token_urlsafe(32):
    se cambiasse la lunghezza, la redazione smetterebbe di funzionare in
    silenzio."""
    for _ in range(200):
        token = genera_token()
        assert len(token) == 43
        assert re.fullmatch(r"[A-Za-z0-9_-]{43}", token)
        assert token not in redigi(f"valore {token} fine")


def test_la_redazione_non_storpia_la_riga():
    """Due regole che si sovrappongono producevano "token=[REDATTO]]]": il
    valore spariva comunque, ma il log diventava illeggibile proprio dove
    serve leggerlo."""
    token = genera_token()
    riga = f'GET /auth/password-reset/validate?token={token} HTTP/1.1" 200'
    redatto = redigi(riga)

    assert redatto == 'GET /auth/password-reset/validate?token=[REDATTO] HTTP/1.1" 200'
    assert "]]" not in redatto
    assert redatto.count("[REDATTO]") == 1
