# Glossario

Definizioni brevi dei termini usati nella piattaforma e nella sua documentazione, in ordine alfabetico.

## Abilitazioni alle pratiche

Interruttori personali che decidono quali righe della pagina Pratiche si aprono: uno generale per le pratiche universitarie e uno per ogni ateneo. Il Nazionale li cambia nella scheda "Abilitazioni" di un attuatore. Vedi [Ruoli e permessi](ruoli-e-permessi.md).

## Accesso come altro utente

Detto anche impersonificazione. Permette a un Regionale o a un Nazionale di entrare con l'identità di un altro attuatore attivo, senza conoscerne la password. Non vale mai verso un Nazionale. La sessione di chi lo usa termina. Vedi [Ruoli e permessi](ruoli-e-permessi.md).

## Aderente

Ruolo da attuatore, con accesso alla piattaforma. È il ruolo proposto per un nuovo attuatore. Nella scheda della pratica compare come "aderente emittente".

## App di autenticazione

App del telefono, per esempio Google Authenticator o Microsoft Authenticator, che mostra un codice di 6 cifre che cambia ogni 30 secondi, anche senza rete. È uno dei metodi del secondo fattore.

## Attuatore

Persona che opera nella rete con ruolo Aderente, Provinciale, Regionale, Nazionale od Operatore. Con i primi quattro ruoli accede alla piattaforma e può recuperare la password; l'Operatore compare fra gli attuatori ma non accede. Può essere associata a un'azienda. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

## Azienda padre e azienda figlia

Nella gerarchia delle aziende, l'azienda padre sta sopra l'azienda figlia. Un'azienda senza padre è una radice. Solo il Nazionale cambia l'azienda padre. Vedi [Aziende](aziende.md).

## Collaudo

Ambiente di prova in cui si pubblicano le nuove versioni per verificarle prima dell'uso reale. Chi pubblica e come è descritto in [Deploy](../tecnica/deploy.md).

## Curriculum formativo

Scheda della persona con il percorso di studi: titoli (istruzione secondaria o anno integrativo, titolo universitario, titoli post laurea), immatricolazioni ed iscrizioni, abilitazioni professionali e invalidità. Si salva insieme all'anagrafica. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

## Dashboard

Pagina con il messaggio di benvenuto. Il pannello delle pratiche, diviso per ateneo, sta nella pagina Pratiche. Vedi [Pratiche](pratiche.md).

## Frammento di changelog

Per chi contribuisce: breve testo che accompagna ogni modifica e che, alla pubblicazione, entra nel registro delle novità con il numero di versione. Vedi [Documentazione](../tecnica/documentazione.md).

## Gerarchia

Relazione padre e figlia fra aziende. Decide quali aziende vede chi non è Nazionale: la propria e tutte quelle che le stanno sotto. Fra le persone esiste anche l'utente padre, che oggi è solo un'informazione. Vedi [Ruoli e permessi](ruoli-e-permessi.md).

## Nazionale

Ruolo da attuatore con funzioni amministrative e la visibilità più ampia: vede tutte le voci di menu e tutte le aziende, cambia l'azienda padre e gestisce i propri metodi del secondo fattore, che per lui è obbligatorio.

## Passkey

Chiave conservata nel telefono, o in una chiave di sicurezza, che sostituisce il codice: all'accesso si conferma sul telefono con impronta, volto o PIN. È uno dei metodi del secondo fattore.

## Pratica

Richiesta di iscrizione a un percorso universitario. Collega uno studente, cioè un sottoscrittore, un aderente emittente, un percorso formativo e la sua università. Ha numero, anno accademico, sede di erogazione, prezzo, stato, data di creazione e note. Vedi [Pratiche](pratiche.md).

## Prodotto formativo

Voce del listino: un percorso dell'offerta formativa, con codice, università, tipo di corso, righe di prezzo con date di validità e stato "Attivo". Nella scheda della pratica si sceglie come "Percorso formativo". Vedi [Prodotti formativi](prodotti-formativi.md).

## Provinciale

Ruolo da attuatore, con accesso alla piattaforma e senza funzioni amministrative.

## Regionale

Ruolo da attuatore con funzioni amministrative: modifica gli altri utenti e può accedere come un altro utente, mai come un Nazionale.

## Secondo fattore

Conferma richiesta dopo la password, obbligatoria solo per il Nazionale. I metodi sono passkey sul telefono, app di autenticazione e codice via email. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

## Sessione

Periodo in cui la piattaforma ricorda chi è collegato. Con la configurazione predefinita scade dopo 14 giorni senza attività e comunque dopo 90 giorni. Termina anche con "Esci". Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

## Sottoscrittore

Persona con ruolo Utente o Consulente: compare nell'elenco Sottoscrittori. Solo chi ha il ruolo Utente si sceglie come studente nelle pratiche. Non accede alla piattaforma. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

## Stato della pratica

Indica a che punto è una pratica. Si sceglie da un elenco nella scheda della pratica. La piattaforma non impone un ordine fra gli stati e non registra lo storico dei cambi. Vedi [Pratiche](pratiche.md).

## Verifica dei contatti

Conferma che email e cellulare di una persona sono suoi, con un codice di 6 cifre inviato al contatto. Quando entrambi sono verificati, un account nuovo si attiva e riceve le credenziali via email. Se un contatto cambia, la sua verifica decade. Il flusso è descritto in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md). Per il Nazionale, l'email verificata abilita il codice via email come secondo fattore: vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

## Versione

Numero progressivo della pubblicazione, mostrato in fondo al menu con data e ora dell'aggiornamento. Dove l'applicazione non è stata pubblicata con la procedura di rilascio compare "Versione di sviluppo". Vedi [Panoramica](panoramica.md).
