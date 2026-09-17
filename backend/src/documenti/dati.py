"""I dati di una pratica nella forma che i modelli Typst si aspettano.

Tutto arriva come testo gia' formattato: il modello posiziona stringhe e non
deve sapere di date, importi o valori mancanti. Le scelte condizionali (quale
crocetta disegnare) le aggiunge ogni modello sopra questi dati comuni.

Il database del gestionale usa segnaposto invece di NULL: '' per i testi e
1999-12-31 per le date. Qui diventano stringa vuota, cosi' non finiscono
stampati nel modulo.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.pratiche.models import Pratica
from src.universita.models import Universita

DATA_SEGNAPOSTO = date(1999, 12, 31)


def testo(valore) -> str:
    """Stringa pulita; None e segnaposto diventano ''."""
    if valore is None:
        return ""
    if isinstance(valore, datetime):
        valore = valore.date()
    if isinstance(valore, date):
        return "" if valore == DATA_SEGNAPOSTO else valore.strftime("%d/%m/%Y")
    if isinstance(valore, Decimal):
        return importo(valore)
    return " ".join(str(valore).split())


def importo(valore: Decimal | float | int | None) -> str:
    """Formato italiano con due decimali: 1.250,00."""
    if valore is None:
        return ""
    intero, decimali = f"{Decimal(valore):.2f}".split(".")
    segno = "-" if intero.startswith("-") else ""
    cifre = intero.lstrip("-")
    gruppi = [cifre[max(i - 3, 0):i] for i in range(len(cifre), 0, -3)][::-1]
    return f"{segno}{'.'.join(gruppi)},{decimali}"


def _descrizione(oggetto, campo: str) -> str:
    return testo(getattr(oggetto, campo, None)) if oggetto is not None else ""


def generalita_di(db: Session, cliente_id: int) -> Universita | None:
    """La scheda "generalita' universitarie" del cliente; la piu' recente se ce ne sono piu'."""
    return db.scalar(
        select(Universita).where(Universita.cliente_id == cliente_id)
        .order_by(Universita.universita_id.desc()).limit(1)
    )


def _cliente(cliente) -> dict:
    campi = {
        "cognome": "cliente_cognome", "nome": "cliente_nome", "codice_fiscale": "cliente_codice_fiscale",
        "sesso": "cliente_sesso", "cittadinanza": "cliente_cittadinanza",
        "email": "cliente_email", "pec": "cliente_pec", "telefono": "cliente_telefono", "cellulare": "cliente_cellulare",
        "luogo_nascita": "cliente_luogoNascita", "provincia_nascita": "cliente_provinciaNascita",
        "data_nascita": "cliente_dataNascita",
        "tipo_documento": "cliente_tipoDocumento", "documento": "cliente_documento",
        "comune_rilascio": "cliente_comuneRilascio", "data_rilascio": "cliente_dataRilascio",
        "scadenza_documento": "cliente_dataScadenzaDocumento",
    }
    dati = {chiave: _descrizione(cliente, colonna) for chiave, colonna in campi.items()}
    dati["residenza"] = {
        "indirizzo": _descrizione(cliente, "cliente_indirizzo"), "civico": _descrizione(cliente, "cliente_civico"),
        "cap": _descrizione(cliente, "cliente_CAP"), "comune": _descrizione(cliente, "cliente_citta"),
        "provincia": _descrizione(cliente, "cliente_provincia"),
    }
    dati["domicilio"] = {
        "indirizzo": _descrizione(cliente, "cliente_indirizzoDomicilio"), "civico": _descrizione(cliente, "cliente_civicoDomicilio"),
        "cap": _descrizione(cliente, "cliente_CAPDomicilio"), "comune": _descrizione(cliente, "cliente_cittaDomicilio"),
        "provincia": _descrizione(cliente, "cliente_provinciaDomicilio"),
    }
    return dati


def _corso(listino) -> dict:
    return {
        "descrizione": _descrizione(listino, "listTesta_descrizione"),
        "codice": _descrizione(listino, "listTesta_codice"),
        "livello": _descrizione(listino, "listTesta_livello"),
        "ente": _descrizione(getattr(listino, "universita", None), "nome_universita_descrizione"),
        "tipo_corso": _descrizione(getattr(listino, "tipo_corso", None), "listino_tipoCorso_descrizione"),
        "durata": _descrizione(getattr(listino, "durata_laurea", None), "listino_durataLaurea_descrizione"),
        "facolta": _descrizione(getattr(listino, "facolta", None), "listino_facolta_descrizione"),
        "corso_laurea": _descrizione(getattr(listino, "corso_laurea", None), "listino_corsoLaurea_descrizione"),
    }


def _generalita(scheda: Universita | None) -> dict:
    """Tutte le colonne della scheda, senza il prefisso universita_, gia' come testo."""
    if scheda is None:
        return {}
    return {
        colonna.key.removeprefix("universita_"): testo(getattr(scheda, colonna.key))
        for colonna in Universita.__table__.columns
        if colonna.key not in {"universita_id", "cliente_id"} and not colonna.key.startswith(("universita_create", "universita_update"))
    }


def dati_pratica(db: Session, pratica: Pratica) -> tuple[dict, dict[str, bytes]]:
    """Dati comuni a tutti i modelli e allegati binari (la firma, se c'e')."""
    dati = {
        "pratica": {
            "numero": testo(pratica.pratica_numero),
            "anno_accademico": testo(pratica.pratica_annoAccademico),
            "data_creazione": testo(pratica.pratica_dataCreazione),
            "prezzo": importo(pratica.pratica_prezzo),
            "sede_erogazione": testo(pratica.pratica_sedeErogazione),
            "rinnovo": {
                "primo_anno": bool(pratica.pratica_rinnPrimoAnno),
                "secondo_anno": bool(pratica.pratica_rinnSecondoAnno),
                "terzo_anno": bool(pratica.pratica_rinnTerzoAnno),
            },
        },
        "cliente": _cliente(pratica.cliente),
        "corso": _corso(pratica.listino_testa),
        "generalita": _generalita(generalita_di(db, pratica.cliente_id)),
    }
    allegati = {"firma": pratica.pratica_firma} if pratica.pratica_firma else {}
    return dati, allegati
