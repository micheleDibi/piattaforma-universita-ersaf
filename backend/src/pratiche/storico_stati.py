"""Storico dei cambi di stato di una pratica (porting ridotto di Pratica.AfterSave).

pratiche_stati_storico esiste gia' nello schema ma prima di questo modulo non
la scriveva nessuno. Va usata DENTRO la stessa transazione del salvataggio
della pratica, prima del commit: la riga di storico deve valere solo se il
salvataggio va a buon fine.

Gli stati si riconoscono per id, non per pratica_stato_codice o
pratica_stato_descrizione: 6 = Bozza, 1 = Caricata, stessa mappa gia' usata
in frontend/src/lib/pannelloPratiche.js (STATI_PANNELLO) e confermata contro
i dati reali.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from src.pratiche.models import Pratica
from src.pratiche_stati_storico.models import PraticaStatoStorico

STATO_BOZZA_ID = 6
STATO_CARICATA_ID = 1


def stato_gia_raggiunto(db: Session, pratica_id: int, pratica_stato_id: int) -> bool:
    """Vero se la pratica e' gia' passata per questo stato in precedenza:
    l'email di 'prima volta' va mandata una volta sola."""
    return db.query(PraticaStatoStorico.pratica_stato_storico_id).filter(
        PraticaStatoStorico.pratica_id == pratica_id,
        PraticaStatoStorico.pratica_stato_id == pratica_stato_id,
    ).first() is not None


def registra_stato(db: Session, pratica: Pratica, utente_id: int) -> None:
    """Aggiunge la riga di storico per lo stato ATTUALE (pratica.pratica_stato_id)."""
    db.add(PraticaStatoStorico(
        pratica_id=pratica.pratica_id,
        pratica_stato_id=pratica.pratica_stato_id,
        pratica_stato_storico_created_by=utente_id,
        pratica_stato_storico_updated_by=utente_id,
    ))
