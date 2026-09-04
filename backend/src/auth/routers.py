"""Rotte di autenticazione."""

from __future__ import annotations

import contextlib
import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.dipendenze import (  # noqa: F401  (get_current_utente e' riesportata)
    SessioneCorrente,
    get_current_utente,
    get_sessione_corrente,
    schema_bearer,
)
from src.auth.models import Esito, MotivoRevoca
from src.auth.schemas import (
    CORPO_RISPOSTA_GENERICA,
    MESSAGGIO_CREDENZIALI,
    ConfermaResetRequest,
    LoginRequest,
    RichiestaResetRequest,
)
from src.auth.servizio_login import (
    cliente_principale,
    codice_ruolo,
    trova_utente_per_username,
    verifica_credenziali,
)
from src.auth.servizio_reset import (
    applica_nuova_password,
    consuma_token,
    dati_token,
    elabora_richiesta_reset,
    nome_cliente,
    registra_esito_isolato,
    stato_token,
    username_e_email,
)
from src.config import get_impostazioni
from src.database import get_db
from src.notifiche.backend_invio import Mailer, get_mailer
from src.notifiche.email import (
    DatiInvioCambio,
    invia_mail_cambio_eseguito,
    invia_mail_reset,
)
from src.security.password import hash_password, messaggi_policy, verifica_policy_password
from src.security.rete import ip_client, user_agent
from src.security.sessioni import crea_sessione, revoca_sessione
from src.security.tempo import pavimento_temporale
from src.security.tokens import forma_token_valida

logger = logging.getLogger("ersaf.auth")

router = APIRouter(prefix="/auth", tags=["Login"])


def _credenziali_errate() -> HTTPException:
    """Un solo messaggio per tutti i motivi di rifiuto.

    Password sbagliata, utente inesistente, account disattivato, utente senza
    riga `clienti`, username ambiguo: dall'esterno devono essere
    indistinguibili, altrimenti il login diventa un oracolo di enumerazione.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=MESSAGGIO_CREDENZIALI
    )


@router.post("/login")
def login(creds: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = ip_client(request)
    ua = user_agent(request)

    utente, ambiguo = trova_utente_per_username(db, creds.utente_username)
    if ambiguo:
        # Il database non ha la UNIQUE su utente_username e contiene sei gruppi
        # di duplicati. Prima si prendeva una riga arbitraria: se la password
        # digitata era quella dell'altro omonimo l'accesso falliva senza motivo
        # apparente, e se coincideva si entrava nell'account sbagliato.
        # La bonifica e' descritta nella migrazione 005.
        logger.warning(
            "accesso negato: lo username corrisponde a piu' di un utente"
        )
        verifica_credenziali(db, None, creds.utente_password)
        raise _credenziali_errate()

    if not verifica_credenziali(db, utente, creds.utente_password):
        raise _credenziali_errate()

    # Gli 869 utenti senza riga `clienti` producevano un 500 qui
    # (user.clienti.ruolo.ruolo_codice su clienti = None), e un 500 distingueva
    # "password sbagliata" da "utente esistente ma orfano".
    cliente = cliente_principale(db, utente.utente_id)
    if cliente is None:
        logger.warning(
            "accesso negato: utente senza riga clienti, utente_id=%s",
            utente.utente_id,
        )
        raise _credenziali_errate()

    ruolo = codice_ruolo(db, cliente.cliente_ruolo)

    if ruolo and ruolo.lower() == "nazionale":
        # Il flusso 2FA vero e' fuori perimetro. Non si emette sessione e non
        # si restituisce utente_id: il frontend deve fermarsi qui.
        db.commit()  # l'eventuale rehash pigro resta valido
        logger.info(
            "verifica a due fattori richiesta per utente_id=%s", utente.utente_id
        )
        return {
            "requires_2fa": True,
            "message": "Verifica a due fattori richiesta (2FA)",
            "utente_username": utente.utente_username,
        }

    token, scadenza = crea_sessione(db, utente.utente_id, ip, ua)
    db.commit()
    logger.info("login riuscito per utente_id=%s", utente.utente_id)

    return {
        "message": "Login effettuato con successo",
        # utente_id resta nella risposta: il frontend lo salva e lo inserisce
        # nel corpo di POST /clienti/. Toglierlo romperebbe la creazione dei
        # sottoscrittori.
        "utente_id": utente.utente_id,
        "utente_username": utente.utente_username,
        "ruolo_codice": ruolo,
        "token": token,
        "token_type": "bearer",
        "scadenza": scadenza.isoformat() if scadenza else None,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credenziali: HTTPAuthorizationCredentials | None = Depends(schema_bearer),
    db: Session = Depends(get_db),
) -> Response:
    """Sempre 204, anche con un token gia' revocato o inesistente.

    Un codice diverso direbbe al chiamante se quel token e' mai esistito.
    """
    if credenziali is not None and credenziali.scheme.lower() == "bearer":
        revoca_sessione(db, credenziali.credentials, MotivoRevoca.LOGOUT)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Recupero password
# =============================================================================
@router.post("/password-reset/request")
async def richiedi_reset(
    corpo: RichiestaResetRequest,
    request: Request,
    attivita: BackgroundTasks,
    db: Session = Depends(get_db),
    mailer: Mailer = Depends(get_mailer),
) -> Response:
    """Risponde SEMPRE 200 con lo stesso identico corpo.

    Mai un codice diverso, mai un campo diverso, mai un 429: un 429 direbbe
    all'attaccante che quell'indirizzo vale la pena insistere.

    E' `async def` mentre tutto il resto del progetto e' sync, ed e'
    deliberato: il pavimento temporale deve attendere senza occupare un thread.
    Esiste un solo threadpool da 40 slot condiviso da TUTTE le route sync, e un
    time.sleep(0.9) ne occuperebbe uno — quaranta richieste concorrenti
    congelerebbero anche /clienti/, /utenti/ e /auth/login. Il lavoro sul
    database resta sincrono, dentro run_in_threadpool.
    """
    impostazioni = get_impostazioni()
    ip = ip_client(request)
    ua = user_agent(request)
    invio = None

    async with pavimento_temporale(impostazioni.password_reset_budget_ms):
        try:
            invio = await run_in_threadpool(
                elabora_richiesta_reset, db, corpo.email, ip, ua
            )
        except Exception:
            # Un'eccezione qui produrrebbe un 500, cioe' esattamente l'oracolo
            # che questo endpoint esiste per evitare.
            db.rollback()
            logger.exception("errore interno nella richiesta di reset")
            with contextlib.suppress(Exception):
                registra_esito_isolato(ip, ua, Esito.ERRORE_INTERNO)
            invio = None

    if invio is not None:
        # Accodato DOPO il commit e fuori dal ciclo di richiesta: il tempo di
        # consegna SMTP non entra nel tempo di risposta.
        attivita.add_task(invia_mail_reset, mailer, invio)

    return Response(
        content=CORPO_RISPOSTA_GENERICA,
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )


@router.get("/password-reset/validate")
def valida_token_reset(token: str = "", db: Session = Depends(get_db)) -> dict:
    """SOLA LETTURA: non marca nulla.

    Il prefetch di un client di posta o un crawler che apre il link
    brucerebbero il token.
    """
    return stato_token(db, token)


@router.post("/password-reset/confirm")
def conferma_reset(
    corpo: ConfermaResetRequest,
    request: Request,
    attivita: BackgroundTasks,
    db: Session = Depends(get_db),
    mailer: Mailer = Depends(get_mailer),
) -> dict:
    ip = ip_client(request)
    ua = user_agent(request)

    if corpo.password != corpo.password_conferma:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "codice": "password_non_coincidono",
                "messaggi": ["Le due password non coincidono"],
            },
        )

    if not forma_token_valida(corpo.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "codice": "token_non_valido",
                "messaggi": ["Il link non e' piu' valido. Richiedine uno nuovo."],
            },
        )

    # Si legge l'utente PRIMA di consumare, per poter applicare la regola
    # "password diversa da username e email". La lettura non modifica nulla.
    riferimenti = dati_token(db, corpo.token)
    username, email = (
        username_e_email(db, riferimenti.utente_id) if riferimenti else (None, None)
    )

    violate = verifica_policy_password(corpo.password, username=username, email=email)
    if violate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "codice": "policy_password",
                "regole_violate": violate,
                "messaggi": messaggi_policy(violate),
            },
        )

    # bcrypt (~250 ms in produzione) FUORI dalla transazione: dentro terrebbe un
    # lock di riga su password_reset_token per un quarto di secondo senza
    # motivo. L'unicita' della transazione riguarda gli effetti sul database.
    nuovo_hash = hash_password(corpo.password)

    try:
        # Query [C] della 002: consumo atomico. Due richieste concorrenti: solo
        # una ottiene rowcount == 1.
        if consuma_token(db, corpo.token, ip, ua) != 1 or riferimenti is None:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "codice": "token_non_valido",
                    "messaggi": ["Il link non e' piu' valido. Richiedine uno nuovo."],
                },
            )

        applica_nuova_password(
            db, riferimenti.utente_id, riferimenti.prt_id, nuovo_hash
        )
        nome = nome_cliente(db, riferimenti.utente_id)
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("errore nel completamento del cambio password")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"codice": "errore_interno"},
        )

    logger.info("cambio password completato, prt_id=%s", riferimenti.prt_id)

    if riferimenti.prt_email_inviata:
        # Dopo il commit. Il destinatario e' l'indirizzo a cui il link e' stato
        # realmente spedito, congelato dalla 002: se il cliente ha cambiato
        # email nel frattempo, la notifica segue il link.
        attivita.add_task(
            invia_mail_cambio_eseguito,
            mailer,
            DatiInvioCambio(
                destinatario=riferimenti.prt_email_inviata, nome=nome, ip=ip
            ),
        )

    # L'utente NON viene autenticato: la risposta rimanda al login.
    return {
        "message": "Password aggiornata. Ora puoi accedere con le nuove credenziali."
    }
