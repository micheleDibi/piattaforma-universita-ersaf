-- =============================================================================
-- SCHEMA BASE PER IL DATABASE DI TEST
-- =============================================================================
--
--   ⚠️  NON ESEGUIRE QUESTO FILE SU UN DATABASE CON DEI DATI.  ⚠️
--
--   Fa DROP TABLE su utenti, clienti, aziende, ruoli e messaggi_email.
--   Serve a costruire da zero il database usa-e-getta della suite di test.
--   Non e' una migrazione e non va mai eseguito su admin_entedb ne' su una
--   copia di lavoro che contenga dati veri.
--
-- =============================================================================
-- Le migrazioni 001-006 presuppongono che `utenti`, `clienti`, `ruoli`,
-- `aziende` e `messaggi_email` esistano gia': fanno parte delle 171 tabelle
-- ereditate dalla piattaforma Instant Developer e non sono gestite da alcuna
-- migrazione. Questo file le ricrea su un database vuoto, cosi' la suite di
-- test puo' applicare le 001-006 esattamente come si farebbe in produzione.
--
-- COSA C'E' QUI DENTRO
--   Solo DDL — nomi di colonna e tipi — piu' le sette righe di `ruoli`, che
--   sono dati di lookup pubblici e senza i quali nessun join funziona.
--   NESSUN dato personale. `dump.sql` non e' e non deve diventare la sorgente
--   dei dati di test: contiene password in chiaro, codici fiscali, numeri di
--   documento e date di nascita di ~3.900 persone.
--
--   La DDL e' quella reale, riprodotta fedelmente. In produzione la sorgente
--   canonica e' `SHOW CREATE TABLE`, ed e' quella da usare per riallinearla.
--
-- FEDELTA' CHE CONTA
--   Le differenze rispetto ai modelli SQLAlchemy sono deliberate: qui c'e' il
--   database reale, non quello che i modelli dichiarano.
--     * `utenti.utente_username` NON ha UNIQUE (in produzione ci sono 6
--       duplicati, incluso il valore '/'), malgrado il modello lo dichiari;
--     * `utenti.utente_password` e' NOT NULL: "svuotare il chiaro" significa
--       scrivere '', mai NULL;
--     * `clienti` ha SOLO la PRIMARY KEY: nessun indice su cliente_email,
--       utente_id o cliente_ruolo. Li aggiunge la migrazione 005;
--     * `clienti` non ha nessuna FOREIGN KEY, malgrado il modello ne dichiari
--       tre;
--     * `clienti.cliente_codice_fiscale` esiste nel database ma non nel
--       modello;
--     * `messaggi_email.messaggio_email_codice` non ha UNIQUE: la aggiunge la
--       migrazione 006.
--
-- Uso:  mariadb -u <user> -p <db_di_test> < db/test/schema_base.sql
-- =============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `password_reset_token`;
DROP TABLE IF EXISTS `password_reset_richiesta`;
DROP TABLE IF EXISTS `auth_sessione`;
DROP TABLE IF EXISTS `clienti`;
DROP TABLE IF EXISTS `utenti`;
DROP TABLE IF EXISTS `aziende`;
DROP TABLE IF EXISTS `ruoli`;
DROP TABLE IF EXISTS `messaggi_email`;

-- -----------------------------------------------------------------------------
CREATE TABLE `ruoli` (
  `ruolo_id` int(11) NOT NULL AUTO_INCREMENT,
  `ruolo_codice` varchar(45) NOT NULL DEFAULT '',
  `ruolo_descrizione` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`ruolo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dati di lookup, non personali. "Attuatore" non e' un valore in tabella: e'
-- l'insieme {1,2,3,5}, lo stesso che il filtro solo_attuatori di
-- src/clienti/routers.py gia' seleziona.
--
-- NO_AUTO_VALUE_ON_ZERO e' indispensabile: su una colonna AUTO_INCREMENT il
-- valore 0 verrebbe altrimenti sostituito dal successivo della sequenza, e la
-- riga del ruolo 0 (Utente) finirebbe con ruolo_id = 1 collidendo con
-- Aderente. Il ruolo 0 esiste davvero in produzione ed e' quello dei
-- sottoscrittori: senza, il test di `ruolo_non_abilitato` proverebbe la cosa
-- sbagliata.
SET @sql_mode_precedente = @@SESSION.sql_mode;
SET SESSION sql_mode = CONCAT(@@SESSION.sql_mode, ',NO_AUTO_VALUE_ON_ZERO');

INSERT INTO `ruoli` (`ruolo_id`, `ruolo_codice`, `ruolo_descrizione`) VALUES
  (0, 'Utente',      'Utente generico'),
  (1, 'Aderente',    'Attuatore aderente'),
  (2, 'Regionale',   'Attuatore regionale'),
  (3, 'Provinciale', 'Attuatore provinciale'),
  (4, 'Consulente',  'Consulente'),
  (5, 'Nazionale',   'Attuatore nazionale'),
  (6, 'Operatore',   'Operatore');

SET SESSION sql_mode = @sql_mode_precedente;

-- -----------------------------------------------------------------------------
CREATE TABLE `aziende` (
  `azienda_id` int(11) NOT NULL AUTO_INCREMENT,
  `azienda_ragione_sociale` varchar(255) NOT NULL,
  `azienda_partitaIVA` varchar(255) NOT NULL,
  `azienda_codiceFiscale` varchar(255) DEFAULT NULL,
  `azienda_fatturazioneSDI` varchar(255) DEFAULT NULL,
  `azienda_via` varchar(255) NOT NULL,
  `azienda_civico` varchar(255) DEFAULT NULL,
  `azienda_citta` varchar(255) NOT NULL,
  `azienda_CAP` varchar(45) NOT NULL,
  `azienda_provincia` varchar(45) NOT NULL,
  `azienda_sitoWeb` varchar(255) DEFAULT NULL,
  `azienda_email` varchar(255) DEFAULT NULL,
  `azienda_telefono` varchar(45) DEFAULT NULL,
  `azienda_pec` varchar(255) DEFAULT NULL,
  `azienda_logo` longblob DEFAULT NULL,
  `azienda_codice_nazionale` varchar(45) DEFAULT NULL,
  `azienda_iban` varchar(255) DEFAULT NULL,
  `azienda_codice_bic` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`azienda_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- NOTA: nessuna UNIQUE su utente_username. E' cosi' anche in produzione.
CREATE TABLE `utenti` (
  `utente_id` int(11) NOT NULL AUTO_INCREMENT,
  `utente_username` varchar(255) NOT NULL,
  `utente_password` varchar(255) NOT NULL,
  `utente_ultimo_login` date DEFAULT NULL,
  `utente_ultimo_logout` date DEFAULT NULL,
  `utente_padre` int(11) DEFAULT NULL,
  `utente_attivoSN` int(11) DEFAULT -1,
  `utente_created_by` int(11) DEFAULT NULL,
  `utente_created_at` date DEFAULT NULL,
  `utente_updated_by` int(11) DEFAULT NULL,
  `utente_updated_at` datetime DEFAULT NULL,
  `utente_salt` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`utente_id`),
  KEY `FK_utenti_utente_created_by` (`utente_created_by`),
  KEY `FK_utenti_utente_updated_by` (`utente_updated_by`),
  CONSTRAINT `FK_utenti_utente_created_by` FOREIGN KEY (`utente_created_by`)
    REFERENCES `utenti` (`utente_id`),
  CONSTRAINT `FK_utenti_utente_updated_by` FOREIGN KEY (`utente_updated_by`)
    REFERENCES `utenti` (`utente_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- NOTA: SOLO la PRIMARY KEY, nessun indice e nessuna FOREIGN KEY. E' cosi'
-- anche in produzione: gli indici arrivano con la migrazione 005.
CREATE TABLE `clienti` (
  `cliente_id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_codice` varchar(20) NOT NULL DEFAULT '',
  `cliente_codice_fiscale` varchar(20) DEFAULT NULL,
  `cliente_nome` varchar(255) NOT NULL DEFAULT '',
  `cliente_cognome` varchar(255) NOT NULL DEFAULT '',
  `cliente_email` varchar(255) NOT NULL DEFAULT '',
  `cliente_telefono` varchar(255) NOT NULL DEFAULT '',
  `cliente_pec` varchar(255) DEFAULT NULL,
  `cliente_indirizzo` varchar(255) NOT NULL DEFAULT '',
  `cliente_civico` varchar(45) NOT NULL DEFAULT '',
  `cliente_citta` varchar(255) NOT NULL DEFAULT '',
  `cliente_CAP` varchar(10) NOT NULL DEFAULT '',
  `cliente_provincia` varchar(45) NOT NULL DEFAULT '',
  `cliente_cellulare` varchar(45) DEFAULT NULL,
  `utente_id` int(11) NOT NULL DEFAULT 1,
  `cliente_luogoNascita` varchar(255) NOT NULL DEFAULT '',
  `cliente_provinciaNascita` varchar(45) NOT NULL DEFAULT '',
  `cliente_dataNascita` date NOT NULL DEFAULT '1999-12-31',
  `cliente_cittadinanza` varchar(255) NOT NULL DEFAULT '',
  `cliente_tipoDocumento` varchar(255) NOT NULL DEFAULT '',
  `cliente_documento` varchar(45) NOT NULL DEFAULT '',
  `cliente_comuneRilascio` varchar(255) NOT NULL DEFAULT '',
  `cliente_dataRilascio` date NOT NULL DEFAULT '1999-12-31',
  `cliente_dataScadenzaDocumento` date NOT NULL DEFAULT '1999-12-31',
  `cliente_sesso` varchar(45) NOT NULL DEFAULT '',
  `cliente_indirizzoDomicilio` varchar(255) DEFAULT NULL,
  `cliente_civicoDomicilio` varchar(45) DEFAULT NULL,
  `cliente_cittaDomicilio` varchar(255) DEFAULT NULL,
  `cliente_CAPDomicilio` varchar(45) DEFAULT NULL,
  `cliente_provinciaDomicilio` varchar(45) DEFAULT NULL,
  `cliente_ruolo` int(11) NOT NULL DEFAULT 0,
  `cliente_gg` int(11) DEFAULT NULL,
  `attuatore_id` int(11) DEFAULT NULL,
  `azienda_id` int(11) DEFAULT NULL,
  `tessera_id` int(11) DEFAULT NULL,
  `cliente_abilPraticheUniv` int(11) NOT NULL DEFAULT 0,
  `cliente_pathCertificato` varchar(255) DEFAULT NULL,
  `cliente_abilitazione_ecampus` int(11) NOT NULL DEFAULT 0,
  `cliente_abilitazione_link_campus` int(11) NOT NULL DEFAULT 0,
  `cliente_abilitazione_corsi_speciali` int(11) NOT NULL DEFAULT -1,
  `cliente_abilitazione_a4u` int(11) NOT NULL DEFAULT -1,
  PRIMARY KEY (`cliente_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- NOTA: nessuna UNIQUE su messaggio_email_codice. La aggiunge la 006.
-- Nessuna riga: i due template password_reset_* devono arrivare dalla
-- migrazione 006, che e' esattamente cio' che si vuole verificare.
CREATE TABLE `messaggi_email` (
  `messaggio_email_id` int(11) NOT NULL AUTO_INCREMENT,
  `messaggio_email_codice` varchar(45) NOT NULL DEFAULT '',
  `messaggio_email_testo` longtext DEFAULT NULL,
  `messaggio_email_oggetto` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`messaggio_email_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
