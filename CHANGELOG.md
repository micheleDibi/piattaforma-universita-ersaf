# Registro delle modifiche

Le novità della Piattaforma Università, versione per versione, dalla più recente.

Una versione è una pubblicazione riuscita sul collaudo: numero, data e ora sono gli stessi che l'applicazione mostra in fondo al menu. Ogni versione ha due parti:

- **Novità e correzioni**: cosa cambia per chi usa la piattaforma.
- **Dettagli tecnici**: migrazioni del database, API cambiate, modifiche incompatibili, sicurezza.

Il file non si modifica a mano. Chi fa una modifica scrive un frammento in `changelog/non-pubblicato/` (formato ed esempi in [changelog/MODELLO.md](changelog/MODELLO.md)); alla pubblicazione il deploy raccoglie i frammenti e scrive qui la versione. Il meccanismo è descritto in [documentazione](docs/tecnica/documentazione.md) e in [deploy](docs/tecnica/deploy.md).

<!-- nuove-versioni: il timbro del deploy inserisce qui sotto le versioni pubblicate; non spostare questa riga -->

## Storico precedente alla documentazione (fino al 17/09/2026)

Riassunto delle modifiche arrivate su main fino al 17 settembre 2026, ricavato dai messaggi di commit. Le pubblicazioni di quel periodo non si possono ricostruire dal repository, quindi qui non hanno un numero di versione.

### Accesso e recupero password

- Accesso con nome utente e password; le pagine di accesso sono pagine normali e non più finestre.
- Recupero della password dimenticata: richiesta, email con il collegamento e pagina per scegliere la nuova password.
- Chi ha già una sessione aperta, aprendo la pagina di accesso, entra direttamente nell'applicazione.

### Sessione

- La sessione è gestita dal server e non più da un identificativo inviato dal browser.
- Corretto un errore per cui, dopo l'accesso, le operazioni fallivano dalla seconda in poi.
- La sessione resta attiva finché la si usa: scade dopo un periodo di inattività e comunque dopo un tetto massimo.

### Secondo fattore e verifica dei contatti

- Il ruolo Nazionale accede con un secondo fattore: codice via email, app di autenticazione o passkey.
- Nel profilo, la scheda Sicurezza permette al Nazionale di gestire app di autenticazione e passkey.
- Email e cellulare di un'anagrafica si verificano con un codice; a verifica completata l'account si attiva e le credenziali arrivano via email.

### Sottoscrittori, attuatori e utenti

- Elenchi di sottoscrittori e attuatori, con ricerca e filtro per ruolo.
- Creazione di anagrafica e utente in un solo passaggio, con controllo dei doppioni.
- Scheda dell'utente, curriculum formativo e scheda dell'azienda per gli attuatori.
- Gli amministratori regionali e nazionali possono accedere come un altro utente.
- Dettaglio utente, controlli sulla validità dei documenti e recupero delle verifiche dei contatti già effettuate.

### Aziende

- Elenco e scheda delle aziende.
- Gerarchia delle aziende, che stabilisce chi vede quali aziende; il Nazionale può cambiare l'azienda padre, con richiesta di conferma quando alcune percentuali vanno azzerate.
- Nuovi controlli e avvisi nella scheda dell'azienda.

### Pratiche

- Elenco e scheda delle pratiche, con filtri.
- Sezione delle pratiche nella dashboard, con i pulsanti per ateneo e tipo di corso.
- Documento PDF della pratica, a partire dal modulo eCampus per i corsi di laurea.

### Prodotti formativi

- Elenco dei prodotti formativi con filtri e ricerca.
- Creazione e modifica dei prodotti con le righe di prezzo; la fine della validità di ogni riga si calcola da sola.

### Interfaccia

- Menu laterale, tema grafico unico e indirizzi propri per ogni pagina.
- Nuova grafica degli elenchi, con righe cliccabili.
- In fondo al menu compaiono il numero della versione e la data dell'ultimo aggiornamento.

### Pubblicazione, sicurezza e dati

- Ambiente di collaudo pubblicato con un solo comando da Windows, con controlli preliminari e ritorno automatico alla versione precedente se qualcosa non va.
- Avviso quando si pubblica un ramo diverso da main; contatore delle pubblicazioni riuscite.
- Chiusi i servizi che rispondevano senza accesso; il server non parte se la configurazione dei segreti non è valida.
- Password protette con bcrypt, convertite al primo accesso di ciascun utente.
- Migrazioni del database con procedura di annullamento e suite di test automatici.
