---
---

## Novità e correzioni

- modificato: Negli elenchi Sottoscrittori e Attuatori nome e cognome sono in un'unica colonna
  Nominativo («Cognome Nome»), con le iniziali in un cerchio e il segnale di avviso subito accanto.
- modificato: Le verifiche di email, cellulare e diploma sono etichette con il loro nome, verdi con
  la spunta quando sono a posto; la legenda sopra l'elenco non serve più ed è stata tolta.
- aggiunto: Accanto al titolo degli elenchi Sottoscrittori e Attuatori compare il numero di
  risultati, che segue ricerca e filtri.
- modificato: La finestra degli avvisi di un'anagrafica ha come titolo il numero di errori.

## Dettagli tecnici

- aggiunto: `GET /clienti/conteggio` restituisce `{"totale": n}` con gli stessi filtri e la stessa
  visibilità di `GET /clienti/`, senza paginazione.
- modificato: I filtri di `GET /clienti/` sono in `_filtra_elenco`, condivisa con il conteggio.
