-- Eseguito una sola volta all'inizializzazione del container.
-- ersaf_test lo crea gia' MARIADB_DATABASE; qui si aggiunge il database di
-- sviluppo, cosi' `backend/.env` e la suite di test possono puntare allo
-- stesso server senza calpestarsi.
CREATE DATABASE IF NOT EXISTS `ersaf_dev`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Il carattere jolly copre anche i database usa-e-getta che la suite crea per
-- provare migrazioni e rollback senza toccare quello condiviso.
GRANT ALL PRIVILEGES ON `ersaf\_%`.* TO 'ersaf'@'%';
GRANT CREATE, DROP ON *.* TO 'ersaf'@'%';
FLUSH PRIVILEGES;
