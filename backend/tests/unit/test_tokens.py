"""Generazione e impronta dei token."""

from __future__ import annotations

import pytest

from src.errori import ErroreConfigurazione
from src.security.tokens import (
    LUNGHEZZA_IMPRONTA,
    LUNGHEZZA_TOKEN,
    TipoToken,
    confronta_impronte,
    forma_token_valida,
    genera_token,
    impronta,
)


def test_forma_del_token():
    token = genera_token()
    assert len(token) == LUNGHEZZA_TOKEN
    assert set(token) <= set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    )


def test_i_token_sono_tutti_distinti():
    assert len({genera_token() for _ in range(2000)}) == 2000


def test_impronta_e_sha256_esadecimale_minuscolo():
    """La forma e' imposta dalle migrazioni 002 e 004: CHAR(64) ascii_bin."""
    valore = impronta(genera_token(), TipoToken.RESET)
    assert len(valore) == LUNGHEZZA_IMPRONTA
    assert valore == valore.lower()
    assert all(c in "0123456789abcdef" for c in valore)


def test_impronta_stabile_e_dipendente_dal_pepper():
    token = genera_token()
    assert impronta(token, TipoToken.RESET) == impronta(token, TipoToken.RESET)
    # Pepper diverse -> impronte diverse: e' il motivo per cui la
    # configurazione rifiuta due pepper uguali.
    assert impronta(token, TipoToken.RESET) != impronta(token, TipoToken.SESSIONE)


def test_impronta_non_contiene_il_token():
    token = genera_token()
    assert token not in impronta(token, TipoToken.RESET)


def test_impronta_dell_identificativo_email():
    """La 003 salva SHA-256 dell'email normalizzata, mai l'indirizzo in chiaro,
    con lo stesso pepper della 002."""
    normalizzata = "mario.rossi@example.org"
    assert impronta(normalizzata, TipoToken.RESET) != normalizzata
    assert impronta(" Mario.Rossi@Example.ORG ".strip().lower(), TipoToken.RESET) == (
        impronta(normalizzata, TipoToken.RESET)
    )


@pytest.mark.parametrize(
    "valore", [None, "", "corto", "a" * 42, "a" * 44, "con spazio " + "a" * 32, "<script>"]
)
def test_forma_token_valida_scarta_la_spazzatura(valore):
    assert not forma_token_valida(valore)


def test_forma_token_valida_accetta_i_nostri():
    assert forma_token_valida(genera_token())


def test_pepper_mancante_e_un_errore_di_configurazione(monkeypatch):
    """Difesa in profondita': se qualcuno costruisce TestClient(app) senza il
    context manager, il lifespan non gira e la verifica non viene eseguita."""
    from src.config import get_impostazioni

    monkeypatch.setattr(get_impostazioni(), "password_reset_token_pepper", "corta")
    with pytest.raises(ErroreConfigurazione):
        impronta("x", TipoToken.RESET)


def test_confronto_a_tempo_costante():
    a = impronta("x", TipoToken.RESET)
    assert confronta_impronte(a, a)
    assert not confronta_impronte(a, impronta("y", TipoToken.RESET))
