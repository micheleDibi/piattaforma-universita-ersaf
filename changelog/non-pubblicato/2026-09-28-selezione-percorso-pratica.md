---
---

## Novità e correzioni

- aggiunto: La scelta del percorso formativo in una pratica nuova ora apre una finestra larga con l'elenco dei percorsi (Codice, Denominazione, Prezzo, CFU), filtrato per l'ateneo e il tipo di corso da cui si è aperta la scheda, con solo i percorsi attivi e con un listino in corso.
- aggiunto: Per le pratiche di tipo Corsi Singoli si possono scegliere più corsi: il prezzo della pratica è la somma dei prezzi correnti dei corsi scelti, e si aggiorna man mano che se ne aggiungono o tolgono. Una volta salvata la pratica l'elenco dei corsi resta fisso.

## Dettagli tecnici

- modificato: `GET /listini-testa/` accetta `nome_universita_id`, `listino_tipo_corso_id` (uno o più) e `valido_oggi`, oltre ai filtri testuali già esistenti (usati dall'Elenco Prodotti Formativi); restituisce anche `dettagli` nell'elenco, non solo nel dettaglio per id.
- aggiunto: `POST /pratiche/` accetta `corsi_singoli` (lista di `{listTesta_id, prezzo}`): per ogni voce crea una riga in `pratiche_listini`, nella stessa transazione dell'inserimento della pratica. Il primo elemento resta anche in `listTesta_id`, come per ogni altra pratica.
- rimosso: Il componente di selezione a ricerca libera (`SelezioneRicercabile.jsx`) e il suo foglio di stile: non aveva più altri usi dopo questa modifica.
