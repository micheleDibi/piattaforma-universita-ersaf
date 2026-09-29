-- 018 - Metadati del servizio realtime completo; nessun rollback distruttivo.

CREATE TABLE IF NOT EXISTS realtime_auth_session (
    -- I DATETIME(6) di questa tabella sono codificati esplicitamente in UTC.
    session_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    utente_id INT NOT NULL,
    cliente_id INT NOT NULL,
    azienda_id INT NOT NULL DEFAULT 0,
    ruolo_codice VARCHAR(45) NOT NULL,
    device_id VARCHAR(128) NOT NULL,
    refresh_token_hash BINARY(32) NOT NULL,
    refresh_generation INT UNSIGNED NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    refresh_expires_at DATETIME(6) NOT NULL,
    last_used_at DATETIME(6) NOT NULL,
    revoked_at DATETIME(6) NULL,
    revocation_reason VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NULL,
    PRIMARY KEY (session_id),
    UNIQUE KEY uq_realtime_auth_refresh_hash (refresh_token_hash),
    KEY ix_realtime_auth_user (utente_id),
    KEY ix_realtime_auth_expiry (refresh_expires_at),
    KEY ix_realtime_auth_revoked (revoked_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_person_contact_acl (
    utente_low_id INT NOT NULL,
    utente_high_id INT NOT NULL,
    source VARCHAR(45) NOT NULL,
    granted_at DATETIME(6) NOT NULL,
    revoked_at DATETIME(6) NULL,
    PRIMARY KEY (utente_low_id, utente_high_id),
    KEY ix_realtime_person_acl_high (utente_high_id),
    KEY ix_realtime_person_acl_revoked (revoked_at),
    CONSTRAINT ck_realtime_person_acl_order
        CHECK (utente_low_id > 0 AND utente_low_id < utente_high_id),
    CONSTRAINT fk_realtime_person_acl_low
        FOREIGN KEY (utente_low_id) REFERENCES utenti (utente_id) ON DELETE CASCADE,
    CONSTRAINT fk_realtime_person_acl_high
        FOREIGN KEY (utente_high_id) REFERENCES utenti (utente_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_person_conversation (
    utente_low_id INT NOT NULL,
    utente_high_id INT NOT NULL,
    document_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (utente_low_id, utente_high_id),
    UNIQUE KEY uq_realtime_person_document (document_id),
    CONSTRAINT ck_realtime_person_conversation_order
        CHECK (utente_low_id > 0 AND utente_low_id < utente_high_id),
    CONSTRAINT fk_realtime_person_conversation_acl
        FOREIGN KEY (utente_low_id, utente_high_id)
        REFERENCES realtime_person_contact_acl
            (utente_low_id, utente_high_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_message_command (
    sender_user_id INT NOT NULL,
    client_message_id VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    request_hash BINARY(32) NOT NULL,
    destination_type VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    legacy_message_id BIGINT NULL,
    canonical_payload LONGTEXT NULL,
    created_at DATETIME(6) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    PRIMARY KEY (sender_user_id, client_message_id),
    KEY ix_realtime_message_command_expiry (expires_at),
    CONSTRAINT ck_realtime_message_command_payload CHECK (JSON_VALID(canonical_payload))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_notification_command (
    producer_event_id VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    request_hash BINARY(32) NOT NULL,
    recipient_user_id INT NOT NULL,
    legacy_notification_id BIGINT NULL,
    legacy_parameter_id BIGINT NULL,
    canonical_payload LONGTEXT NULL,
    created_at DATETIME(6) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    PRIMARY KEY (producer_event_id),
    KEY ix_realtime_notification_command_expiry (expires_at),
    CONSTRAINT ck_realtime_notification_command_payload CHECK (JSON_VALID(canonical_payload))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_auth_refresh_history (
    token_hash BINARY(32) NOT NULL,
    session_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    consumed_at DATETIME(6) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    PRIMARY KEY (token_hash),
    KEY ix_realtime_refresh_history_session (session_id),
    KEY ix_realtime_refresh_history_expiry (expires_at, token_hash),
    CONSTRAINT fk_realtime_refresh_history_session
        FOREIGN KEY (session_id)
        REFERENCES realtime_auth_session (session_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_notification_bridge (
    notification_id INT NOT NULL,
    bridged_at DATETIME(6) NOT NULL,
    bridge_status VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    error_code VARCHAR(64) CHARACTER SET ascii COLLATE ascii_bin NULL,
    PRIMARY KEY (notification_id),
    CONSTRAINT ck_realtime_notification_bridge_status CHECK (
        (bridge_status = 'DELIVERED' AND error_code IS NULL)
        OR (bridge_status = 'REJECTED' AND error_code IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_notification_bridge_state (
    singleton_id TINYINT UNSIGNED NOT NULL,
    baseline_id INT NOT NULL,
    scan_floor_id INT NOT NULL,
    initialized TINYINT(1) NOT NULL DEFAULT 0,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (singleton_id),
    CONSTRAINT ck_realtime_notification_bridge_singleton CHECK (singleton_id = 1),
    CONSTRAINT ck_realtime_notification_bridge_state
        CHECK (baseline_id >= 0 AND scan_floor_id >= baseline_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_notification_seen (
    utente_id INT NOT NULL,
    notification_id INT NOT NULL,
    seen_at DATETIME(6) NOT NULL,
    PRIMARY KEY (utente_id, notification_id),
    CONSTRAINT fk_realtime_seen_user FOREIGN KEY (utente_id)
        REFERENCES utenti(utente_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_notification_seen_snapshot (
    snapshot_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    utente_id INT NOT NULL,
    cliente_id INT NOT NULL,
    notification_ids MEDIUMTEXT NOT NULL CHECK (JSON_VALID(notification_ids)),
    created_at DATETIME(6) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    applied_at DATETIME(6) NULL,
    PRIMARY KEY (snapshot_id),
    KEY ix_realtime_seen_snapshot_user (utente_id, expires_at),
    CONSTRAINT fk_realtime_seen_snapshot_user FOREIGN KEY (utente_id)
        REFERENCES utenti(utente_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

CREATE TABLE IF NOT EXISTS realtime_message_seen_snapshot (
    snapshot_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    utente_id INT NOT NULL,
    cliente_id INT NOT NULL,
    item_ids MEDIUMTEXT NOT NULL CHECK (JSON_VALID(item_ids)),
    created_at DATETIME(6) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    applied_at DATETIME(6) NULL,
    PRIMARY KEY (snapshot_id),
    KEY ix_realtime_message_snapshot_user (utente_id, expires_at),
    CONSTRAINT fk_realtime_message_snapshot_user FOREIGN KEY (utente_id)
        REFERENCES utenti(utente_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

ALTER TABLE realtime_auth_session
    ADD COLUMN IF NOT EXISTS refresh_generation INT UNSIGNED NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS revocation_reason VARCHAR(16) CHARACTER SET ascii COLLATE ascii_bin NULL;

CREATE TABLE IF NOT EXISTS realtime_presenza (
    connessione CHAR(36) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
    session_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    utente_id INT NOT NULL,
    scadenza DATETIME(6) NOT NULL,
    KEY ix_presenza_utente (utente_id,scadenza),
    KEY ix_presenza_scadenza (scadenza)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_evento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    utente_id INT NOT NULL,
    payload LONGTEXT NOT NULL CHECK (JSON_VALID(payload)),
    scadenza DATETIME(6) NOT NULL,
    KEY ix_evento_destinatario (utente_id,id),
    KEY ix_evento_scadenza (scadenza)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_flusso_utente (
    utente_id INT PRIMARY KEY,
    revisione BIGINT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_limite (
    chiave BINARY(32) PRIMARY KEY,
    finestra BIGINT NOT NULL,
    conteggio INT NOT NULL,
    scadenza DATETIME(6) NOT NULL
) ENGINE=InnoDB;
