import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import get_impostazioni

_impostazioni = get_impostazioni()

# Fallback INERTE, non piu' `mysql+pymysql://root:1234@localhost` (rilievo S6
# dell'analisi): in assenza di .env l'applicazione tentava di connettersi con
# credenziali di default senza dirlo a nessuno. Ora, se DATABASE_URL manca,
# l'app non parte comunque — ci pensa verifica_configurazione() nel lifespan —
# ma l'import non esplode, cosi' la raccolta dei test resta possibile.
#
# TEST_DATABASE_URL ha la precedenza: e' il DB dedicato usato dalla suite.
SQLALCHEMY_DATABASE_URL = (
    os.getenv("TEST_DATABASE_URL")
    or _impostazioni.database_url
    or "sqlite+pysqlite:///:memory:"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # La piattaforma legacy tiene MariaDB con un wait_timeout basso: senza
    # questi due, la prima richiesta dopo una pausa fallisce con "server has
    # gone away".
    pool_pre_ping=True,
    pool_recycle=1800,
    # CRITICO per il requisito "nessun valore sensibile nei log": senza,
    # ogni errore SQLAlchemy porta "[parameters: ('a3f9...',)]" nel messaggio
    # dell'eccezione, cioe' l'impronta del token, e quel messaggio finisce nel
    # traceback e nella risposta di errore.
    hide_parameters=True,
    # MAI True: il logger sqlalchemy.engine stamperebbe ogni statement con i
    # parametri.
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# Database amministrativi secondari (facoltativi)
# =============================================================================
# Stesso server, stesso utente e password del DB principale, nome diverso.
# A differenza di SQLALCHEMY_DATABASE_URL non hanno un fallback e non sono
# richiesti da verifica_configurazione(): se la variabile manca, l'engine e
# la sessione restano None e get_db_* solleva un errore chiaro solo se
# qualcuno prova davvero a usarli. Nessuna funzionalita' li usa ancora.
SQLALCHEMY_DATABASE_URL_GESTIONE_PAGAMENTI = (
    os.getenv("TEST_DATABASE_URL_GESTIONE_PAGAMENTI")
    or _impostazioni.database_url_gestione_pagamenti
    or None
)
SQLALCHEMY_DATABASE_URL_SYS_ADMIN = (
    os.getenv("TEST_DATABASE_URL_SYS_ADMIN")
    or _impostazioni.database_url_sys_admin
    or None
)


def _crea_engine_facoltativo(url: str | None):
    if not url:
        return None
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        hide_parameters=True,
        echo=False,
        future=True,
    )


engine_gestione_pagamenti = _crea_engine_facoltativo(SQLALCHEMY_DATABASE_URL_GESTIONE_PAGAMENTI)
engine_sys_admin = _crea_engine_facoltativo(SQLALCHEMY_DATABASE_URL_SYS_ADMIN)

SessionGestionePagamenti = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine_gestione_pagamenti)
    if engine_gestione_pagamenti is not None
    else None
)
SessionSysAdmin = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine_sys_admin)
    if engine_sys_admin is not None
    else None
)


def get_db_gestione_pagamenti():
    if SessionGestionePagamenti is None:
        raise RuntimeError("DATABASE_URL_GESTIONE_PAGAMENTI non e' configurata")
    db = SessionGestionePagamenti()
    try:
        yield db
    finally:
        db.close()


def get_db_sys_admin():
    if SessionSysAdmin is None:
        raise RuntimeError("DATABASE_URL_SYS_ADMIN non e' configurata")
    db = SessionSysAdmin()
    try:
        yield db
    finally:
        db.close()
