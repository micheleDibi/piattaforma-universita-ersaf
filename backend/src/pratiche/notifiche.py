"""Email sui cambi di stato della pratica (porting ridotto di Pratica.AfterSave).

Solo i due template che esistono davvero in messaggi_email e che lo script
originale collega a un cambio di stato: 'pratica_bozza' (al cliente, quando
la pratica raggiunge per la prima volta lo stato Bozza) e
'nuova_pratica_ersaf' (a ERSAF, quando raggiunge per la prima volta lo stato
Caricata). Nessuno dei due ha segnaposto {{...}}, quindi non serve passare
alcun valore dinamico.

Stesso schema di notifiche/email.py: sessione propria (gira in
BackgroundTasks, dopo che la risposta e' partita, mai dentro il ciclo di
richiesta) ed errori solo loggati, mai propagati - un'email non inviata non
deve far sembrare fallito un salvataggio gia' andato a buon fine.
"""
from __future__ import annotations

import logging

from src.config import get_impostazioni
from src.database import SessionLocal
from src.notifiche.backend_invio import Mailer
from src.notifiche.email import carica_template, componi, rendi_html, rendi_oggetto

logger = logging.getLogger("ersaf.email")

CODICE_PRATICA_BOZZA = "pratica_bozza"
CODICE_NUOVA_PRATICA_ERSAF = "nuova_pratica_ersaf"


def _invia(mailer: Mailer, codice_template: str, destinatario: str) -> None:
    db = SessionLocal()
    try:
        oggetto_grezzo, corpo_grezzo = carica_template(db, codice_template)
        messaggio = componi(rendi_oggetto(oggetto_grezzo, {}), rendi_html(corpo_grezzo, {}), destinatario)
        mailer.invia(messaggio)
        logger.info("mail '%s' inviata", codice_template)
    except Exception:
        logger.exception("invio della mail '%s' fallito", codice_template)
    finally:
        db.close()


def invia_mail_pratica_bozza(mailer: Mailer, destinatario: str) -> None:
    _invia(mailer, CODICE_PRATICA_BOZZA, destinatario)


def invia_mail_nuova_pratica_ersaf(mailer: Mailer) -> None:
    # Letta a ogni invio, non a import-time: cambiarla in .env non deve
    # richiedere una modifica al codice, solo un riavvio (vedi config.py).
    _invia(mailer, CODICE_NUOVA_PRATICA_ERSAF, get_impostazioni().email_notifiche_pratiche)
