"""Generazione del codice pratica: numerazione atomica per prefisso.

Adattamento della logica della piattaforma Instant Developer (il codice
originale, ricevuto per la card Trello "Creazione Pratica - Salvataggio -
Codice", leggeva MAX(PraticaNumero) per prefisso). Stesso formato
[A4U_]<prefisso a 2 lettere><6 cifre>, es. MT000042, A4U_CP000007, con due
differenze volute:

- il numero viene da pratiche_contatori con incremento atomico (vedi
  prossimo_numero), non da un MAX ricalcolato ogni volta: due salvataggi
  concorrenti con lo stesso prefisso non possono piu' generare lo stesso
  codice (vedi db/migrations/020_contatori_codice_pratica.sql);
- il prefisso si sceglie da listino_tipo_corso_id, un id stabile gia' usato
  per le caratteristiche del percorso (vedi campiPercorsoVisibili in
  frontend/src/config/pratica.js), invece che da un confronto testuale sulla
  descrizione del tipo di corso: piu' robusto, e non dipende da un ordine di
  controlli particolare per distinguere casi come "MASTER" da "... FORMAZIONE".

Uso (dentro la stessa transazione dell'INSERT della pratica, vedi
backend/src/pratiche/routers.py::crea_pratica):

    codici = genera_codici_pratica(
        db,
        nome_universita_codice=nuova_pratica.universita.nome_universita_codice,
        listino_tipo_corso_id=nuova_pratica.listino_tipo_corso_id,
    )
    if codici:
        nuova_pratica.pratica_numero = codici.numero
        if codici.codice_asg:
            nuova_pratica.pratica_codiceASG = codici.codice_asg
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.errori import CodicePraticaError

CIFRE_NUMERO = 6

# Verificato contro nome_universita reale: le uniche righe con codice SSML e
# A4U sono quelle due, come nell'originale Instant Developer.
UNIVERSITA_CON_CODICE = frozenset({"SSML", "A4U"})

# listino_tipoCorso_id -> prefisso, stessa tassonomia documentata in testa a
# frontend/src/lib/configPratiche.js (1=MASTER, 2=MASTER AREA SCUOLA,
# 3=MASTER CLASSI DI CONCORSO, 4=CORSI DI PERFEZIONAMENTO, 5=PERCORSO DOCENTI,
# 6=CORSI DI FORMAZIONE, 7=CORSI DI ALTA FORMAZIONE, 8=LAUREE, 9=CORSI
# SINGOLI, 10=CORSI SPECIALI). Il 5 (Percorso docenti) resta fuori apposta:
# come nell'originale, un tipo corso senza prefisso associato blocca la
# generazione invece di produrre un codice sbagliato.
PREFISSI_PER_TIPO_CORSO = {
    1: "MT", 2: "MT", 3: "MT",
    4: "CP", 10: "CP",
    6: "AF", 7: "AF",
    8: "CL",
    9: "CS",
}


@dataclass(frozen=True)
class CodiciPratica:
    numero: str
    codice_asg: Optional[str]


def prefisso_tipo_corso(listino_tipo_corso_id: Optional[int]) -> str:
    prefisso = PREFISSI_PER_TIPO_CORSO.get(listino_tipo_corso_id)
    if prefisso is None:
        raise CodicePraticaError(
            "Tipo corso senza prefisso associato per il codice pratica: "
            f"listino_tipo_corso_id={listino_tipo_corso_id!r}"
        )
    return prefisso


def prefisso_pratica(nome_universita_codice: str, listino_tipo_corso_id: Optional[int]) -> str:
    base = prefisso_tipo_corso(listino_tipo_corso_id)
    return f"A4U_{base}" if nome_universita_codice == "A4U" else base


def formatta_codice(prefisso: str, numero: int) -> str:
    if not 1 <= numero < 10**CIFRE_NUMERO:
        raise CodicePraticaError(f"Numero pratica fuori range per {prefisso}: {numero}")
    return f"{prefisso}{numero:0{CIFRE_NUMERO}d}"


# Incremento atomico: la riga del contatore resta bloccata fino al commit,
# quindi pratiche concorrenti con lo stesso prefisso vengono serializzate. Se
# la transazione fa rollback, anche l'incremento viene annullato (niente
# buchi nella numerazione). LAST_INSERT_ID() e' per connessione: la Session
# usa la stessa connessione per tutta la transazione, quindi il valore letto
# e' sempre il nostro, anche con altre connessioni concorrenti allo stesso
# prefisso.
_SQL_INCREMENTA = text(
    """
    INSERT INTO pratiche_contatori (prefisso, ultimo_numero)
    VALUES (:prefisso, LAST_INSERT_ID(1))
    ON DUPLICATE KEY UPDATE ultimo_numero = LAST_INSERT_ID(ultimo_numero + 1)
    """
)


def prossimo_numero(db: Session, prefisso: str) -> int:
    db.execute(_SQL_INCREMENTA, {"prefisso": prefisso})
    return int(db.execute(text("SELECT LAST_INSERT_ID()")).scalar_one())


# Come _SQL_INCREMENTA, ma il risultato non scende mai sotto minimo + 1. Serve
# ai progressivi che anche il gestionale precedente continua a scrivere con
# MAX(...) + 1: ogni uso riallinea il contatore, invece di un seed una tantum.
_SQL_INCREMENTA_OLTRE = text(
    """
    INSERT INTO pratiche_contatori (prefisso, ultimo_numero)
    VALUES (:prefisso, LAST_INSERT_ID(:minimo + 1))
    ON DUPLICATE KEY UPDATE
        ultimo_numero = LAST_INSERT_ID(GREATEST(ultimo_numero, :minimo) + 1)
    """
)


def prossimo_numero_oltre(db: Session, prefisso: str, minimo: int) -> int:
    """Prossimo numero per `prefisso`, comunque maggiore di `minimo`.

    `minimo` puo' venire da una lettura non bloccante e quindi essere vecchio:
    fra due chiamate di questo backend decide comunque il contatore, letto
    sempre aggiornato sotto il blocco della sua riga.
    """
    db.execute(_SQL_INCREMENTA_OLTRE, {"prefisso": prefisso, "minimo": minimo})
    return int(db.execute(text("SELECT LAST_INSERT_ID()")).scalar_one())


def genera_codici_pratica(
    db: Session,
    *,
    nome_universita_codice: Optional[str],
    listino_tipo_corso_id: Optional[int],
) -> Optional[CodiciPratica]:
    """I codici per una pratica NUOVA, o None se l'universita' non prevede
    codifica: solo SSML e A4U hanno una numerazione automatica, le altre
    lasciano pratica_numero vuoto come prima di questa funzione.
    """
    codice = (nome_universita_codice or "").strip().upper()
    if codice not in UNIVERSITA_CON_CODICE:
        return None

    prefisso = prefisso_pratica(codice, listino_tipo_corso_id)
    numero = formatta_codice(prefisso, prossimo_numero(db, prefisso))
    return CodiciPratica(numero=numero, codice_asg=numero if codice == "SSML" else None)
