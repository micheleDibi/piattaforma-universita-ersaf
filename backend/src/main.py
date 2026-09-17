import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.config import get_impostazioni, verifica_configurazione
from src.logging_config import NOME_LOGGER, configura_logging
from src.security.browser import verifica_richiesta_browser
from src.notifiche.config_sms import ConfigSMS

# Gli import dei modelli servono a registrare i mapper prima che i router
# risolvano le relazioni dichiarate per nome. Rimuoverli rompe la
# configurazione di SQLAlchemy.
from src.pratiche.models import Pratica  # noqa: F401
from src.aziende.models import Azienda  # noqa: F401
from src.aziende_xcod.models import AziendaXCod  # noqa: F401
from src.clienti.models import Cliente  # noqa: F401
from src.ruolo.models import Ruolo  # noqa: F401
from src.utenti.models import Utente  # noqa: F401
from src.universita.models import Universita  # noqa: F401
from src.pratiche_registri_mise.models import PraticaRegistroMise
from src.listino_tipoCorso.models import ListinoTipoCorsoDB
from src.pratiche_stati.models import PraticaStato
from src.listini_testa.models import ListinoTestaDB
from src.auth.models import (  # noqa: F401
    AuthSessione,
    PasswordResetRichiesta,
    PasswordResetToken,
)
from src.notifiche.models import MessaggioEmail  # noqa: F401
from src.mfa.models import AuthMfaUtente, AuthPasskey, AuthTotp  # noqa: F401

from src.otp.contatti import router as otp_contatti_router
from src.otp.accesso import router as otp_accesso_router
from src.mfa.accesso import router as mfa_accesso_router
from src.mfa.gestione import router as mfa_gestione_router
from src.auth.routers import router as auth_router
from src.aziende.routers import router as azienda_router
from src.aziende_xcod.router import router as aziende_xcod_router
from src.clienti.routers import router as cliente_router
from src.ruolo.routers import router as ruolo_router
from src.utenti.routers import router as utente_router
from src.universita.routers import router as universita_router
from src.listini_testa.routers import router as listini_testa_router
from src.pratiche.routers import router as pratiche_router
from src.profilo.routers import router as profilo_router
from src.listino_tipoCorso.routers import router as listini_tipi_corsi_router
from fastapi.exceptions import RequestValidationError

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
    sms = ConfigSMS()
    sms.verifica()
    if impostazioni.ersaf_env == "produzione" and sms.sms_backend != "skebby":
        raise ValueError("In produzione configurare SMS_BACKEND=skebby.")
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
    expose_headers=["Retry-After"],
)


@app.middleware("http")
async def proteggi_richieste_browser(request: Request, call_next):
    try:
        verifica_richiesta_browser(request)
    except HTTPException as errore:
        return JSONResponse(status_code=errore.status_code, content={"detail": errore.detail})
    risposta = await call_next(request)
    if request.url.path.startswith(("/auth/", "/profilo/")) or "/contatti" in request.url.path or risposta.status_code in (401, 403, 429):
        risposta.headers["Cache-Control"] = "no-store"
    return risposta

app.include_router(utente_router)
app.include_router(ruolo_router)
app.include_router(cliente_router)
app.include_router(auth_router)
app.include_router(otp_accesso_router)
app.include_router(mfa_accesso_router)
app.include_router(mfa_gestione_router)
app.include_router(otp_contatti_router)
app.include_router(azienda_router)
app.include_router(aziende_xcod_router)
app.include_router(universita_router)
app.include_router(listini_testa_router)
app.include_router(pratiche_router)
app.include_router(profilo_router)
app.include_router(listini_tipi_corsi_router)


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


@app.exception_handler(RequestValidationError)
async def gestisci_errori_validazione(request: Request, exc: RequestValidationError):
    """Pydantic/FastAPI restituiscono di default un 422 con 'loc', 'msg'
    prefissato da 'Value error, ' e altri dettagli tecnici (nome del campo,
    struttura annidata). Qui si estraggono tutti i messaggi pensati per
    l'utente - quelli scritti nei nostri field_validator/model_validator
    sollevando ValueError - ripuliti dal prefisso tecnico e uniti in un
    unico testo, cosi' un submit con piu' campi non validi mostra subito
    tutti i problemi invece di farli scoprire uno alla volta a colpi di
    invio. Il formato resta {"detail": ...} come le HTTPException sollevate
    a mano nel resto del backend."""
    messaggi = []
    for errore in exc.errors():
        testo = errore.get("msg", "Dati non validi.")
        if testo.startswith("Value error, "):
            testo = testo[len("Value error, "):]
        messaggi.append(testo)

    # Piu' errori sullo stesso campo (raro, ma possibile con piu'
    # validator) non vanno ripetuti identici nel messaggio finale.
    messaggi_unici = list(dict.fromkeys(messaggi))
    dettaglio = "; ".join(messaggi_unici)

    logger.info("validazione fallita su %s %s: %s", request.method, request.url.path, dettaglio)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": dettaglio},
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