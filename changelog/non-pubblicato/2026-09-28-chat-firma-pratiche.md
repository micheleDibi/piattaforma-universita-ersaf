---
---

## Novità e correzioni

- aggiunto: Nella scheda della pratica si può consultare e utilizzare la conversazione condivisa con Universo, quando il collegamento è configurato.
- aggiunto: La firma della pratica si può disegnare con mouse, dito o penna e usare nei documenti generati successivamente.
- sicurezza: Il salvataggio avvisa se la firma è stata modificata nel frattempo da un'altra finestra.

## Dettagli tecnici

- aggiunto: Ponte FastAPI verso le API e il WebSocket Java esistenti, con sessione interna breve e controllo dei partecipanti alla pratica.
- aggiunto: Configurazione facoltativa CHAT_JAVA_URL, CHAT_JAVA_ORIGINE, CHAT_JAVA_SECRET_FILE e CHAT_DATASET; attivazione subordinata alla pubblicazione del delta Java e alla configurazione della rete privata.
- aggiunto: API dedicate per firma PNG con CSRF e versione ottimistica; riutilizzato il campo pratica_firma senza nuove migrazioni.
- modificato: Nginx e proxy di sviluppo inoltrano l'upgrade WebSocket; il container API limita dimensione e coda dei frame.
- modificato: Indici della documentazione e specifiche storiche riordinati; chiarito il riuso del ramo personale e il ciclo di vita dei checkout temporanei.
