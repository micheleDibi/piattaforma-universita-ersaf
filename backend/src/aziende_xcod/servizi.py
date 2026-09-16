"""Logica di attraversamento della gerarchia aziende (aziende_xcod) e delle
regole che ne dipendono: visibilita' per ruolo e cascata di reset delle
percentuali quando una modifica le porterebbe sopra il limite del padre.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from src.aziende_xcod.models import AziendaXCod
from src.aziende.models import Azienda, AderenteDettaglio
from src.aziende.schemas import AderenteDettaglioBase
from src.auth.autorizzazioni import ruolo_di
from src.auth.servizio_login import cliente_principale

CAMPI_PERCENTUALI = list(AderenteDettaglioBase.model_fields)

# Sentinella per distinguere "padre non specificato, usa quello attuale" da
# "padre esplicitamente None" (azienda radice) in calcola_cascata_percentuali.
_INVARIATO = object()


def discendenti_ids(db: Session, azienda_id: int) -> set[int]:
    """Id di azienda_id e di tutti i suoi discendenti (figli, figli dei
    figli, ... fino alle foglie), senza limite di profondita', tramite una
    CTE ricorsiva su aziende_xcod. L'azienda di partenza e' sempre inclusa
    nel risultato.
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


def figli_diretti_ids(db: Session, azienda_id: int) -> list[int]:
    """Solo i figli diretti (un livello): usata dalla cascata per scendere
    nell'albero un livello alla volta."""
    return [
        r[0]
        for r in db.query(AziendaXCod.azienda_figlia_id)
        .filter(AziendaXCod.azienda_padre_id == azienda_id)
        .filter(AziendaXCod.azienda_figlia_id.isnot(None))
        .all()
    ]


def padre_id_di(db: Session, azienda_id: int) -> Optional[int]:
    """Il padre "corrente" di un'azienda: si prende l'arco piu' recente con
    questa azienda come figlia. "Un padre per azienda" e' un vincolo
    applicativo, non garantito dal database (azienda_figlia_id non ha una
    UNIQUE).
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


def valori_percentuali_di(db: Session, azienda_id: Optional[int]) -> dict:
    """Le percentuali attualmente salvate per un'azienda, o tutte a 0 se non
    ha ancora un dettaglio salvato o se azienda_id e' None (azienda radice,
    nessun tetto)."""
    if azienda_id is None:
        return {campo: 0 for campo in CAMPI_PERCENTUALI}
    dettaglio = (
        db.query(AderenteDettaglio)
        .filter(AderenteDettaglio.azienda_id == azienda_id)
        .first()
    )
    return {
        campo: getattr(dettaglio, campo, 0) if dettaglio else 0
        for campo in CAMPI_PERCENTUALI
    }


def calcola_cascata_percentuali(
    db: Session,
    azienda_id: int,
    valori_proposti: dict,
    padre_id=_INVARIATO,
) -> dict[int, dict[str, int]]:
    """Simula il salvataggio di `valori_proposti` su azienda_id, sotto il
    padre indicato (o quello attuale, se non specificato), e propaga a
    cascata sui discendenti: un campo va a 0 - sull'azienda stessa o su un
    discendente, a qualunque profondita' - ogni volta che supera il valore
    (gia' eventualmente azzerato in un passaggio precedente) del proprio
    padre in quel campo.

    Non scrive nulla sul database. Ritorna solo le aziende i cui valori
    effettivi risulterebbero diversi da zero forzati a zero:
    {azienda_id: {campo: 0, ...}, ...}. Un dizionario vuoto significa
    "nessun reset necessario, si puo' applicare senza chiedere conferma".
    """
    if padre_id is _INVARIATO:
        padre_id = padre_id_di(db, azienda_id)

    modifiche: dict[int, dict[str, int]] = {}
    valori_padre = valori_percentuali_di(db, padre_id) if padre_id is not None else None

    effettivi = {}
    for campo in CAMPI_PERCENTUALI:
        proposto = valori_proposti.get(campo, 0)
        limite = valori_padre[campo] if valori_padre is not None else None
        if limite is not None and proposto > limite:
            effettivi[campo] = 0
            modifiche.setdefault(azienda_id, {})[campo] = 0
        else:
            effettivi[campo] = proposto

    coda = [(azienda_id, effettivi)]
    while coda:
        genitore_id, valori_genitore = coda.pop(0)
        for figlio_id in figli_diretti_ids(db, genitore_id):
            attuali_figlio = valori_percentuali_di(db, figlio_id)
            effettivi_figlio = {}
            for campo in CAMPI_PERCENTUALI:
                limite = valori_genitore[campo]
                valore = attuali_figlio[campo]
                if valore > limite:
                    effettivi_figlio[campo] = 0
                    modifiche.setdefault(figlio_id, {})[campo] = 0
                else:
                    effettivi_figlio[campo] = valore
            coda.append((figlio_id, effettivi_figlio))

    return modifiche


def applica_cascata_percentuali(
    db: Session, azienda_id: int, valori_proposti: dict, cascata: dict[int, dict[str, int]]
) -> None:
    """Scrive valori_proposti su azienda_id, sovrascrivendo con 0 i campi
    presenti in cascata[azienda_id], poi azzera solo i campi indicati per
    ogni altra azienda in cascata. Non fa il commit: il chiamante decide
    quando."""
    valori_azienda = dict(valori_proposti)
    valori_azienda.update(cascata.get(azienda_id, {}))

    dettaglio = (
        db.query(AderenteDettaglio)
        .filter(AderenteDettaglio.azienda_id == azienda_id)
        .first()
    )
    if dettaglio is None:
        dettaglio = AderenteDettaglio(azienda_id=azienda_id, **valori_azienda)
        db.add(dettaglio)
    else:
        for campo, valore in valori_azienda.items():
            setattr(dettaglio, campo, valore)

    for altra_azienda_id, campi in cascata.items():
        if altra_azienda_id == azienda_id:
            continue
        dettaglio_altra = (
            db.query(AderenteDettaglio)
            .filter(AderenteDettaglio.azienda_id == altra_azienda_id)
            .first()
        )
        if dettaglio_altra is None:
            continue  # nessuna riga salvata: il valore e' gia' 0 di default
        for campo, valore in campi.items():
            setattr(dettaglio_altra, campo, valore)


def descrivi_cascata(db: Session, cascata: dict[int, dict[str, int]]) -> list[dict]:
    """Traduce la cascata in qualcosa di leggibile per l'alert di conferma
    nel frontend: nome azienda invece del solo id, elenco campi azzerati."""
    descrizione = []
    for azienda_id, campi in cascata.items():
        azienda = db.query(Azienda).filter(Azienda.azienda_id == azienda_id).first()
        descrizione.append({
            "azienda_id": azienda_id,
            "azienda_ragione_sociale": azienda.azienda_ragione_sociale if azienda else None,
            "campi": sorted(campi.keys()),
        })
    return descrizione