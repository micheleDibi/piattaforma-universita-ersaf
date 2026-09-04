import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_impostazioni, verifica_configurazione
from src.logging_config import NOME_LOGGER, configura_logging

# Gli import dei modelli servono a registrare i mapper prima che i router
# risolvano le relazioni dichiarate per nome. Rimuoverli rompe la
# configurazione di SQLAlchemy.
from src.aziende.models import Azienda  # noqa: F401
from src.clienti.models import Cliente  # noqa: F401
from src.ruolo.models import Ruolo  # noqa: F401
from src.utenti.models import Utente  # noqa: F401
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


@app.get("/")
def read_root():
    return {"message": "Benvenuto"}
