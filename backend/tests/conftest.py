"""Fixture condivise.

L'ORDINE DI QUESTO FILE E' VINCOLANTE. `src/database.py` chiama create_engine a
livello di modulo e SQLAlchemy importa subito il DBAPI: se DATABASE_URL non e'
gia' impostata quando `src.*` viene importato, la raccolta dei test punta al
database di sviluppo. Percio' l'ambiente si prepara nelle primissime righe,
prima di qualunque import di src.
"""

from __future__ import annotations

import functools
import os
from pathlib import Path

DIR_BACKEND = Path(__file__).resolve().parents[1]
RADICE = DIR_BACKEND.parent

URL_TEST_PREDEFINITA = "mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test"

os.environ.setdefault("TEST_DATABASE_URL", URL_TEST_PREDEFINITA)
os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

# Pepper di test, deliberatamente DIVERSE dai valori di .env.example: un test
# verifica che quei valori vengano rifiutati, e se il conftest li usasse come
# default quel test non potrebbe esistere.
os.environ.setdefault("PASSWORD_RESET_TOKEN_PEPPER", "pepper-di-test-reset-" + "r" * 32)
os.environ.setdefault("SESSION_TOKEN_PEPPER", "pepper-di-test-sessione-" + "s" * 32)

# Un hash a costo 12 richiede ~250 ms: con decine di login la suite diventerebbe
# inutilizzabile. Un solo test rialza il costo e verifica il prefisso $2b$12$.
os.environ.setdefault("BCRYPT_COST", "4")

os.environ.setdefault("EMAIL_BACKEND", "memoria")
os.environ.setdefault("FRONTEND_BASE_URL", "https://test.example.org")
os.environ.setdefault("SMTP_HOST", "smtp.invalid")  # RFC 6761: non risolve mai
os.environ.setdefault("PASSWORD_RESET_BUDGET_MS", "150")
os.environ.setdefault("LOG_FILE", "")  # nessun file di log durante i test
os.environ.setdefault("ERSAF_ENV", "test")

# --- da qui in poi si puo' importare src ------------------------------------
import pytest  # noqa: E402
import sqlalchemy as sa  # noqa: E402

from src.config import get_impostazioni  # noqa: E402

get_impostazioni.cache_clear()

MIGRAZIONI = sorted((RADICE / "db" / "migrations").glob("*.sql"))
SCHEMA_BASE = RADICE / "db" / "test" / "schema_base.sql"

# Ordine figlio -> padre. `ruoli` non compare: e' lookup, non stato.
TABELLE_DA_SVUOTARE = [
    "password_reset_token",
    "password_reset_richiesta",
    "auth_sessione",
    "clienti",
    "utenti",
    "aziende",
]


@functools.cache
def mariadb_disponibile() -> tuple[bool, str]:
    url = os.environ.get("TEST_DATABASE_URL", "")
    if not url:
        return False, "TEST_DATABASE_URL non impostata"
    try:
        import pymysql  # noqa: F401
    except ImportError:
        return False, "pymysql non installato (pip install -r requirements.txt)"
    try:
        # connect_timeout basso: senza, con un host irraggiungibile la sessione
        # resta appesa sul TCP per minuti.
        motore = sa.create_engine(url, connect_args={"connect_timeout": 3})
        with motore.connect() as connessione:
            connessione.execute(sa.text("SELECT 1"))
        motore.dispose()
    except Exception as errore:  # pragma: no cover - dipende dall'ambiente
        return False, f"connessione fallita ({type(errore).__name__})"
    return True, ""


def pytest_addoption(parser):
    parser.addoption(
        "--require-mariadb",
        action="store_true",
        help="fa fallire la sessione se i test che richiedono MariaDB non "
        "possono essere eseguiti. Da usare in CI: uno skip li' e' un errore.",
    )


def pytest_collection_modifyitems(config, items):
    disponibile, motivo = mariadb_disponibile()
    if disponibile:
        return
    if config.getoption("--require-mariadb"):
        pytest.exit(
            f"--require-mariadb richiesto ma MariaDB non e' utilizzabile: {motivo}",
            returncode=3,
        )
    salta = pytest.mark.skip(
        reason=f"MariaDB non disponibile ({motivo}). "
        "Avvia: docker compose -f db/test/docker-compose.test.yml up -d"
    )
    for elemento in items:
        if "mariadb" in elemento.keywords:
            elemento.add_marker(salta)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Il rischio numero uno di questa suite e' essere verde per skip."""
    disponibile, motivo = mariadb_disponibile()
    if disponibile:
        return
    saltati = len(terminalreporter.stats.get("skipped", []))
    terminalreporter.write_sep(
        "!",
        f"ATTENZIONE: {saltati} test NON eseguiti perche' MariaDB non e' "
        f"disponibile ({motivo}). Consumo concorrente del token, migrazioni, "
        f"ENUM, revoca delle sessioni e rate limit NON sono verificati.",
        red=True,
    )


# =============================================================================
# Fixture del database
# =============================================================================
from src.database import SessionLocal, engine  # noqa: E402
from tests.support.sqlrunner import esegui_file_sql  # noqa: E402


@pytest.fixture(scope="session")
def schema():
    # NON autouse: i test unitari (politica delle password, impronte, IP,
    # configurazione) non toccano il database e devono restare eseguibili
    # ovunque, anche senza Docker. Chi ha bisogno del database chiede `db` o
    # `client`, che dipendono da qui.
    """Ricostruisce lo schema una volta per sessione.

    schema_base.sql ricrea le cinque tabelle preesistenti (che le migrazioni
    presuppongono e che nessuna migrazione crea), poi si applicano le 001-008
    in ordine, esattamente come si farebbe in produzione. Far girare la suite
    e' quindi anche la prova che le migrazioni funzionano su un database
    pulito.
    """
    disponibile, motivo = mariadb_disponibile()
    if not disponibile:
        pytest.skip(f"MariaDB non disponibile: {motivo}", allow_module_level=True)
    url = os.environ["TEST_DATABASE_URL"]
    esegui_file_sql(url, SCHEMA_BASE)
    for migrazione in MIGRAZIONI:
        esegui_file_sql(url, migrazione)
    yield


@pytest.fixture
def db_pulito(schema):
    """Svuota le tabelle di stato prima di ogni test.

    SI USA TRUNCATE E NON UNA TRANSAZIONE CON ROLLBACK, che sarebbe il pattern
    canonico. Il motivo e' il test di consumo concorrente: ha bisogno di due
    connessioni che vedano i commit l'una dell'altra, e dentro un'unica
    transazione non committata il secondo thread non vedrebbe mai il token
    consumato dal primo — il test piu' importante della suite diventerebbe un
    falso positivo per costruzione. In piu' il flusso di conferma e' definito
    come "un'unica transazione", e verificarlo dentro un savepoint imposto dal
    test significherebbe verificare il savepoint.

    `ruoli` e `messaggi_email` non si toccano: sono dati di lookup e template,
    non stato. TRUNCATE azzera anche l'AUTO_INCREMENT, quindi gli id sono
    deterministici fra un test e l'altro.
    """
    with engine.begin() as connessione:
        connessione.execute(sa.text("SET FOREIGN_KEY_CHECKS = 0"))
        for tabella in TABELLE_DA_SVUOTARE:
            connessione.execute(sa.text(f"TRUNCATE TABLE `{tabella}`"))
        connessione.execute(sa.text("SET FOREIGN_KEY_CHECKS = 1"))
    yield


@pytest.fixture
def db(db_pulito):
    """Sessione per allestire lo scenario e ispezionare il risultato.

    Committa davvero: l'applicazione committa, e i test devono vedere lo stato
    committato.
    """
    sessione = SessionLocal()
    try:
        yield sessione
    finally:
        sessione.close()
