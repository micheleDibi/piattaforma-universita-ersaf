"""Creazione di un cliente con il suo utente.

Era una funzione sola di 188 righe dentro il router, con otto responsabilita':
sei controlli di unicita', la creazione dell'utente, la generazione delle
credenziali, la verifica della policy, la costruzione della riga cliente, la
costruzione della riga universita, due passate di coercizione dei tipi e la
gestione degli errori. Il 27% del corpo era conversione di tipi, ed e' li' che
vivevano i difetti - perche' quel codice non era raggiungibile da un test se
non passando da una richiesta HTTP e da un database.

Qui le due funzioni che costruiscono i dizionari sono pure: prendono un dict e
ne restituiscono un altro. Si testano senza database e senza applicazione.
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
from src.security.password import (
    hash_password,
    messaggi_policy,
    verifica_policy_password,
)
from src.universita.models import Universita
from src.universita.schemas import UniversitaBase
from src.utenti.models import Utente

logger = logging.getLogger("ersaf.clienti")


class TipoUtente(str, Enum):
    """Era un `str` libero: `?tipo_utente=Attuatorre` cadeva in silenzio nel
    ramo sottoscrittore, e chi lo aveva scritto non se ne accorgeva. Come Enum,
    FastAPI risponde 422 con l'elenco dei valori ammessi."""

    SOTTOSCRITTORE = "sottoscrittore"
    ATTUATORE = "attuatore"


# (attributo, messaggio). L'ordine e' quello dei controlli originali, cosi' i
# messaggi restano gli stessi che il frontend gia' mostra.
CAMPI_UNIVOCI_CLIENTE = (
    ("cliente_codice", "Esiste già un cliente con questo codice."),
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

# Restano a 0 anche per gli attuatori: sono due funzionalita' che si abilitano
# a mano dalla scheda utente. Il database ha DEFAULT -1 su entrambe, ma qui il
# valore viene sempre passato esplicitamente, quindi quel default non entra mai
# in gioco. Cambiarlo significherebbe accendere due funzionalita' a tutti: e'
# una decisione di prodotto, non una correzione.
ABILITAZIONI_SEMPRE_SPENTE = ("cliente_abilitazione_corsi_speciali",)


# =============================================================================
# Unicita'
# =============================================================================
def verifica_unicita_anagrafica(db: Session, dati: dict[str, Any]) -> None:
    """Una sola query al posto di sei SELECT sequenziali.

    Erano sei round-trip, cinque dei quali su colonne senza indice: cinque
    scansioni complete di 3.906 righe a ogni creazione. Restano una regola
    applicativa e non una garanzia - il database non ha UNIQUE su nessuna di
    queste colonne - ma ora costano una query sola.
    """
    condizioni = [
        getattr(Cliente, attributo) == dati[attributo]
        for attributo, _ in CAMPI_UNIVOCI_CLIENTE
        if dati.get(attributo)
    ]
    if not condizioni:
        return

    for esistente in db.query(Cliente).filter(or_(*condizioni)).all():
        for attributo, messaggio in CAMPI_UNIVOCI_CLIENTE:
            atteso = dati.get(attributo)
            if atteso and getattr(esistente, attributo) == atteso:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=messaggio
                )


# =============================================================================
# Credenziali generate dal server
# =============================================================================
def genera_username(db: Session, nome: str, cognome: str) -> str:
    """`NomeCognome`, con un suffisso numerico se e' gia' preso.

    Il database non ha la UNIQUE su utente_username e contiene gia' cinque
    gruppi di omonimi. Prima l'username veniva scritto senza alcun controllo:
    al secondo Mario Rossi, trova_utente_per_username diventava ambiguo e il
    login veniva negato a entrambi.
    """
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
    """Le prime tre lettere di nome e cognome piu' l'id, come prima.

    Prima poteva uscire piu' corta del minimo - "Li Bo" con un id a una cifra
    fa cinque caratteri - e allora la creazione falliva con un 422 sulla policy
    di una password che l'operatore non aveva scelto, dopo avere gia' bruciato
    un valore di AUTO_INCREMENT. Qui si riempie con cifre casuali fino a
    superare la policy, cosi' la generazione non fallisce mai.

    LIMITE NOTO: la password resta ricavabile dal nome della persona. E' una
    scelta consapevole; la mitigazione e' l'obbligo di cambio al primo accesso,
    per cui le colonne utente_password_changed_at/_via esistono gia'.
    """
    base = f"{nome.strip()[:3]}{cognome.strip()[:3]}{utente_id}"

    candidato = base
    for _ in range(12):
        if not verifica_policy_password(candidato, username=username):
            return candidato
        candidato += str(secrets.randbelow(10))

    # Non dovrebbe accadere: dodici cifre in coda superano qualunque lunghezza
    # minima ragionevole. Se accade, meglio una password casuale che un 500.
    logger.warning("password generata dal nome rifiutata dalla policy, uso un valore casuale")
    return secrets.token_urlsafe(16)


def crea_utente_per_cliente(
    db: Session, nome: str, cognome: str, autore_id: int
) -> tuple[Utente, str]:
    """Crea la riga `utenti` e restituisce l'utente e la password in chiaro.

    L'utente si crea per primo perche' serve il suo utente_id: entra sia nella
    password generata sia in clienti.utente_id, che e' NOT NULL.
    """
    nuovo_utente = Utente(
        utente_username=f"temp-{uuid.uuid4()}",
        # NOT NULL nel database: stringa vuota, mai NULL, mai la password.
        utente_password="",
        utente_password_hash="",
        # -1, non 1. La convenzione legacy e' -1 = attivo, e sia il login sia
        # la validazione della sessione confrontano con -1: con 1 l'utente
        # appena creato riceveva lo stesso 401 di un account inesistente.
        utente_attivoSN=ATTIVO,
    )
    db.add(nuovo_utente)
    db.flush()  # genera utente_id

    username = genera_username(db, nome, cognome)
    password_in_chiaro = genera_password(nome, cognome, nuovo_utente.utente_id, username)

    nuovo_utente.utente_username = username
    nuovo_utente.utente_created_by = autore_id
    nuovo_utente.utente_updated_by = autore_id
    # utente_padre contiene un utente_id: la FK del database punta a
    # utenti(utente_id), non a clienti(cliente_id).
    nuovo_utente.utente_padre = autore_id
    nuovo_utente.utente_password_hash = hash_password(password_in_chiaro)
    nuovo_utente.utente_password_algo = "bcrypt"
    # Generato dal server: bcrypt non lo usa, la colonna resta per
    # compatibilita' con la piattaforma legacy.
    nuovo_utente.utente_salt = str(uuid.uuid4())

    return nuovo_utente, password_in_chiaro


# =============================================================================
# Costruzione dei payload: funzioni pure, testabili senza database
# =============================================================================
CAMPI_UNIVERSITA = frozenset(UniversitaBase.model_fields.keys())


def payload_cliente(
    dati: dict[str, Any], tipo_utente: TipoUtente, utente_id: int
) -> dict[str, Any]:
    """I campi della riga `clienti`, separati da quelli del curriculum.

    `cliente_ruolo` resta quello ricevuto (0 dal form): il ruolo si assegna
    dopo, dalla scheda utente. Finche' e' 0 l'utente non accede, ed e' voluto.
    """
    payload = {
        chiave: valore
        for chiave, valore in dati.items()
        if chiave not in CAMPI_UNIVERSITA
        and chiave not in {"utente_username", "utente_password"}
        # Un None in creazione significa "non fornito", e va tolto: omettere
        # la colonna nella INSERT lascia agire il DEFAULT della tabella, che
        # per le nullable e' NULL e per le NOT NULL e' '' o 0. Scrivere None
        # esplicito su cliente_telefono, cliente_CAP, cliente_provincia,
        # cliente_provinciaNascita, cliente_tipoDocumento o cliente_sesso -
        # tutte NOT NULL DEFAULT '' - faceva fallire l'intera creazione, e il
        # frontend manda proprio `formData.x || null` per ognuna di queste.
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
    """I campi del curriculum formativo.

    I cinque flag legacy non si toccano qui: li ha gia' normalizzati il
    validatore di UniversitaBase, che vale per tutti i percorsi di scrittura e
    non solo per questo. Prima la conversione stava in questa funzione,
    scriveva 1 dove la colonna vuole -1, e un -1 in ingresso finiva nell'else
    e veniva salvato 0.

    Dei campi vuoti resta una sola regola: si omettono, e la colonna prende il
    DEFAULT della tabella. Erano tre diramazioni che assegnavano tutte None -
    dieci righe equivalenti a una - e su universita_immatricolato e le altre
    quattro colonne NOT NULL quel None sarebbe stato un errore.
    """
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

    nuovo_utente, password_in_chiaro = crea_utente_per_cliente(
        db, dati["cliente_nome"], dati["cliente_cognome"], autore_id
    )

    nuovo_cliente = Cliente(
        **payload_cliente(dati, tipo_utente, nuovo_utente.utente_id)
    )
    db.add(nuovo_cliente)
    db.flush()  # genera cliente_id, indispensabile per il curriculum

    db.add(
        Universita(
            **payload_universita(dati, nuovo_cliente.cliente_id, autore_id)
        )
    )

    return {
        "cliente": nuovo_cliente,
        "utente": nuovo_utente,
        "password_in_chiaro": password_in_chiaro,
    }
