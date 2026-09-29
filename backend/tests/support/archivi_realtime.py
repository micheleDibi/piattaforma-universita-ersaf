"""DDL sintetica condivisa dalle fixture HTTP, chat e realtime."""

from sqlalchemy import text
from src.chat_pratiche.models import Messaggio, StatoMessaggio

TICKET = [
    """CREATE TABLE IF NOT EXISTS messaggio (messaggio_id INT AUTO_INCREMENT PRIMARY KEY,
       messaggio_data_creazione DATETIME, messaggio_testo TEXT,utente_dest_id INT,
       utente_dest_denominazione VARCHAR(255),utente_mitt_id INT,utente_mitt_denominazione VARCHAR(255),
       messaggio_doc_id VARCHAR(60),messaggio_lettoSN INT)""",
    """CREATE TABLE IF NOT EXISTS ticket (ticket_id INT PRIMARY KEY,utente_id INT,ticket_codice VARCHAR(45))""",
    """CREATE TABLE IF NOT EXISTS ticket_uditore (ticket_id INT,utente_id INT,ticket_uditore_attivoSN INT,
       PRIMARY KEY(ticket_id,utente_id))""",
    """CREATE TABLE IF NOT EXISTS ticket_messaggio (ticket_messaggio_id INT AUTO_INCREMENT PRIMARY KEY,
       ticket_messaggio_data_creazione DATETIME,ticket_messagglio_testo TEXT,utente_id INT,
       utente_denomazione VARCHAR(255),ticket_id INT,ticket_messaggio_is_public INT)""",
]

NOTIFICHE = [
    """CREATE TABLE IF NOT EXISTS notifiche_parameters (
       notifica_parameter_id INT AUTO_INCREMENT PRIMARY KEY,
       notifica_parameter_operation VARCHAR(64), notifica_parameter_id_ref VARCHAR(64),
       notifica_parameter_message TEXT)""",
    """CREATE TABLE IF NOT EXISTS notifiche (
       notifica_id INT AUTO_INCREMENT PRIMARY KEY, notifica_title VARCHAR(255), notifica_body TEXT,
       notifica_created_by INT, notifica_created_at DATETIME, notifica_updated_by INT,
       notifica_updated_at DATETIME, notifica_parameter_id INT, notifica_letta INT, cliente_id INT)""",
]


def prepara(connessione):
    Messaggio.__table__.create(connessione, checkfirst=True)
    StatoMessaggio.__table__.create(connessione, checkfirst=True)
    for sql in TICKET + NOTIFICHE:
        connessione.execute(text(sql))


def svuota(connessione):
    archivi = {
        "messaggi",
        "messaggi_stati",
        "messaggio",
        "ticket",
        "ticket_uditore",
        "ticket_messaggio",
        "notifiche",
        "notifiche_parameters",
    }
    tabelle = connessione.execute(text("SHOW TABLES")).scalars().all()
    connessione.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    try:
        for nome in tabelle:
            if nome in archivi or nome.startswith(("realtime_", "chat_pratica_")):
                connessione.execute(text(f"DELETE FROM `{nome}`"))
    finally:
        connessione.execute(text("SET FOREIGN_KEY_CHECKS=1"))
