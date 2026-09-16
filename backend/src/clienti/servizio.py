"""Creazione di un cliente con il suo utente.

L'utente nasce disattivato e senza password reale: la password vera si
genera solo dopo la verifica di email e cellulare (attiva_utente_con_password),
non piu' alla creazione. Fino a quel momento l'account e' indistinguibile,
dall'esterno, da un account inesistente (stesso controllo di
verifica_credenziali sul login).
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import date
from enum import Enum
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.auth.models import ATTIVO
from src.clienti.models import Cliente
from src.ruolo.models import Ruolo
from src.security.password import (
    hash_password,
    verifica_policy_password,
)
from src.universita.models import Universita
from src.universita.schemas import UniversitaBase
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.clienti")

# Convenzione della piattaforma: -1 = attivo (ATTIVO, importato sopra),
# 0 = disattivato. In attesa di verifica email l'utente nasce a 0.
UTENTE_IN_ATTESA_VERIFICA = 0


class TipoUtente(str, Enum):
    SOTTOSCRITTORE = "sottoscrittore"
    ATTUATORE = "attuatore"


# cliente_codice non compare piu' qui: e' generato dal backend a partire da
# cliente_id (vedi crea_cliente_con_utente) e quindi unico per definizione.
CAMPI_UNIVOCI_CLIENTE = (
    ("cliente_codice_fiscale", "Esiste già un cliente con questo codice fiscale."),
    ("cliente_email", "Esiste già un cliente registrato con questa email."),
    ("cliente_telefono", "Esiste già un cliente con questo numero di telefono."),
    ("cliente_cellulare", "Esiste già un cliente con questo numero di cellulare."),
    ("cliente_pec", "Esiste già un cliente con questa PEC."),
    ("cliente_documento", "Esiste già un cliente con questo numero di documento."),
)

CAMPI_ABILITAZIONE = (
    "cliente_abilPraticheUniv",
    "cliente_abilitazione_ecampus",
    "cliente_abilitazione_link_campus",
    "cliente_abilitazione_corsi_speciali",
    "cliente_abilitazione_a4u",
)

ABILITAZIONI_SEMPRE_SPENTE = ("cliente_abilitazione_corsi_speciali",)


# =============================================================================
# Unicita'
# =============================================================================
def verifica_unicita_anagrafica(
    db: Session, dati: dict[str, Any], escludi_cliente_id: int | None = None
) -> None:
    """Controlla l'unicita' dei campi sensibili.

    escludi_cliente_id va passato dal PUT per non far scattare il conflitto
    confrontando il cliente con se stesso quando non cambia nulla.
    """
    condizioni = [
        getattr(Cliente, attributo) == dati[attributo]
        for attributo, _ in CAMPI_UNIVOCI_CLIENTE
        if dati.get(attributo)
    ]
    if not condizioni:
        return

    query = db.query(Cliente).filter(or_(*condizioni))
    if escludi_cliente_id is not None:
        query = query.filter(Cliente.cliente_id != escludi_cliente_id)

    for esistente in query.all():
        for attributo, messaggio in CAMPI_UNIVOCI_CLIENTE:
            atteso = dati.get(attributo)
            if atteso and getattr(esistente, attributo) == atteso:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=messaggio
                )


# =============================================================================
# Username e password
# =============================================================================
def genera_username(db: Session, nome: str, cognome: str) -> str:
    base = f"{nome.strip().capitalize()}{cognome.strip().capitalize()}"

    presi = {
        riga[0]
        for riga in db.query(Utente.utente_username)
        .filter(Utente.utente_username.like(f"{base}%"))
        .all()
    }
    if base not in presi:
        return base

    suffisso = 2
    while f"{base}{suffisso}" in presi:
        suffisso += 1
    return f"{base}{suffisso}"


def genera_password(nome: str, cognome: str, utente_id: int, username: str) -> str:
    """Password iniziale casuale; mai derivata dai dati anagrafici."""
    from src.config import get_impostazioni
    lunghezza = max(24, get_impostazioni().password_min_length)
    if lunghezza > 72:
        raise ValueError("La lunghezza minima configurata supera il limite bcrypt.")
    while True:
        password = secrets.token_urlsafe(54)[:lunghezza]
        if not verifica_policy_password(password, username=username):
            return password


def crea_utente_per_cliente(db: Session, nome: str, cognome: str, autore_id: int) -> Utente:
    """Crea la riga `utenti`, disattivata e senza password vera.

    Restituisce SOLO l'utente (non una tupla): a differenza di prima, qui
    non esiste ancora nessuna password in chiaro da restituire.
    """
    nuovo_utente = Utente(
        utente_username=f"temp-{uuid.uuid4()}",
        utente_password="",
        utente_password_hash="",
        utente_attivoSN=UTENTE_IN_ATTESA_VERIFICA,
    )
    db.add(nuovo_utente)
    db.flush()  # genera utente_id

    username = genera_username(db, nome, cognome)
    nuovo_utente.utente_username = username
    nuovo_utente.utente_created_by = autore_id
    nuovo_utente.utente_updated_by = autore_id
    nuovo_utente.utente_padre = autore_id
    # Hash di un valore casuale che nessuno conoscera' mai: non vuoto
    # (romperebbe verify_password) e non la password vera, che a questo
    # punto non esiste ancora.
    nuovo_utente.utente_password_hash = hash_password(secrets.token_urlsafe(32))
    nuovo_utente.utente_password_algo = "bcrypt"
    nuovo_utente.utente_salt = str(uuid.uuid4())

    return nuovo_utente


def attiva_utente_con_password(db: Session, utente: Utente, nome: str, cognome: str) -> str:
    """Genera la password vera e attiva l'account (ATTIVO = -1).

    Va chiamata solo dopo la verifica di email e cellulare. Ritorna la password
    in chiaro, da mandare una sola volta per email: da qui in poi nel
    database resta solo l'hash.
    """
    password_in_chiaro = genera_password(nome, cognome, utente.utente_id, utente.utente_username)
    utente.utente_password_hash = hash_password(password_in_chiaro)
    utente.utente_password_algo = "bcrypt"
    utente.utente_attivoSN = ATTIVO
    return password_in_chiaro


# =============================================================================
# Costruzione dei payload: funzioni pure, testabili senza database
# =============================================================================
CAMPI_UNIVERSITA = frozenset(UniversitaBase.model_fields.keys())


def payload_cliente(
    dati: dict[str, Any], tipo_utente: TipoUtente, utente_id: int
) -> dict[str, Any]:
    payload = {
        chiave: valore
        for chiave, valore in dati.items()
        if chiave not in CAMPI_UNIVERSITA
        # cliente_codice escluso a prescindere da cio' che manda il client:
        # lo decide solo il backend, dopo il flush, da cliente_id.
        and chiave not in {"utente_username", "utente_password", "cliente_codice"}
        and valore is not None
    }
    payload["utente_id"] = utente_id

    acceso = -1 if tipo_utente is TipoUtente.ATTUATORE else 0
    for campo in CAMPI_ABILITAZIONE:
        if payload.get(campo) is None:
            payload[campo] = 0 if campo in ABILITAZIONI_SEMPRE_SPENTE else acceso

    return payload


def payload_universita(
    dati: dict[str, Any], cliente_id: int, autore_id: int, oggi: date | None = None
) -> dict[str, Any]:
    oggi = oggi or date.today()

    payload = {
        chiave: valore
        for chiave, valore in dati.items()
        if chiave in CAMPI_UNIVERSITA and valore is not None and valore != ""
    }
    payload["cliente_id"] = cliente_id
    payload["universita_createBy"] = autore_id
    payload["universita_updateBy"] = autore_id
    payload["universita_createDate"] = oggi
    payload["universita_updateDate"] = oggi
    return payload


# =============================================================================
# Orchestrazione
# =============================================================================
def crea_cliente_con_utente(
    db: Session, dati: dict[str, Any], tipo_utente: TipoUtente, autore_id: int
) -> dict[str, Any]:
    """Il flusso completo. Non fa commit: lo fa il chiamante."""
    verifica_unicita_anagrafica(db, dati)

    nuovo_utente = crea_utente_per_cliente(
        db, dati["cliente_nome"], dati["cliente_cognome"], autore_id
    )

    if tipo_utente is TipoUtente.ATTUATORE and not dati.get("cliente_ruolo"):
        ruolo_aderente = db.query(Ruolo).filter(Ruolo.ruolo_codice == "Aderente").first()
        if ruolo_aderente:
            dati["cliente_ruolo"] = ruolo_aderente.ruolo_id

    nuovo_cliente = Cliente(
        **payload_cliente(dati, tipo_utente, nuovo_utente.utente_id)
    )
    db.add(nuovo_cliente)
    db.flush()  # genera cliente_id, indispensabile per il curriculum e per il codice

    # cliente_codice = CODICEFISCALE_ID quando c'e' il CF, altrimenti solo
    # l'ID. Leggibile, e unico per definizione grazie a cliente_id.
    cf = (nuovo_cliente.cliente_codice_fiscale or "").strip().upper()
    nuovo_cliente.cliente_codice = (
        f"{cf}_{nuovo_cliente.cliente_id}" if cf else str(nuovo_cliente.cliente_id)
    )

    db.add(
        Universita(
            **payload_universita(dati, nuovo_cliente.cliente_id, autore_id)
        )
    )

    from src.otp.models import Attivazione
    db.add(Attivazione(utente_id=nuovo_utente.utente_id, cliente_id=nuovo_cliente.cliente_id))
    return {"cliente": nuovo_cliente, "utente": nuovo_utente}