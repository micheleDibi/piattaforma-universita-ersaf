"""Accesso Universo con il verificatore password e i limiti comuni del backend."""

import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response
from fastapi.concurrency import run_in_threadpool
from src.auth.limiti_login import azzera_account, prenota_tentativo
from src.auth.servizio_login import trova_utente_per_username, verifica_credenziali
from src.chat_pratiche.configurazione import configurazione
from src.database import SessionLocal
from src.realtime import sessioni, token
from src.realtime.contratti import corpo, stringa
from src.realtime.dati import esegui, ora
from src.realtime.errori import richiedi
from src.realtime.identita import carica
from src.security.rete import ip_client

router = APIRouter(prefix="/auth")


def login(dati, ip):
    richiedi(set(dati) <= {"username", "password", "deviceId"})
    username, password = (
        stringa(dati, "username").strip(),
        stringa(dati, "password", 512),
    )
    device = dati.get("deviceId")
    richiedi(device is None or isinstance(device, str))
    device = (device or "").strip() or "unknown"
    richiedi(len(device) <= 128)
    prenotazione = prenota_tentativo(username, ip)
    with SessionLocal.begin() as db:
        utente, _ = trova_utente_per_username(db, username)
        richiedi(verifica_credenziali(db, utente, password), "invalid_credentials", 401)
        identita = carica(db, utente.utente_id)
        s, refresh = nuova_sessione(db, identita, device.strip())
    azzera_account(prenotazione)
    return dict(
        **token.emetti(s, refresh),
        utente=dict(
            utenteId=str(identita.utente_id),
            clienteId=identita.cliente_id,
            clienteCodiceFiscale=identita.codice_fiscale,
            utenteRuoloCodice=identita.ruolo,
            aziendaId=identita.azienda_id,
        ),
    )


def nuova_sessione(db, identita, device):
    adesso, refresh = ora(), token.nuovo_refresh()
    s = dict(
        session_id=str(uuid.uuid4()),
        utente_id=identita.utente_id,
        cliente_id=identita.cliente_id,
        azienda_id=identita.azienda_id,
        ruolo_codice=identita.ruolo,
        device_id=device,
        refresh_token_hash=token.impronta(refresh),
        created_at=adesso,
        refresh_expires_at=adesso + timedelta(days=configurazione().realtime_refresh_giorni),
        last_used_at=adesso,
    )
    esegui(
        db,
        "INSERT INTO realtime_auth_session ("
        + ",".join(s)
        + ") VALUES ("
        + ",".join(":" + k for k in s)
        + ")",
        s,
    )
    return s, refresh


@router.post("/login")
async def entra(request: Request):
    return await run_in_threadpool(login, await corpo(request), ip_client(request))


@router.post("/refresh")
async def rinnova(request: Request):
    dati = await corpo(request)
    richiedi(set(dati) == {"refreshToken"})
    return await run_in_threadpool(sessioni.ruota, stringa(dati, "refreshToken"))


@router.post("/recover")
async def recupera(request: Request):
    dati = await corpo(request, 4096)
    richiedi(set(dati) == {"refreshToken", "deviceId"})
    return await run_in_threadpool(
        sessioni.ruota,
        stringa(dati, "refreshToken"),
        stringa(dati, "deviceId", 128).strip(),
    )


@router.post("/logout", status_code=204)
def esci(accesso=Depends(sessioni.bearer)):
    d = token.decodifica(accesso)
    with sessioni.transazione(accesso) as (db, _):
        sessioni.revoca(db, d["sid"], "LOGOUT")
    return Response(status_code=204)
