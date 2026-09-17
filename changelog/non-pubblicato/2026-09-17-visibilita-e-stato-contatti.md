---
pr: 4
---

## Novità e correzioni

- aggiunto: Negli elenchi Sottoscrittori e Attuatori una colonna Stato mostra con dei pallini se
  l'email e il cellulare sono stati verificati e, per i sottoscrittori, se il diploma è completo.
  Sopra l'elenco c'è la legenda che spiega i pallini.
- corretto: Nella sezione dei titoli di studio l'anno di conseguimento si scrive come anno
  scolastico. Prima i due campi chiedevano una data e salvavano nel posto sbagliato.
- sicurezza: Chi non è Nazionale non può più assegnare il ruolo Nazionale, nemmeno a se stesso, e
  non può più cambiare il proprio ruolo.
- modificato: Chi vede quali sottoscrittori, quali aziende e quali pratiche segue adesso la stessa
  regola in tutta la piattaforma.

## Dettagli tecnici

- aggiunto: `backend/src/auth/visibilita.py` è l'unico punto che contiene la regola di visibilità,
  per clienti, aziende e pratiche; i router la chiamano invece di riscriverla. La CTE ricorsiva
  segnala il superamento di `max_recursive_iterations` invece di restituire in silenzio un
  risultato parziale.
- aggiunto: migrazione `016_indici_visibilita_clienti` con gli indici che sostengono i filtri di
  visibilità, e il suo rollback.
- aggiunto: `diploma_completo` sugli elenchi e sulla scheda dei clienti, calcolato con una
  `selectinload` del curriculum: nessuna query per riga. La regola dei campi del diploma sta in
  `universita/models.py` e vale sia per l'elenco sia per la scheda.
- sicurezza: `verifica_ruolo_assegnabile` chiude l'innalzamento di privilegi che si otteneva
  scrivendo sulla propria riga `clienti`, sempre visibile, o creando un Nazionale con con-utente.
- modificato: `universita_anno_scolastico` e `universita_anno_scolastico_ai` sono campi di testo da
  45 caratteri, come lo schema. Nessuna migrazione dei dati.
- modificato: le liste dei campi azienda stanno in `frontend/src/config/campiAzienda.js`, così un
  file di componente esporta solo componenti e il fast refresh di Vite non ricarica la pagina.
