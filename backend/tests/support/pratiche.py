"""Lookup e pulizia delle sole pratiche sintetiche della suite locale."""

from sqlalchemy import delete, text

from src.pratiche.models import Pratica
from src.pratiche_stati_storico.models import PraticaStatoStorico
from tests.support import contabilita


def pulisci_pratiche(connessione):
    contabilita.svuota(connessione)
    connessione.execute(delete(PraticaStatoStorico))
    connessione.execute(delete(Pratica))


def prepara_lookup(connessione):
    for numero, nome in ((1, "Caricata"), (6, "Bozza")):
        connessione.execute(text("""
            INSERT INTO pratiche_stati
                (pratica_stato_id, pratica_stato_codice, pratica_stato_descrizione)
            VALUES (:numero, :nome, :nome)
            ON DUPLICATE KEY UPDATE pratica_stato_id=VALUES(pratica_stato_id)
        """), {"numero": numero, "nome": nome})
    for codice in ("pratica_bozza", "nuova_pratica_ersaf"):
        connessione.execute(text("""
            INSERT INTO messaggi_email
                (messaggio_email_codice, messaggio_email_oggetto, messaggio_email_testo)
            VALUES (:codice, 'Aggiornamento della pratica', '<p>La pratica e stata salvata.</p>')
            ON DUPLICATE KEY UPDATE messaggio_email_codice=VALUES(messaggio_email_codice)
        """), {"codice": codice})
