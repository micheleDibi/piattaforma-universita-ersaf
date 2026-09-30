-- 017 - Chat pratiche nativa con archivio e metadati condivisi con Universo
-- Nessun DROP nel rollback: le tabelle condivise possono essere preesistenti.
CREATE TABLE IF NOT EXISTS realtime_message_state (
    utente_id INT NOT NULL,
    item_id BIGINT NOT NULL,
    seen_at DATETIME(6) NULL,
    read_at DATETIME(6) NULL,
    PRIMARY KEY (utente_id, item_id),
    CONSTRAINT ck_realtime_message_item CHECK (item_id > 0 AND MOD(item_id,4) < 3),
    CONSTRAINT fk_realtime_message_state_user FOREIGN KEY (utente_id)
        REFERENCES utenti(utente_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_message_key_grant (
    utente_id INT NOT NULL,
    canonical_context VARCHAR(128) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    key_version TINYINT UNSIGNED NOT NULL,
    epoch_hour INT UNSIGNED NOT NULL,
    granted_at DATETIME(6) NOT NULL,
    PRIMARY KEY (utente_id, canonical_context, key_version, epoch_hour),
    KEY ix_realtime_message_key_grant_epoch (epoch_hour)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_message_time (
    destination_type VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    message_id INT NOT NULL,
    sent_at_utc DATETIME(6) NOT NULL,
    PRIMARY KEY (destination_type, message_id)
) ENGINE=InnoDB;

-- Una chiave per mittente/pratica; il retry restituisce lo stesso messaggio.
CREATE TABLE IF NOT EXISTS chat_pratica_comando (
    utente_id INT NOT NULL,
    pratica_id INT NOT NULL,
    client_id VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    impronta BINARY(32) NOT NULL,
    messaggio_id INT NOT NULL,
    creato_il DATETIME(6) NOT NULL,
    PRIMARY KEY (utente_id, pratica_id, client_id),
    UNIQUE KEY uq_chat_pratica_messaggio (messaggio_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chat_pratica_limite (
    utente_id INT PRIMARY KEY,
    finestra BIGINT NOT NULL,
    tentativi INT NOT NULL
) ENGINE=InnoDB;

-- Coda interoperabile: Universo può consumarla durante il passaggio al nuovo WS.
CREATE TABLE IF NOT EXISTS realtime_delivery (
    delivery_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    recipient_user_id INT NOT NULL,
    channel VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    payload_json LONGTEXT NOT NULL CHECK (JSON_VALID(payload_json)),
    created_at DATETIME(6) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    acknowledged_at DATETIME(6) NULL,
    attempt_count INT NOT NULL DEFAULT 0,
    last_attempt_at DATETIME(6) NULL,
    next_attempt_at DATETIME(6) NOT NULL,
    PRIMARY KEY (delivery_id),
    KEY ix_realtime_delivery_due_v2
      (recipient_user_id, acknowledged_at, next_attempt_at, created_at, delivery_id),
    KEY ix_realtime_delivery_expiry (expires_at)
) ENGINE=InnoDB;
