"""Le migrazioni su un database pulito: applicazione, idempotenza, rollback.

Girano su un database usa-e-getta, non su quello condiviso dal resto della
suite: applicano e annullano DDL, e non devono lasciare macerie.
"""

from __future__ import annotations

import os

import pytest
import sqlalchemy as sa
from sqlalchemy.engine import make_url

from tests.conftest import MIGRAZIONI, RADICE, SCHEMA_BASE
from tests.support.sqlrunner import esegui_file_sql, esegui_sql

pytestmark = pytest.mark.mariadb

ROLLBACK = sorted((RADICE / "db" / "rollback").glob("*.sql"), reverse=True)

INTERROGAZIONE_SCHEMA = """
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
  FROM information_schema.COLUMNS  WHERE TABLE_SCHEMA = :schema
UNION ALL
SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME, '', ''
  FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = :schema
UNION ALL
SELECT TABLE_NAME, CONSTRAINT_NAME, CONSTRAINT_TYPE, '', ''
  FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = :schema
UNION ALL
SELECT 'evento', EVENT_NAME, '', '', ''
  FROM information_schema.EVENTS WHERE EVENT_SCHEMA = :schema
"""


def _istantanea(url: str) -> set[tuple]:
    nome = make_url(url).database
    motore = sa.create_engine(url)
    try:
        with motore.connect() as connessione:
            righe = connessione.execute(
                sa.text(INTERROGAZIONE_SCHEMA), {"schema": nome}
            ).all()
    finally:
        motore.dispose()
    # Insieme e non lista: l'ordine di information_schema non e' garantito e
    # confrontarlo produrrebbe differenze inventate.
    return {tuple("" if v is None else str(v) for v in r) for r in righe}


@pytest.fixture
def database_vergine():
    """Solo ersaf_test locale, con ripristino dello schema dopo ogni prova DDL."""
    url = os.environ["TEST_DATABASE_URL"]
    esegui_sql(url, "DROP DATABASE IF EXISTS ersaf_test; "
               "CREATE DATABASE ersaf_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    try:
        yield url
    finally:
        esegui_file_sql(url, SCHEMA_BASE)
        for migrazione in MIGRAZIONI:
            esegui_file_sql(url, migrazione)


def test_migrazioni_su_database_pulito(database_vergine):
    esegui_file_sql(database_vergine, SCHEMA_BASE)
    for migrazione in MIGRAZIONI:
        esegui_file_sql(database_vergine, migrazione)

    motore = sa.create_engine(database_vergine)
    try:
        with motore.connect() as connessione:
            tabelle = {
                r[0]
                for r in connessione.execute(sa.text("SHOW TABLES")).all()
            }
            template = connessione.execute(
                sa.text(
                    "SELECT messaggio_email_codice FROM messaggi_email "
                    "WHERE messaggio_email_codice LIKE 'password_reset%'"
                )
            ).scalars().all()
            colonne = {
                r[0]
                for r in connessione.execute(
                    sa.text("SHOW COLUMNS FROM utenti LIKE 'utente_password%'")
                ).all()
            }
    finally:
        motore.dispose()

    assert {
        "password_reset_token", "password_reset_richiesta", "auth_sessione",
        "auth_totp", "auth_passkey", "auth_mfa_utente",
    } <= tabelle
    assert sorted(template) == ["password_reset_eseguito", "password_reset_richiesta"]
    assert colonne == {
        "utente_password",
        "utente_password_hash",
        "utente_password_algo",
        "utente_password_changed_at",
        "utente_password_changed_via",
    }


def test_indici_della_visibilita(database_vergine):
    """La 016 aggiunge i due indici su cui poggia la CTE di visibilita':
    senza, ogni passo della ricorsione scansiona tutta `utenti`."""
    esegui_file_sql(database_vergine, SCHEMA_BASE)
    for migrazione in MIGRAZIONI:
        esegui_file_sql(database_vergine, migrazione)

    motore = sa.create_engine(database_vergine)
    try:
        with motore.connect() as connessione:
            righe = connessione.execute(sa.text(
                "SELECT TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME "
                "FROM information_schema.STATISTICS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND INDEX_NAME IN ('ix_utenti_padre', 'ix_clienti_azienda_utente')"
            )).all()
    finally:
        motore.dispose()

    assert sorted(tuple(r) for r in righe) == [
        ("clienti", "ix_clienti_azienda_utente", 1, "azienda_id"),
        ("clienti", "ix_clienti_azienda_utente", 2, "utente_id"),
        ("utenti", "ix_utenti_padre", 1, "utente_padre"),
    ]


def test_migrazioni_idempotenti(database_vergine):
    """Riapplicarle sopra se stesse non deve produrre errori ne' cambiare lo
    schema: e' cio' che rende sicuro rieseguire uno script interrotto a meta'.
    """
    esegui_file_sql(database_vergine, SCHEMA_BASE)
    for migrazione in MIGRAZIONI:
        esegui_file_sql(database_vergine, migrazione)
    prima = _istantanea(database_vergine)

    for migrazione in MIGRAZIONI:
        esegui_file_sql(database_vergine, migrazione)
    assert _istantanea(database_vergine) == prima


def test_rollback_riporta_allo_stato_iniziale(database_vergine):
    esegui_file_sql(database_vergine, SCHEMA_BASE)
    prima = _istantanea(database_vergine)

    for migrazione in MIGRAZIONI:
        esegui_file_sql(database_vergine, migrazione)
    assert _istantanea(database_vergine) != prima, "le migrazioni non hanno fatto nulla"

    for annullamento in ROLLBACK:
        esegui_file_sql(database_vergine, annullamento)
    assert _istantanea(database_vergine) == prima


def test_enum_esiti_allineato_al_codice(database_vergine):
    """I valori della classe Esito devono coincidere con l'ENUM del database:
    scriverne uno non previsto darebbe un errore solo a runtime."""
    from src.auth.models import Esito

    esegui_file_sql(database_vergine, SCHEMA_BASE)
    for migrazione in MIGRAZIONI:
        esegui_file_sql(database_vergine, migrazione)

    motore = sa.create_engine(database_vergine)
    try:
        with motore.connect() as connessione:
            tipo = connessione.execute(
                sa.text(
                    "SELECT COLUMN_TYPE FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() "
                    "AND TABLE_NAME = 'password_reset_richiesta' "
                    "AND COLUMN_NAME = 'prr_esito'"
                )
            ).scalar_one()
    finally:
        motore.dispose()

    nel_database = set(tipo.removeprefix("enum(").removesuffix(")").replace("'", "").split(","))
    assert nel_database == {e.value for e in Esito}


def test_il_database_di_test_e_in_modalita_severa():
    """La suite deve girare nelle condizioni piu' severe fra quelle plausibili.

    Con una sql_mode permissiva un troncamento e' solo un avviso, mentre su
    un'installazione reale con STRICT_TRANS_TABLES lo stesso statement
    fallisce. E' esattamente cosi' che un difetto in segna_ultimo_accesso e'
    passato inosservato: il container di test era piu' tollerante della
    macchina di chi ha poi eseguito il codice.
    """
    import sqlalchemy as sa

    from src.database import engine

    with engine.connect() as connessione:
        modo = connessione.execute(sa.text("SELECT @@SESSION.sql_mode")).scalar()
    assert "STRICT_TRANS_TABLES" in modo, (
        f"sql_mode del database di test troppo permissiva: {modo}. "
        "Vedi db/test/docker-compose.test.yml."
    )
