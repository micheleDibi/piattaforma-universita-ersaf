"""DDL sintetica delle tabelle contabili toccate dopo la creazione di una pratica.

In produzione `articolo`, `documento` e i collegamenti stanno nello schema dei
pagamenti, `pratica_codice` nel principale. Nei test SCHEMA_GESTIONE_PAGAMENTI
e' `ersaf_test` (vedi conftest.py), quindi stanno tutte nello stesso database.
Colonne e tipi come nel database reale; le chiavi esterne verso tabelle
legacy restano fuori, come in archivi_realtime.py.
"""

from sqlalchemy import text

TABELLE = [
    """CREATE TABLE IF NOT EXISTS articolo_tipo (
       articolo_tipo_id INT AUTO_INCREMENT PRIMARY KEY,
       articolo_tipo_codice VARCHAR(45) NOT NULL, articolo_tipo_descrizione VARCHAR(255) NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS articolo_gruppo (
       articolo_gruppo_id INT AUTO_INCREMENT PRIMARY KEY,
       articolo_gruppo_codice VARCHAR(45) NOT NULL, articolo_gruppo_descrizione VARCHAR(255) NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS articolo (
       articolo_id INT AUTO_INCREMENT PRIMARY KEY,
       articolo_codice VARCHAR(45) NOT NULL, articolo_descrizione VARCHAR(255) NOT NULL,
       articolo_prezzo DECIMAL(20,8) NOT NULL DEFAULT 0,
       articolo_tipo_id INT NOT NULL, articolo_gruppo_id INT NOT NULL,
       articolo_createdBy INT NOT NULL, articolo_createdAt DATETIME,
       articolo_updatedBy INT NOT NULL, articolo_updatedAt DATETIME)""",
    """CREATE TABLE IF NOT EXISTS articolo_pratica (
       articolo_pratica_id INT AUTO_INCREMENT PRIMARY KEY,
       articolo_id INT NOT NULL, pratica_id INT NOT NULL,
       articolo_pratica_createdBy INT NOT NULL, articolo_pratica_createdAt DATETIME,
       articolo_pratica_updatedBy INT NOT NULL, articolo_pratica_updatedAt DATETIME)""",
    """CREATE TABLE IF NOT EXISTS documento (
       documento_id INT AUTO_INCREMENT PRIMARY KEY,
       documento_codice VARCHAR(45) NOT NULL, documento_totale DECIMAL(20,8) NOT NULL DEFAULT 0,
       cliente_id INT NOT NULL, fornitore_id INT NOT NULL,
       documento_createdBy INT NOT NULL, documento_createdAt DATETIME,
       documento_updatedBy INT NOT NULL, documento_updatedAt DATETIME,
       documento_data_creazione DATE NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS documento_articolo (
       doc_articolo_id INT AUTO_INCREMENT PRIMARY KEY,
       documento_id INT NOT NULL, articolo_id INT NOT NULL,
       doc_articolo_createdBy INT NOT NULL, doc_articolo_createdAt DATETIME,
       doc_articolo_updatedBy INT NOT NULL, doc_articolo_updatedAt DATETIME)""",
    """CREATE TABLE IF NOT EXISTS pratica_codice (
       pratica_codice_id INT AUTO_INCREMENT PRIMARY KEY, pratica_id INT NOT NULL,
       pratica_codice_temporanreo VARCHAR(45) NOT NULL, pratica_codice_permanente VARCHAR(45),
       pratica_codice_created_by INT NOT NULL, pratica_codice_created_at DATETIME,
       pratica_codice_updated_by INT NOT NULL, pratica_codice_updated_at DATETIME,
       pratica_codice_assigned_by INT, pratica_codice_assigned_at DATETIME)""",
]

# I gruppi reali: il 2 si chiama "ALTA FORMAZIONE" e non ne esiste uno per
# Master area scuola, Master classi di concorso o Corsi di formazione.
GRUPPI = [
    "PRATICA CORSI DI PERFEZIONAMENTO", "PRATICA CORSI DI ALTA FORMAZIONE", "PRATICA MASTER",
    "PRATICA CORSI SINGOLI", "PRATICA LAUREE", "PRATICA CORSI SPECIALI",
]

# Figlio -> padre, per lo svuotamento.
DA_SVUOTARE = ["documento_articolo", "articolo_pratica", "documento", "articolo", "pratica_codice"]


def prepara(connessione):
    for sql in TABELLE:
        connessione.execute(text(sql))
    connessione.execute(text("DELETE FROM articolo_gruppo"))
    connessione.execute(text("DELETE FROM articolo_tipo"))
    connessione.execute(text(
        "INSERT INTO articolo_tipo (articolo_tipo_codice, articolo_tipo_descrizione) "
        "VALUES ('PRATICA', 'Articolo Pratica')"
    ))
    for codice in GRUPPI:
        connessione.execute(text(
            "INSERT INTO articolo_gruppo (articolo_gruppo_codice, articolo_gruppo_descrizione) "
            "VALUES (:codice, :codice)"
        ), {"codice": codice})


def svuota(connessione):
    for tabella in DA_SVUOTARE:
        connessione.execute(text(f"DELETE FROM `{tabella}`"))
