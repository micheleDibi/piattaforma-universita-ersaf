-- Rollback della migrazione 022. Le righe con un prefisso oltre i 10 caratteri
-- non entrerebbero piu' nella colonna: si eliminano. Non si perde nulla, perche'
-- quei contatori si riallineano da soli al massimo degli articoli e dei
-- partitari esistenti al primo uso (vedi backend/src/pratiche/dopo_salvataggio.py).
DELETE FROM `pratiche_contatori` WHERE CHAR_LENGTH(`prefisso`) > 10;

ALTER TABLE `pratiche_contatori`
  MODIFY COLUMN `prefisso` varchar(10) NOT NULL;
