---
---

## Novità e correzioni

- modificato: Per il Nazionale la pagina Pratiche non mostra più il pannello degli atenei ma un unico elenco
  con tutte le pratiche tranne le Bozze, ordinate per stato (Caricata, In lavorazione, In attesa di modifica,
  Conclusa, Rifiutata) e, dentro ogni stato, dalla modifica più recente. Senza ricerca né filtri l'elenco ha
  in testa "Tutte le pratiche" con il totale; con la ricerca o un filtro si divide in un gruppo per stato, con
  il numero di pratiche accanto a ogni stato.
- aggiunto: Nell'elenco del Nazionale ci sono le colonne Ultima modifica, Tipo corso e Università (al posto
  della data di creazione), la ricerca per sottoscrittore e i filtri Codice pratica e Stato.
- aggiunto: Nell'elenco del Nazionale, sotto il titolo, i loghi dei quattro atenei filtrano le pratiche per
  ateneo; scorrendo restano in alto, più piccoli, accanto al titolo.
- modificato: In fondo a tutti gli elenchi la scritta "Hai raggiunto la fine dell'elenco", il caricamento e il
  pulsante "Carica altri elementi" sono centrati e staccati dall'ultima riga.
- rimosso: Il Nazionale non ha più il pulsante "Nuova" nelle pratiche: le gestisce, non le crea.
- aggiunto: Nella scheda di una pratica eCampus il Nazionale vede e modifica il Codice ASG; gli altri ruoli
  non lo vedono.

## Dettagli tecnici

- aggiunto: `GET /pratiche/` accetta `escludi_bozze` e `ordine=stato` (gruppi Caricata, In lavorazione,
  In attesa di modifica, Conclusa, Rifiutata, poi `COALESCE(pratica_updated_at, pratica_created_at,
  pratica_dataCreazione)` decrescente): l'ordine sta nella query, quindi la paginazione non spezza i gruppi.
- aggiunto: `GET /pratiche/conteggi/stati`, il numero di pratiche per stato con gli stessi filtri dell'elenco.
- sicurezza: `pratica_codiceASG` esce nelle risposte delle pratiche solo per il Nazionale (`null` per gli altri
  ruoli); `PUT /pratiche/{id}` lo accetta solo dal Nazionale e solo su pratiche eCampus
  (`nome_universita_id` 1), e lo ignora in silenzio negli altri casi; `POST /pratiche/` lo ignora sempre.
- aggiunto: `ElencoPraticheNazionale.jsx` e `useFiltriPraticheNazionale.js`; `SchedaPratica.jsx` riporta il
  Nazionale all'elenco da `/pratiche/nuova`.
- aggiunto: `ConRuoloVerificato.jsx` e `ricaricaSessione` in `lib/api.js`: elenco e scheda pratica rileggono
  il ruolo da `GET /auth/session` prima di scegliere la vista, perché quello in memoria resta quello
  dell'accesso anche se il ruolo cambia dopo.
