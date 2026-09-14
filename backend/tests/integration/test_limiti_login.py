"""Limiti reali su MariaDB: concorrenza, IP, account e durata progressiva."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi import HTTPException
from sqlalchemy import select, text

from src.auth.limiti_login import LimiteLogin, chiave_limite, prenota_tentativo
from src.config import get_impostazioni
from src.security.password import hash_password
from tests.support import factories as f

pytestmark = pytest.mark.mariadb


def login(client, username="sconosciuto", password="errata"):
    return client.post("/auth/login", json={"utente_username": username, "utente_password": password})


def sblocca(db):
    db.execute(text("UPDATE auth_login_limite SET prossimo_tentativo = NOW(6) - INTERVAL 1 SECOND"))
    db.commit()


def test_attesa_progressiva_persistente_e_finestra(client, db):
    for _ in range(5):
        assert login(client).status_code == 401
    for secondi in (1, 2, 4, 8, 16, 32, 60):
        negata = login(client)
        assert negata.status_code == 429
        assert int(negata.headers["Retry-After"]) == secondi
        sblocca(db)
        assert login(client).status_code == 401
    # Un nuovo worker deve vedere lo stesso stato dal database.
    get_impostazioni.cache_clear()
    assert login(client).status_code == 429
    db.execute(text("UPDATE auth_login_limite SET finestra_inizio = NOW(6) - INTERVAL 16 MINUTE"))
    db.commit()
    assert login(client).status_code == 401


def test_stesso_account_da_ip_diversi_e_varianti(client_da, db):
    primo = client_da("203.0.113.1")
    secondo = client_da("203.0.113.2")
    for _ in range(5):
        assert login(primo, "Caffè").status_code == 401
    assert login(secondo, "CAFFE ").status_code == 429
    assert login(secondo, "altro-account").status_code == 401
    chiavi = db.execute(select(LimiteLogin.chiave)).scalars().all()
    assert all(len(c) == 64 and "caffe" not in c for c in chiavi)


def test_varianti_della_collation_legacy_non_aggirano_il_limite(client_da, db):
    f.crea_attuatore(db, username="coeur", email="collation@example.org",
                    password_hash=hash_password("password-valida"))
    for variante in ("coeur", "cœur", "COEUR ", "co\u200beur", "cœur"):
        assert db.execute(text("SELECT utente_id FROM utenti WHERE utente_username=:nome"),
                          {"nome": variante}).scalar_one() is not None
        assert login(client_da("203.0.113.1"), variante).status_code == 401
    assert login(client_da("203.0.113.2"), "cœur").status_code == 429


def test_ip_aggrega_account_diversi_e_header_non_falsifica_ip(client, db, monkeypatch):
    monkeypatch.setattr(get_impostazioni(), "login_tentativi_ip", 3)
    for n in range(3):
        assert login(client, f"account-{n}").status_code == 401
    risposta = client.post("/auth/login", json={"utente_username": "quarto", "utente_password": "x"},
                           headers={"X-Forwarded-For": "198.51.100.10"})
    assert risposta.status_code == 429


def test_successo_azzera_account_ma_non_ip(client, db):
    utente = f.crea_attuatore(db, username="conto", email="conto@example.org", password_hash=hash_password("password-valida"))
    for _ in range(4):
        assert login(client, utente.username).status_code == 401
    assert login(client, utente.username, "password-valida").status_code == 200
    assert db.get(LimiteLogin, chiave_limite("account", "conto")) is None
    assert db.execute(select(LimiteLogin.tentativi)).scalar_one() == 5
    assert login(client, utente.username).status_code == 401


def test_prenotazioni_simultanee_non_superano_soglia(db_pulito):
    barriera = Barrier(10)

    def tenta(n):
        barriera.wait(timeout=10)
        try:
            prenota_tentativo("stesso-account", bytes([203, 0, 113, n + 1]))
            return 200
        except HTTPException as errore:
            return errore.status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        esiti = list(pool.map(tenta, range(10)))
    assert esiti.count(200) == 5
    assert esiti.count(429) == 5
