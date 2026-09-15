from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased
from src.aziende_xcod.models import AziendaXCod
from src.auth.autorizzazioni import ruolo_di
from src.auth.servizio_login import cliente_principale


def discendenti_ids(db: Session, azienda_id: int) -> set[int]:
    """Id di azienda_id e di tutti i suoi discendenti (figli, figli dei
    figli, ... fino alle foglie), senza limite di profondita', tramite una
    CTE ricorsiva su aziende_xcod. L'azienda di partenza e' sempre inclusa
    nel risultato (coerente con "la propria azienda e' inclusa nella
    vista" delle regole di visibilita').
    """
    base = (
        select(AziendaXCod.azienda_figlia_id.label("azienda_id"))
        .where(AziendaXCod.azienda_padre_id == azienda_id)
        .where(AziendaXCod.azienda_figlia_id.isnot(None))
        .cte(name="discendenti", recursive=True)
    )
    figli = aliased(AziendaXCod)
    ricorsiva = base.union_all(
        select(figli.azienda_figlia_id).where(
            figli.azienda_padre_id == base.c.azienda_id,
            figli.azienda_figlia_id.isnot(None),
        )
    )
    righe = db.execute(select(ricorsiva.c.azienda_id)).scalars().all()
    return {azienda_id, *righe}


def padre_id_di(db: Session, azienda_id: int) -> Optional[int]:
    """Il padre "corrente" di un'azienda: si prende l'arco piu' recente con
    questa azienda come figlia. "Un padre per azienda" e' un vincolo
    applicativo, non garantito dal database (azienda_figlia_id non ha una
    UNIQUE), quindi qui si sceglie deterministicamente il piu' recente,
    stesso approccio usato per aderenti_dettagli.
    """
    arco = (
        db.query(AziendaXCod)
        .filter(AziendaXCod.azienda_figlia_id == azienda_id)
        .order_by(AziendaXCod.azienda_xCod_id.desc())
        .first()
    )
    return arco.azienda_padre_id if arco else None


def aziende_visibili_ids(db: Session, utente) -> Optional[set[int]]:
    """None = nessun filtro (nazionale, vede tutto).
    Un set = solo questi azienda_id sono visibili (chiunque altro).

    Il ruolo e l'azienda non sono su Utente ma si ricavano da Cliente,
    stessa strada di ruolo_di/cliente_principale usata nel resto di auth.
    """
    ruolo = (ruolo_di(db, utente.utente_id) or "").lower()
    if ruolo == "nazionale":
        return None

    cliente = cliente_principale(db, utente.utente_id)
    azienda_id = getattr(cliente, "azienda_id", None) if cliente else None
    if azienda_id is None:
        return set()
    return discendenti_ids(db, azienda_id)