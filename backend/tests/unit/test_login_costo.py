"""Ogni rifiuto deve svolgere una verifica bcrypt, anche per il legacy."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.auth import servizio_login
from src.auth.models import ATTIVO
from src.security.password import hash_password


@pytest.mark.parametrize("ramo", ["assente", "spento", "legacy", "bcrypt", "vuoto"])
def test_password_errata_esegue_bcrypt_senza_modificare_utente(monkeypatch, ramo):
    utente = SimpleNamespace(
        utente_attivoSN=ATTIVO, utente_password="password-legacy",
        utente_password_hash=None, utente_id=1,
    )
    if ramo == "assente":
        utente = None
    elif ramo == "spento":
        utente.utente_attivoSN = 0
    elif ramo == "bcrypt":
        utente.utente_password_hash = hash_password("password-esistente")
    elif ramo == "vuoto":
        utente.utente_password = ""
    verifica = Mock(wraps=servizio_login.verify_password)
    riscrivi = Mock()
    monkeypatch.setattr(servizio_login, "verify_password", verifica)
    monkeypatch.setattr(servizio_login, "riscrivi_hash", riscrivi)
    assert servizio_login.verifica_credenziali(Mock(), utente, "password-errata") is False
    verifica.assert_called_once()
    assert verifica.call_args.args[1].startswith("$2b$")
    riscrivi.assert_not_called()
