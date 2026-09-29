"""Sessioni amministrative facoltative, inizializzate solo al primo utilizzo."""

import os
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker

from src.config import get_impostazioni
from src.database_trasporto import configura as configura_trasporto
from src.database_trasporto import limiti_pool

VARIABILI = {
    "DATABASE_URL_GESTIONE_PAGAMENTI": "database_url_gestione_pagamenti",
    "DATABASE_URL_SYS_ADMIN": "database_url_sys_admin",
}
_fabbriche = {}
_blocco = Lock()


def _indirizzo(variabile):
    impostazioni = get_impostazioni()
    in_test = impostazioni.ersaf_env == "test" or bool(os.getenv("TEST_DATABASE_URL"))
    override_test = {
        "DATABASE_URL_GESTIONE_PAGAMENTI": os.getenv("TEST_DATABASE_URL_GESTIONE_PAGAMENTI", ""),
        "DATABASE_URL_SYS_ADMIN": os.getenv("TEST_DATABASE_URL_SYS_ADMIN", ""),
    }
    indirizzo = (override_test[variabile] if in_test
                 else getattr(impostazioni, VARIABILI[variabile]))
    if not indirizzo:
        raise RuntimeError(f"{variabile} non e' configurata")
    try:
        url = make_url(indirizzo)
    except (ArgumentError, ValueError):
        raise RuntimeError(f"{variabile} non e' valida") from None
    if in_test and (
        url.drivername != "mysql+pymysql" or url.host not in {"127.0.0.1", "localhost", "::1"}
        or url.port != 3307 or url.database != "ersaf_test" or url.query
    ):
        raise RuntimeError("I database secondari di test richiedono loopback:3307/ersaf_test")
    return indirizzo


def _fabbrica(variabile):
    indirizzo = _indirizzo(variabile)
    chiave = (variabile, indirizzo)
    with _blocco:
        if chiave not in _fabbriche:
            try:
                engine = create_engine(
                    indirizzo, **limiti_pool(indirizzo), pool_pre_ping=True, pool_recycle=1800,
                    hide_parameters=True, echo=False, future=True,
                )
                configura_trasporto(engine, get_impostazioni)
            except (ArgumentError, ImportError, ValueError):
                raise RuntimeError(f"{variabile} non e' valida") from None
            _fabbriche[chiave] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return _fabbriche[chiave]


def sessione_secondaria(variabile):
    db = _fabbrica(variabile)()
    try:
        yield db
    finally:
        db.close()
