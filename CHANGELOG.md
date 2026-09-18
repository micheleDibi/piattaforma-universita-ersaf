# Registro delle modifiche

Le novità della Piattaforma Università, versione per versione, dalla più recente.

Una versione è una pubblicazione riuscita sul collaudo: numero, data e ora sono gli stessi che l'applicazione mostra in fondo al menu. Ogni versione ha due parti:

- **Novità e correzioni**: cosa cambia per chi usa la piattaforma.
- **Dettagli tecnici**: migrazioni del database, API cambiate, modifiche incompatibili, sicurezza.

Il file non si modifica a mano. Chi fa una modifica scrive un frammento in `changelog/non-pubblicato/` (formato ed esempi in [changelog/MODELLO.md](changelog/MODELLO.md)); alla pubblicazione il deploy raccoglie i frammenti e scrive qui la versione. Il meccanismo è descritto in [documentazione](docs/tecnica/documentazione.md) e in [deploy](docs/tecnica/deploy.md).

<!-- nuove-versioni: il timbro del deploy inserisce qui sotto le versioni pubblicate; non spostare questa riga -->

## Versione 6 — 18/09/2026 12:14

<!-- timbro: versione=6 sha=18bd6255bc7866464cb7519cf7823b96dd537a9c -->

### Novità e correzioni

**Corretto**

- La generazione consecutiva di documenti di tipi diversi non accumula più la memoria del compilatore nell’API.

### Dettagli tecnici

**Modificato**

- Ogni PDF viene compilato in un processo breve, una richiesta alla volta per processo API, con timeout e pulizia degli allegati anche in caso di interruzione.

**Sicurezza**

- I dati del documento passano tramite stdin; gli errori del processo non espongono dati personali.

## Versione 5 — 18/09/2026 12:08

<!-- timbro: versione=5 sha=dc19af27d1a8bfb5694e8480b79e9971987a8bb1 -->

### Novità e correzioni

**Aggiunto**

- Avvisi su anagrafiche con codice fiscale o email non validi e dati duplicati, consultabili dall’elenco e dalla scheda anche su mobile.
- Il documento della pratica è disponibile per lauree, master, perfezionamento, formazione e corsi singoli degli enti per cui è presente il modulo originale.
- Gli insegnamenti dei corsi singoli che superano le righe del modulo continuano su una pagina aggiuntiva della domanda.
- Le pratiche eCampus con rate salvate includono l'accordo di rateizzazione nel PDF; i piani oltre dodici rate proseguono su pagine aggiuntive.

**Modificato**

- Il pannello degli atenei si apre dalla pagina Pratiche; il Nazionale dispone della voce dedicata nel menu.
- Aziende è visibile nel menu anche a Regionale e Provinciale.

**Corretto**

- Gli avvisi non aprono accidentalmente la scheda e usano il tema e il dialogo condivisi.
- Le dichiarazioni non indicano più come mai immatricolato uno studente con una carriera universitaria già registrata.
- I valori più lunghi delle caselle del modulo restano completi nel documento.

### Dettagli tecnici

**Aggiunto**

- Dodici moduli oltre a eCampus lauree, con registro unico, layout dichiarativi, sfondi condivisi e mapping comune; nessuna migrazione o dipendenza aggiuntiva.
- Lettura della tabella legacy delle dilazioni eCampus, con importi Decimal, ordinamento per scadenza e ID e tasse separate; composizione dell'accordo centralizzata nel registro dei modelli.

**Modificato**

- Il confronto delle anomalie interroga solo i valori della pagina; codice fiscale ed email modificati usano la validazione completa.
- I corsi richiesti usano la scheda corsi singoli più recente, con fallback ai legami della pratica; gli esami sostenuti restano distinti e riportano i CFU nei moduli SSML.
- I tipi privi di un originale identificato restano non disponibili; nessuna scelta automatica di un modulo alternativo e nessun consenso presunto per i nuovi enti.

**Corretto**

- Risolte funzioni e proprietà duplicate introdotte dall’integrazione, preservati caricamento del curriculum e controllo della scadenza del documento.

**Sicurezza**

- Il dettaglio cliente e il confronto dei duplicati applicano la visibilità centralizzata; nessun nominativo esterno alla portata dell’utente viene esposto.
- Disponibilità e download dei documenti applicano il filtro per azienda centralizzato delle pratiche, con risposta 404 per i documenti non visibili.

## Versione 4 — 18/09/2026 10:00

<!-- timbro: versione=4 sha=4c73d2cc8922cfcecd17933725b2881e67f9de15 -->

### Novità e correzioni

**Aggiunto**

- È disponibile una guida alla piattaforma per chi la usa: pagine, ruoli e permessi, accesso, sottoscrittori e attuatori, aziende, pratiche e prodotti formativi. (PR #3)
- A ogni pubblicazione il registro delle modifiche riporta le novità della versione, con lo stesso numero e la stessa data mostrati in fondo al menu. (PR #3)
- Negli elenchi Sottoscrittori e Attuatori una colonna Stato mostra con dei pallini se l'email e il cellulare sono stati verificati e, per i sottoscrittori, se il diploma è completo. Sopra l'elenco c'è la legenda che spiega i pallini. (PR #4)

**Modificato**

- Chi vede quali sottoscrittori, quali aziende e quali pratiche segue adesso la stessa regola in tutta la piattaforma. (PR #4)

**Corretto**

- Nella sezione dei titoli di studio l'anno di conseguimento si scrive come anno scolastico. Prima i due campi chiedevano una data e salvavano nel posto sbagliato. (PR #4)

**Sicurezza**

- Chi non è Nazionale non può più assegnare il ruolo Nazionale, nemmeno a se stesso, e non può più cambiare il proprio ruolo né la propria azienda. Restano modificabili il ruolo e l'azienda delle persone che vede. (PR #4)

### Dettagli tecnici

**Aggiunto**

- Documentazione in `docs/` (funzionale e tecnica), `README.md`, `CLAUDE.md` per gli agenti e riferimenti generati da `scripts/documentazione/genera.py` (API, pagine, migrazioni, configurazione). (PR #3)
- Controllo `.github/workflows/documentazione.yml` sulle pull request verso main: frammento di changelog, documenti collegati secondo `docs/mappa-documentazione.yml`, link interni e pagine generate. Esenzioni con le etichette `senza-changelog` e `documentazione-invariata`. (PR #3)
- Timbro del changelog dopo il deploy di origin/main (`scripts/documentazione/timbra_changelog.py`), con il comando remoto in sola lettura `release-info`; gate `Docs` in `scripts/verify-local.ps1`. (PR #3)
- `backend/src/auth/visibilita.py` è l'unico punto che contiene la regola di visibilità, per clienti, aziende e pratiche; i router la chiamano invece di riscriverla. La CTE ricorsiva segnala il superamento di `max_recursive_iterations` invece di restituire in silenzio un risultato parziale. (PR #4)
- migrazione `016_indici_visibilita_clienti` con gli indici che sostengono i filtri di visibilità, e il suo rollback. (PR #4)
- `diploma_completo` sugli elenchi e sulla scheda dei clienti, calcolato con una `selectinload` del curriculum: nessuna query per riga. La regola dei campi del diploma sta in `universita/models.py` e vale sia per l'elenco sia per la scheda. (PR #4)

**Modificato**

- `.gitattributes` impone LF ai file Markdown e agli strumenti della documentazione; commenti di `backend/.env.example` e `db/README.md` allineati al codice. (PR #3)
- `universita_anno_scolastico` e `universita_anno_scolastico_ai` sono campi di testo da 45 caratteri, come lo schema. Nessuna migrazione dei dati. (PR #4)
- le liste dei campi azienda stanno in `frontend/src/config/campiAzienda.js`, così un file di componente esporta solo componenti e il fast refresh di Vite non ricarica la pagina. (PR #4)

**Sicurezza**

- `verifica_ruolo_assegnabile` e `verifica_azienda_assegnabile` chiudono l'innalzamento di privilegi che si otteneva scrivendo sulla propria riga `clienti`, sempre visibile per costruzione: il ruolo dava la vista del Nazionale, l'azienda spostava la visibilità di pratiche, colleghi e aziende. Riassegnare il valore già presente resta ammesso, perché la scheda rimanda tutti i campi a ogni salvataggio. (PR #4)

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
