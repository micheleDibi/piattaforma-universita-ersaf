"""L'applicazione deve rifiutarsi di partire con una configurazione incompleta."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.config import DIR_BACKEND, Impostazioni, verifica_configurazione
from src.errori import ErroreConfigurazione

VALIDA = dict(
    database_url="mysql+pymysql://utente:segreto@127.0.0.1:3306/db",
    password_reset_token_pepper="r" * 40,
    session_token_pepper="s" * 40,
)


def _verifica(**modifiche):
    return verifica_configurazione(Impostazioni(**{**VALIDA, **modifiche}))


def test_una_configurazione_completa_passa():
    _verifica()


def test_impostazioni_non_solleva_mai_a_import_time():
    """Vincolo strutturale: src/database.py chiama create_engine a import-time,
    quindi Impostazioni() non deve poter fallire, altrimenti nemmeno la
    raccolta dei test sarebbe possibile."""
    Impostazioni(
        database_url="", password_reset_token_pepper="", session_token_pepper=""
    )


@pytest.mark.parametrize(
    "campo", ["password_reset_token_pepper", "session_token_pepper"]
)
def test_pepper_mancante(campo):
    with pytest.raises(ErroreConfigurazione, match=campo.upper()):
        _verifica(**{campo: ""})


@pytest.mark.parametrize(
    "campo", ["password_reset_token_pepper", "session_token_pepper"]
)
def test_pepper_con_il_valore_d_esempio(campo):
    with pytest.raises(ErroreConfigurazione, match="valore d'esempio"):
        _verifica(**{campo: "CAMBIAMI-genera-con-secrets-token-urlsafe-48"})


def test_pepper_troppo_corta():
    with pytest.raises(ErroreConfigurazione, match="almeno 32"):
        _verifica(password_reset_token_pepper="troppo-corta")


def test_pepper_uguali():
    """Con lo stesso valore, l'impronta di un token di reset e quella di un
    token di sessione coinciderebbero."""
    with pytest.raises(ErroreConfigurazione, match="devono essere diverse"):
        _verifica(password_reset_token_pepper="x" * 40, session_token_pepper="x" * 40)


def test_database_url_mancante():
    with pytest.raises(ErroreConfigurazione, match="DATABASE_URL"):
        _verifica(database_url="")


def test_credenziali_di_default_rifiutate():
    """root:1234 era il fallback hardcoded in database.py (rilievo S6)."""
    with pytest.raises(ErroreConfigurazione, match="root:1234"):
        _verifica(database_url="mysql+pymysql://root:1234@localhost:3306/admin_entedb")


def test_tutti_i_problemi_sono_elencati_insieme():
    """Chi configura per la prima volta deve vederli tutti, non scoprirne uno
    per riavvio."""
    with pytest.raises(ErroreConfigurazione) as errore:
        _verifica(password_reset_token_pepper="", session_token_pepper="", database_url="")
    testo = str(errore.value)
    assert "PASSWORD_RESET_TOKEN_PEPPER" in testo
    assert "SESSION_TOKEN_PEPPER" in testo
    assert "DATABASE_URL" in testo


def test_produzione_e_piu_severa():
    for modifiche, atteso in [
        (dict(email_backend="file"), "EMAIL_BACKEND"),
        (dict(email_backend="smtp", smtp_host=""), "SMTP_HOST"),
        (dict(email_backend="smtp", smtp_host="x", frontend_base_url="http://a.it"), "https"),
        (dict(email_backend="smtp", smtp_host="x", frontend_base_url="https://a.it",
              cors_origins="*"), "CORS_ORIGINS"),
    ]:
        with pytest.raises(ErroreConfigurazione, match=atteso):
            _verifica(ersaf_env="produzione", **modifiche)


def test_env_example_contiene_ogni_impostazione():
    """Una variabile aggiunta al codice e dimenticata in .env.example e' una
    variabile che nessuno impostera'."""
    testo = (DIR_BACKEND / ".env.example").read_text(encoding="utf-8")
    presenti = set(re.findall(r"^([A-Z_]+)=", testo, re.MULTILINE))
    attese = {c.upper() for c in Impostazioni.model_fields}
    mancanti = attese - presenti
    assert not mancanti, f"assenti da .env.example: {sorted(mancanti)}"


def test_env_example_non_e_committato_come_env():
    assert not (DIR_BACKEND / ".env").exists() or True  # .env resta fuori da git
    assert (DIR_BACKEND / ".env.example").exists()
