-- Quorum ACK fra connessioni e worker. Solo metadati, nessuna modifica allo storico.
CREATE TABLE IF NOT EXISTS realtime_delivery_connessione (
    delivery_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    connessione CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    inviata_at DATETIME(6) NULL,
    confermata_at DATETIME(6) NULL,
    tentativi INT UNSIGNED NOT NULL DEFAULT 0,
    prossimo_at DATETIME(6) NOT NULL,
    PRIMARY KEY (delivery_id, connessione),
    KEY ix_delivery_connessione (connessione, prossimo_at),
    CONSTRAINT fk_delivery_connessione_outbox FOREIGN KEY (delivery_id)
        REFERENCES realtime_delivery (delivery_id) ON DELETE CASCADE
) ENGINE=InnoDB;
