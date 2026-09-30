"""Operazioni dopo la creazione di una pratica (porting di Pratica.AfterSave).

Riferimento: lo script ricevuto per la card Trello "Creazione Pratica - Post
Salvataggio". Qui c'e' la parte che mancava; il resto era gia' altrove:
storico degli stati ed email di "prima volta" in storico_stati.py e
notifiche.py, codice pratica in codice.py.

Da chiamare DENTRO la transazione di POST /pratiche/, dopo il flush e dopo
genera_codici_pratica, prima del commit. Se qualcosa manca si solleva
ContabilitaPraticaError e non viene scritto nulla: ne' la pratica, ne' i
contatori, ne' righe nello schema dei pagamenti.

- A4U: una riga in pratica_codice con codice temporaneo e permanente uguali a
  pratica_numero. Sui dati reali coincidono sempre, e il permanente viene
  assegnato alla creazione.
- SSML e A4U: articolo ARTICOLO_PRATICA_<n> e partitario (documento)
  PARTITARIO_PRATICA_<n>, con i due collegamenti articolo_pratica e
  documento_articolo. Stanno nello schema dei pagamenti
  (SCHEMA_GESTIONE_PAGAMENTI), sullo stesso server: si scrivono con la
  connessione principale, cosi' tutto resta in un'unica transazione.

Differenze volute rispetto all'originale:
- solo alla creazione. L'originale girava a ogni salvataggio e creava
  l'articolo quando mancava: modificare una pratica storica ne avrebbe
  generato uno con il prezzo di oggi;
- il gruppo articolo si sceglie dall'id del tipo di corso, come il prefisso
  del codice, e non componendo 'PRATICA ' + descrizione: per Master area
  scuola, Master classi di concorso e Corsi di formazione quel gruppo non
  esiste;
- i progressivi vengono da pratiche_contatori, riallineati a ogni uso al
  massimo gia' presente (vedi prossimo_numero_oltre), non da un MAX + 1;
- nessuna cartella FTP: ftp_path non ha percorsi per le pratiche e il
  backend non gestisce ancora il caricamento dei file;
- pratica_pathFile non viene azzerato al cambio di stato: e' il nome del PDF
  del gestionale precedente, che questo backend non legge (il documento si
  compone al momento, vedi src/documenti).
"""
from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config import get_impostazioni
from src.errori import ContabilitaPraticaError
from src.pratiche.codice import UNIVERSITA_CON_CODICE, prossimo_numero_oltre
from src.pratiche.models import Pratica

PREFISSO_ARTICOLO = "ARTICOLO_PRATICA_"
PREFISSO_PARTITARIO = "PARTITARIO_PRATICA_"
TIPO_ARTICOLO = "PRATICA"

# listino_tipoCorso_id -> articolo_gruppo_codice. Stessa tassonomia di
# PREFISSI_PER_TIPO_CORSO in codice.py, confrontata con gli articoli gia'
# presenti nel database dei pagamenti. Il 5 (Percorso docenti) manca anche
# li': la pratica viene rifiutata prima, dal codice pratica.
GRUPPI_PER_TIPO_CORSO = {
    1: "PRATICA MASTER", 2: "PRATICA MASTER", 3: "PRATICA MASTER",
    4: "PRATICA CORSI DI PERFEZIONAMENTO",
    6: "PRATICA CORSI DI ALTA FORMAZIONE", 7: "PRATICA CORSI DI ALTA FORMAZIONE",
    8: "PRATICA LAUREE",
    9: "PRATICA CORSI SINGOLI",
    10: "PRATICA CORSI SPECIALI",
}

LUNGHEZZA_DESCRIZIONE = 255  # articolo.articolo_descrizione


def dopo_creazione(
    db: Session,
    pratica: Pratica,
    utente_id: int,
    *,
    nome_universita_codice: Optional[str],
) -> None:
    universita = (nome_universita_codice or "").strip().upper()
    if universita not in UNIVERSITA_CON_CODICE:
        return
    if universita == "A4U":
        _registra_codice_a4u(db, pratica, utente_id)
    _crea_articolo_e_partitario(db, pratica, utente_id)


def schema_pagamenti() -> str:
    nome = get_impostazioni().schema_gestione_pagamenti
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", nome):
        # Errore di configurazione, non della richiesta: 500, non 400.
        raise RuntimeError("SCHEMA_GESTIONE_PAGAMENTI non e' un nome di schema valido")
    return f"`{nome}`"


def _registra_codice_a4u(db: Session, pratica: Pratica, utente_id: int) -> None:
    if not pratica.pratica_numero:
        raise ContabilitaPraticaError("Pratica A4U senza codice: impossibile registrarlo.")
    db.execute(
        text(
            """
            INSERT INTO pratica_codice
                (pratica_id, pratica_codice_temporanreo, pratica_codice_permanente,
                 pratica_codice_created_by, pratica_codice_created_at,
                 pratica_codice_updated_by, pratica_codice_updated_at,
                 pratica_codice_assigned_by, pratica_codice_assigned_at)
            VALUES (:pratica, :numero, :numero, :utente, NOW(), :utente, NOW(), :utente, NOW())
            """
        ),
        {"pratica": pratica.pratica_id, "numero": pratica.pratica_numero, "utente": utente_id},
    )


def _massimo_esistente(db: Session, schema: str, tabella: str, colonna: str, prefisso: str) -> int:
    # Lettura non bloccante: il contatore decide fra le transazioni di questo
    # backend (vedi prossimo_numero_oltre), qui serve solo a non restare
    # indietro rispetto ai codici scritti dal gestionale precedente.
    return int(db.execute(
        text(
            f"""
            SELECT COALESCE(MAX(CAST(SUBSTRING({colonna}, :inizio) AS UNSIGNED)), 0)
              FROM {schema}.{tabella}
             WHERE {colonna} REGEXP :formato
            """
        ),
        {"inizio": len(prefisso) + 1, "formato": f"^{prefisso}[0-9]+$"},
    ).scalar_one())


def _crea_articolo_e_partitario(db: Session, pratica: Pratica, utente_id: int) -> None:
    schema = schema_pagamenti()

    gruppo_codice = GRUPPI_PER_TIPO_CORSO.get(pratica.listino_tipo_corso_id)
    if gruppo_codice is None:
        raise ContabilitaPraticaError(
            "Tipo corso senza gruppo articolo associato: "
            f"listino_tipo_corso_id={pratica.listino_tipo_corso_id!r}"
        )

    dati = db.execute(
        text(
            """
            SELECT tc.listino_tipoCorso_descrizione AS tipo_corso,
                   lt.listTesta_codice             AS listino_codice,
                   lt.listTesta_descrizione        AS listino_descrizione,
                   c.cliente_nome, c.cliente_cognome,
                   (SELECT f.cliente_id FROM clienti f
                     WHERE f.utente_id = p.utente_id
                     ORDER BY f.cliente_id LIMIT 1) AS fornitore_id
              FROM pratiche p
              JOIN clienti c ON c.cliente_id = p.cliente_id
              LEFT JOIN listini_testa lt ON lt.listTesta_id = p.listTesta_id
              LEFT JOIN listini_tipicorsi tc ON tc.listino_tipoCorso_id = p.listino_tipo_corso_id
             WHERE p.pratica_id = :pratica
            """
        ),
        {"pratica": pratica.pratica_id},
    ).mappings().one()
    if not dati["tipo_corso"]:
        raise ContabilitaPraticaError(
            f"Tipo corso inesistente: listino_tipo_corso_id={pratica.listino_tipo_corso_id!r}"
        )
    # documento.fornitore_id e' NOT NULL: il fornitore e' il primo cliente
    # dell'utente della pratica, come nel gestionale (verificato su tutti i
    # partitari esistenti).
    if dati["fornitore_id"] is None:
        raise ContabilitaPraticaError(
            "L'utente della pratica non ha un cliente da indicare come fornitore nel partitario."
        )

    articolo_tipo_id = db.execute(
        text(f"SELECT articolo_tipo_id FROM {schema}.articolo_tipo "
             "WHERE articolo_tipo_codice = :codice ORDER BY articolo_tipo_id LIMIT 1"),
        {"codice": TIPO_ARTICOLO},
    ).scalar_one_or_none()
    if articolo_tipo_id is None:
        raise ContabilitaPraticaError(f"Tipo articolo '{TIPO_ARTICOLO}' mancante.")
    articolo_gruppo_id = db.execute(
        text(f"SELECT articolo_gruppo_id FROM {schema}.articolo_gruppo "
             "WHERE articolo_gruppo_codice = :codice ORDER BY articolo_gruppo_id LIMIT 1"),
        {"codice": gruppo_codice},
    ).scalar_one_or_none()
    if articolo_gruppo_id is None:
        raise ContabilitaPraticaError(f"Gruppo articolo '{gruppo_codice}' mancante.")

    numero_articolo = prossimo_numero_oltre(
        db, PREFISSO_ARTICOLO,
        _massimo_esistente(db, schema, "articolo", "articolo_codice", PREFISSO_ARTICOLO),
    )
    numero_partitario = prossimo_numero_oltre(
        db, PREFISSO_PARTITARIO,
        _massimo_esistente(db, schema, "documento", "documento_codice", PREFISSO_PARTITARIO),
    )
    codice_partitario = f"{PREFISSO_PARTITARIO}{numero_partitario}"

    # Stesso testo del gestionale, es. "Documento di riferimento:
    # PARTITARIO_PRATICA_3528 - Pratica per CORSI SINGOLI: MED/42 - IGIENE
    # GENERALE di Mario Rossi".
    descrizione = (
        f"Documento di riferimento: {codice_partitario} - "
        f"Pratica per {dati['tipo_corso']}: "
        f"{dati['listino_codice'] or ''} - {dati['listino_descrizione'] or ''} "
        f"di {dati['cliente_nome'] or ''} {dati['cliente_cognome'] or ''}"
    ).strip()[:LUNGHEZZA_DESCRIZIONE]

    articolo_id = db.execute(
        text(
            f"""
            INSERT INTO {schema}.articolo
                (articolo_codice, articolo_descrizione, articolo_prezzo,
                 articolo_tipo_id, articolo_gruppo_id,
                 articolo_createdBy, articolo_createdAt, articolo_updatedBy, articolo_updatedAt)
            VALUES (:codice, :descrizione, :prezzo, :tipo, :gruppo, :utente, NOW(), :utente, NOW())
            """
        ),
        {"codice": f"{PREFISSO_ARTICOLO}{numero_articolo}", "descrizione": descrizione,
         "prezzo": pratica.pratica_prezzo, "tipo": articolo_tipo_id, "gruppo": articolo_gruppo_id,
         "utente": utente_id},
    ).lastrowid

    db.execute(
        text(
            f"""
            INSERT INTO {schema}.articolo_pratica
                (articolo_id, pratica_id,
                 articolo_pratica_createdBy, articolo_pratica_createdAt,
                 articolo_pratica_updatedBy, articolo_pratica_updatedAt)
            VALUES (:articolo, :pratica, :utente, NOW(), :utente, NOW())
            """
        ),
        {"articolo": articolo_id, "pratica": pratica.pratica_id, "utente": utente_id},
    )

    documento_id = db.execute(
        text(
            f"""
            INSERT INTO {schema}.documento
                (documento_codice, documento_totale, cliente_id, fornitore_id,
                 documento_createdBy, documento_createdAt,
                 documento_updatedBy, documento_updatedAt, documento_data_creazione)
            VALUES (:codice, :prezzo, :cliente, :fornitore, :utente, NOW(), :utente, NOW(), CURDATE())
            """
        ),
        {"codice": codice_partitario, "prezzo": pratica.pratica_prezzo,
         "cliente": pratica.cliente_id, "fornitore": dati["fornitore_id"], "utente": utente_id},
    ).lastrowid

    db.execute(
        text(
            f"""
            INSERT INTO {schema}.documento_articolo
                (documento_id, articolo_id,
                 doc_articolo_createdBy, doc_articolo_createdAt,
                 doc_articolo_updatedBy, doc_articolo_updatedAt)
            VALUES (:documento, :articolo, :utente, NOW(), :utente, NOW())
            """
        ),
        {"documento": documento_id, "articolo": articolo_id, "utente": utente_id},
    )
