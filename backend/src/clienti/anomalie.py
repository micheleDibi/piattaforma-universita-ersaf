"""Avvisi sui dati storici: nessuna anagrafica fuori visibilita' viene rivelata."""

from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.auth.visibilita import Visibilita, filtra_clienti
from src.clienti.models import Cliente
from src.clienti.schemas import _valida_codice_fiscale, _valida_email
from src.clienti.servizio import CAMPI_UNIVOCI_CLIENTE

ETICHETTE = {
    "cliente_codice_fiscale": "Codice fiscale", "cliente_email": "Email",
    "cliente_telefono": "Telefono", "cliente_cellulare": "Cellulare",
    "cliente_pec": "PEC", "cliente_documento": "Numero documento",
}


def _chiave(valore) -> str:
    pulito = (valore or "").strip().lower()
    return pulito if any(c.isalnum() for c in pulito) else ""


def _duplicati(db: Session, clienti: list[Cliente], attributo: str, vis: Visibilita) -> dict:
    valori = {_chiave(getattr(c, attributo)) for c in clienti} - {""}
    mappa = defaultdict(list)
    if not valori:
        return mappa
    colonna = getattr(Cliente, attributo)
    query = db.query(Cliente.cliente_id, colonna, Cliente.cliente_nome, Cliente.cliente_cognome)
    query = filtra_clienti(query, vis).filter(func.lower(func.trim(colonna)).in_(valori))
    for cid, valore, nome, cognome in query.order_by(Cliente.cliente_id):
        nominativo = f"{nome or ''} {cognome or ''}".strip() or f"cliente #{cid}"
        mappa[_chiave(valore)].append((cid, nominativo))
    return mappa


def annota_anomalie(db: Session, clienti: list[Cliente], vis: Visibilita) -> None:
    """Query limitate ai valori della pagina e ai clienti visibili, anche su altre pagine."""
    if not clienti:
        return
    mappe = {campo: _duplicati(db, clienti, campo, vis) for campo, _ in CAMPI_UNIVOCI_CLIENTE}
    for cliente in clienti:
        avvisi = []
        for campo, valida in (("cliente_codice_fiscale", _valida_codice_fiscale), ("cliente_email", _valida_email)):
            valore = getattr(cliente, campo)
            if _chiave(valore):
                try:
                    valida(valore)
                except ValueError as errore:
                    avvisi.append(str(errore))
        for campo, mappa in mappe.items():
            altri = [nome for cid, nome in mappa.get(_chiave(getattr(cliente, campo)), []) if cid != cliente.cliente_id]
            if altri:
                avvisi.append(f"{ETICHETTE[campo]} duplicato con: {', '.join(altri)}")
        cliente.anomalie = avvisi
