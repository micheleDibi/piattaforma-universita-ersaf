---
---

## Novità e correzioni

- aggiunto: La scheda pratica mostra ora, in sola lettura, alcune caratteristiche del percorso formativo scelto: Modalità di erogazione, Facoltà, Durata, CFU, Tasse, Livello, Tipo di Laurea e Corso di Laurea. Quali compaiono dipende dal tipo di corso del percorso (Master, Corsi di perfezionamento, Formazione ed Alta formazione, Lauree, Corsi singoli); per gli altri tipi la sezione non compare.

## Dettagli tecnici

- modificato: `GET /listini-testa/{id}` restituisce anche `listino_modalita_descrizione`, `listino_facolta_descrizione`, `listino_durataLaurea_descrizione` e `listino_corsoLaurea_descrizione`, sullo stesso modello già usato per `nome_universita`/`listino_tipoCorso_descrizione`.
