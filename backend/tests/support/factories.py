"""Costruzione degli scenari di prova.

NESSUN DATO REALE. Tutti gli indirizzi usano @example.org (RFC 2606) e l'host
SMTP e' smtp.invalid (RFC 6761): un errore di configurazione non deve poter
mandare posta a una persona vera. `dump.sql` non e' e non deve diventare la
sorgente dei dati di test.
"""

from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.clienti.models import Cliente
from src.utenti.models import Utente

_contatore = itertools.count(1)

# Ruoli, dalla tabella `ruoli`: 0 Utente, 1 Aderente, 2 Regionale,
# 3 Provinciale, 4 Consulente, 5 Nazionale, 6 Operatore.
RUOLO_SOTTOSCRITTORE = 0
RUOLO_ADERENTE = 1
RUOLO_REGIONALE = 2
RUOLO_PROVINCIALE = 3
RUOLO_CONSULENTE = 4
RUOLO_NAZIONALE = 5
RUOLO_OPERATORE = 6

ATTIVO = -1
DISATTIVO = 0


@dataclass
class Attuatore:
    utente_id: int
    cliente_id: int
    username: str
    email: str
    password_chiaro: str | None


def crea_utente(
    db: Session,
    *,
    username: str | None = None,
    password_chiaro: str | None = None,
    password_hash: str | None = None,
    attivo: int = ATTIVO,
) -> Utente:
    """Crea una riga `utenti`.

    utente_created_by / utente_updated_by / utente_padre restano a NULL: la
    tabella ha due chiavi esterne verso se stessa e su un database vuoto
    qualunque valore diverso da NULL fallirebbe.

    `utente_password` e' NOT NULL: quando non c'e' una password legacy si
    scrive '', che e' anche cio' che il codice scrive dopo il rehash.
    """
    numero = next(_contatore)
    utente = Utente(
        utente_username=username or f"utente{numero}",
        utente_password=password_chiaro if password_chiaro is not None else "",
        utente_password_hash=password_hash,
        utente_password_algo="bcrypt" if password_hash else "legacy_plaintext",
        utente_attivoSN=attivo,
        utente_padre=None,
        utente_created_by=None,
        utente_updated_by=None,
        utente_salt=str(uuid.uuid4()),
    )
    db.add(utente)
    db.commit()
    db.refresh(utente)
    return utente


def crea_cliente(
    db: Session,
    *,
    utente_id: int,
    email: str,
    ruolo: int = RUOLO_ADERENTE,
    nome: str = "Mario",
    cognome: str = "Rossi",
) -> Cliente:
    numero = next(_contatore)
    cliente = Cliente(
        cliente_codice=f"COD{numero:06d}",
        cliente_nome=nome,
        cliente_cognome=cognome,
        cliente_email=email,
        cliente_telefono="",
        cliente_indirizzo="",
        cliente_civico="",
        cliente_citta="",
        cliente_CAP="",
        cliente_provincia="",
        cliente_cellulare="",
        utente_id=utente_id,
        cliente_luogoNascita="",
        cliente_provinciaNascita="",
        cliente_dataNascita="1999-12-31",
        cliente_cittadinanza="",
        cliente_tipoDocumento="",
        cliente_documento="",
        cliente_comuneRilascio="",
        cliente_dataRilascio="1999-12-31",
        cliente_dataScadenzaDocumento="1999-12-31",
        cliente_sesso="",
        cliente_ruolo=ruolo,
        cliente_abilPraticheUniv=0,
        cliente_abilitazione_ecampus=0,
        cliente_abilitazione_link_campus=0,
        cliente_abilitazione_corsi_speciali=0,
        cliente_abilitazione_a4u=0,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def crea_attuatore(
    db: Session,
    *,
    email: str,
    ruolo: int = RUOLO_ADERENTE,
    attivo: int = ATTIVO,
    username: str | None = None,
    password_chiaro: str | None = None,
    password_hash: str | None = None,
    nome: str = "Mario",
) -> Attuatore:
    """Utente piu' cliente: la coppia che il recupero password deve trovare."""
    utente = crea_utente(
        db,
        username=username,
        password_chiaro=password_chiaro,
        password_hash=password_hash,
        attivo=attivo,
    )
    cliente = crea_cliente(
        db, utente_id=utente.utente_id, email=email, ruolo=ruolo, nome=nome
    )
    return Attuatore(
        utente_id=utente.utente_id,
        cliente_id=cliente.cliente_id,
        username=utente.utente_username,
        email=email,
        password_chiaro=password_chiaro,
    )


def crea_utente_orfano(db: Session, **kwargs) -> Utente:
    """Utente SENZA riga `clienti`: nel dump sono 869, e sono quelli su cui
    /auth/login restituiva 500."""
    return crea_utente(db, **kwargs)
