import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.config import get_impostazioni, verifica_configurazione
from src.logging_config import NOME_LOGGER, configura_logging

# Gli import dei modelli servono a registrare i mapper prima che i router
# risolvano le relazioni dichiarate per nome. Rimuoverli rompe la
# configurazione di SQLAlchemy.
from src.pratiche.models import Pratica  # noqa: F401
from src.aziende.models import Azienda  # noqa: F401
from src.clienti.models import Cliente  # noqa: F401
from src.ruolo.models import Ruolo  # noqa: F401
from src.utenti.models import Utente  # noqa: F401
from src.universita.models import Universita  # noqa: F401
from src.listino_tipoCorso.models import ListinoTipoCorsoDB
from src.pratiche_stati.models import PraticaStato
from src.listini_testa.models import ListinoTestaDB
from src.auth.models import (  # noqa: F401
    AuthSessione,
    PasswordResetRichiesta,
    PasswordResetToken,
)
from src.notifiche.models import MessaggioEmail  # noqa: F401

from src.auth.routers import router as auth_router
from src.aziende.routers import router as azienda_router
from src.clienti.routers import router as cliente_router
from src.ruolo.routers import router as ruolo_router
from src.utenti.routers import router as utente_router
from src.universita.routers import router as universita_router
from src.listini_testa.routers import router as listini_testa_router
from src.pratiche.routers import router as pratiche_router

logger = logging.getLogger(NOME_LOGGER)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Avvio dell'applicazione.

    verifica_configurazione() solleva se i pepper mancano, sono corti o sono
    ancora i valori d'esempio: uvicorn lo traduce in "Application startup
    failed" e in un'uscita con codice diverso da zero. E' il meccanismo con cui
    l'applicazione si rifiuta di partire con una configurazione incompleta.

    configura_logging viene prima, cosi' anche il messaggio d'errore passa dal
    formatter con la redazione.
    """
    impostazioni = get_impostazioni()
    configura_logging(impostazioni)
    verifica_configurazione(impostazioni)
    logger.info(
        "avvio: ambiente=%s invio_email=%s costo_bcrypt=%s",
        impostazioni.ersaf_env,
        impostazioni.email_backend,
        impostazioni.bcrypt_cost,
    )
    yield


app = FastAPI(title="Piattaforma Universita ERSAF", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_impostazioni().lista_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(utente_router)
app.include_router(ruolo_router)
app.include_router(cliente_router)
app.include_router(auth_router)
app.include_router(azienda_router)
app.include_router(universita_router)
app.include_router(listini_testa_router)
app.include_router(pratiche_router)


@app.exception_handler(IntegrityError)
async def gestisci_integrity_error(request: Request, exc: IntegrityError):
    """Un vincolo del database violato e' colpa della richiesta, non del server.

    I modelli non rispecchiavano la DDL reale in dieci punti - colonne
    dichiarate nullable e NOT NULL nel database, e viceversa - quindi ogni
    richiesta sbagliata usciva come 500 con traceback. Un 409 dice al chiamante
    che il dato non e' accettabile; il dettaglio resta nel log, dove non
    descrive lo schema a chi non lo conosce.
    """
    logger.warning("vincolo violato su %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "I dati inviati violano un vincolo di integrità."},
    )


@app.exception_handler(SQLAlchemyError)
async def gestisci_errore_database(request: Request, exc: SQLAlchemyError):
    logger.exception("errore di database su %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Errore interno. Riprova, e se persiste segnala l'errore."},
    )


@app.get("/salute", tags=["Servizio"])
def salute():
    """Sonda di liveness per il reverse proxy e per il deploy."""
    return {"stato": "ok"}


@app.get("/")
def read_root():
    return {"message": "Benvenuto"}
