"""Nessun percorso di codice scrive una password in chiaro.

Il criterio di accettazione e' formulato come un grep, che e' debole: dipende
da quali percorsi sono stati eseguiti al momento del controllo. Qui si usano
tre meccanismi complementari — una sentinella a runtime, una post-condizione
sul database e una scansione del sorgente.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from sqlalchemy import event, select

from src.config import DIR_BACKEND
from src.database import engine
from src.security.password import hash_password, verify_password
from src.utenti.models import Utente
from src.utenti.schemas import UtenteUpdate
from tests.support import factories as f

PASSWORD = "cavallo-batteria-graffetta"
SENTINELLA = "SegretoDaNonScrivereMai2026"


@pytest.fixture
def guardia_plaintext():
    """Fallisce se una password nota compare fra i parametri di una scrittura.

    Coglie QUALUNQUE percorso di codice esercitato dai test, presente o futuro,
    senza sapere in anticipo dove guardare. E' la differenza fra "abbiamo
    controllato i punti che ci sono venuti in mente" e "nessuno dei flussi
    provati lo fa".
    """
    intercettate: list[str] = []

    def _valori(parametri):
        if isinstance(parametri, dict):
            return list(parametri.values())
        if isinstance(parametri, (list, tuple)):
            fuori = []
            for elemento in parametri:
                if isinstance(elemento, (list, tuple, dict)):
                    fuori.extend(_valori(elemento))
                else:
                    fuori.append(elemento)
            return fuori
        return [parametri]

    def ascolta(conn, cursor, statement, parameters, context, executemany):
        if "utenti" not in statement.lower():
            return
        for valore in _valori(parameters):
            if isinstance(valore, str) and SENTINELLA in valore:
                intercettate.append(statement[:160])

    event.listen(engine, "before_cursor_execute", ascolta)
    try:
        yield intercettate
    finally:
        event.remove(engine, "before_cursor_execute", ascolta)


@pytest.mark.mariadb
def test_creazione_utente_non_scrive_la_password_in_chiaro(client, db, guardia_plaintext):
    attuatore = f.crea_attuatore(
        db, email="admin@example.org", password_hash=hash_password(PASSWORD)
    )
    accesso = client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    token = accesso.json()["token"]

    risposta = client.post(
        "/utenti/",
        json={"utente_username": "nuovo-utente", "utente_password": SENTINELLA},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert risposta.status_code == 201
    assert guardia_plaintext == [], f"password in chiaro in: {guardia_plaintext}"

    db.commit()
    creato = db.execute(
        select(Utente).where(Utente.utente_username == "nuovo-utente")
    ).scalar_one()
    assert creato.utente_password == ""
    assert creato.utente_password_algo == "bcrypt"
    assert verify_password(SENTINELLA, creato.utente_password_hash)


@pytest.mark.mariadb
def test_aggiornamento_utente_non_puo_toccare_la_password(client, db, guardia_plaintext):
    """Il PUT accettava UtenteCreate e un ciclo di setattr scriveva la password
    in chiaro a ogni aggiornamento."""
    attuatore = f.crea_attuatore(
        db, email="admin2@example.org", password_hash=hash_password(PASSWORD)
    )
    accesso = client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    token = accesso.json()["token"]
    hash_prima = db.get(Utente, attuatore.utente_id).utente_password_hash

    risposta = client.put(
        f"/utenti/{attuatore.utente_id}",
        json={"utente_username": "rinominato", "utente_password": SENTINELLA},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert risposta.status_code == 200
    assert guardia_plaintext == []

    db.commit()
    db.expire_all()
    dopo = db.get(Utente, attuatore.utente_id)
    assert dopo.utente_username == "rinominato"       # il campo lecito cambia
    assert dopo.utente_password_hash == hash_prima     # la password no
    assert dopo.utente_password == ""


def test_lo_schema_di_aggiornamento_non_espone_la_password():
    assert "utente_password" not in UtenteUpdate.model_fields
    assert "utente_salt" not in UtenteUpdate.model_fields


@pytest.mark.mariadb
def test_nessun_utente_con_hash_e_chiaro_insieme(client, db):
    """Post-condizione: un hash presente insieme al chiaro significa che il
    codice ha scritto l'hash senza ripulire il legacy. E' la query 4 della
    diagnostica 010."""
    attuatore = f.crea_attuatore(db, email="legacy@example.org", password_chiaro=PASSWORD)
    client.post(
        "/auth/login",
        json={"utente_username": attuatore.username, "utente_password": PASSWORD},
    )
    db.commit()
    incoerenti = db.execute(
        select(Utente).where(
            Utente.utente_password_hash.isnot(None), Utente.utente_password != ""
        )
    ).all()
    assert incoerenti == []


# --- analisi statica del sorgente -------------------------------------------

# Le uniche due posizioni in cui e' lecito scrivere utenti.utente_password:
# il rehash pigro al login e la conferma del reset. Piu' la creazione, che ci
# scrive la stringa vuota.
POSIZIONI_AMMESSE = {
    "src/auth/servizio_login.py",
    "src/auth/servizio_reset.py",
    "src/utenti/routers.py",
}


def _file_sorgente() -> list[Path]:
    return sorted((DIR_BACKEND / "src").rglob("*.py"))


def test_scritture_su_utente_password_solo_dove_previsto():
    trovate: list[str] = []
    for percorso in _file_sorgente():
        albero = ast.parse(percorso.read_text(encoding="utf-8"), str(percorso))
        relativo = str(percorso.relative_to(DIR_BACKEND))
        for nodo in ast.walk(albero):
            scrive = False
            if isinstance(nodo, ast.Assign):
                for bersaglio in nodo.targets:
                    if isinstance(bersaglio, ast.Attribute) and (
                        bersaglio.attr == "utente_password"
                    ):
                        scrive = True
            if isinstance(nodo, ast.keyword) and nodo.arg == "utente_password":
                scrive = True
            if scrive and relativo not in POSIZIONI_AMMESSE:
                trovate.append(f"{relativo}:{nodo.lineno}")
    assert not trovate, f"scritture su utente_password fuori dalle posizioni ammesse: {trovate}"


def test_nessuno_script_modifica_le_password_in_blocco():
    """Traduzione in test del divieto: nessuna operazione massiva, mai."""
    sospette: list[str] = []
    # scripts/ e' incluso: e' l'unico posto del repo dove qualcuno potrebbe
    # essere tentato di scrivere un "aggiorniamo tutte le password".
    radici = [DIR_BACKEND / "src", DIR_BACKEND / "scripts", DIR_BACKEND.parent / "db"]
    for radice in radici:
        if not radice.exists():
            continue
        for percorso in sorted(radice.rglob("*")):
            if percorso.suffix not in (".py", ".sql") or not percorso.is_file():
                continue
            testo = percorso.read_text(encoding="utf-8", errors="ignore")
            for numero, riga in enumerate(testo.splitlines(), 1):
                spoglia = riga.strip()
                if spoglia.startswith(("--", "#")):
                    continue
                minuscola = spoglia.lower()
                if "update" in minuscola and "utenti" in minuscola and (
                    "utente_password" in minuscola or "utente_password_hash" in minuscola
                ):
                    if "utente_id" not in minuscola:
                        sospette.append(f"{percorso}:{numero}: {spoglia[:90]}")
    assert not sospette, f"possibile aggiornamento massivo: {sospette}"
