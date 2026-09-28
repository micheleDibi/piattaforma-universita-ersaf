-- Rollback della migrazione 017. Non tocca pratica_numero delle pratiche
-- esistenti: quei valori sono dati applicativi, non un artefatto della
-- migrazione.
DROP TABLE IF EXISTS `pratiche_contatori`;
