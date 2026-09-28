# Registro delle modifiche

Le novità della Piattaforma Università, versione per versione, dalla più recente.

Una versione è una pubblicazione riuscita sul collaudo: numero, data e ora sono gli stessi che l'applicazione mostra in fondo al menu. Ogni versione ha due parti:

- **Novità e correzioni**: cosa cambia per chi usa la piattaforma.
- **Dettagli tecnici**: migrazioni del database, API cambiate, modifiche incompatibili, sicurezza.

Il file non si modifica a mano. Chi fa una modifica scrive un frammento in `changelog/non-pubblicato/` (formato ed esempi in [changelog/MODELLO.md](changelog/MODELLO.md)); alla pubblicazione il deploy raccoglie i frammenti e scrive qui la versione. Il meccanismo è descritto in [documentazione](docs/tecnica/documentazione.md) e in [deploy](docs/tecnica/deploy.md).

<!-- nuove-versioni: il timbro del deploy inserisce qui sotto le versioni pubblicate; non spostare questa riga -->

## Versione 11 — 25/09/2026 11:35

<!-- timbro: versione=11 sha=26d6d2d48fee707501c192cd589f7560a20e3bcf -->

### Novità e correzioni

**Modificato**

- La pagina Pratiche mostra il numero di pratiche per ateneo, tipologia di corso e stato: in cima il totale e quello di ogni stato, poi una tabella per ateneo con il totale di ogni riga e dell'ateneo.
- Nella pagina Pratiche si apre l'elenco filtrato scegliendo la riga di una tipologia, al posto del pulsante; senza abilitazione la riga resta visibile ma sbiadita.
- Sul telefono e negli spazi stretti la tabella di ogni ateneo diventa un elenco, con i sei stati sotto il nome della tipologia.
- Nell'elenco delle pratiche lo stato non ha più il pallino: è verde, con la spunta, quando la pratica è conclusa, altrimenti resta neutro.

### Dettagli tecnici

**Aggiunto**

- `GET /pratiche/conteggi` restituisce il numero di pratiche per università, tipo di corso e stato, con la stessa visibilità di `GET /pratiche/` perché passa da `query_filtrata`.
- Le colonne di stato degli elenchi accettano `puntino: false`, che mostra la spunta al posto del pallino solo con il tono positivo; `rigaPratica` calcola il tono dalla descrizione dello stato.

**Modificato**

- Il pannello somma i gruppi secondo i tipi di corso di ogni riga in `lib/pannelloPratiche.js`; stili in `config/styles/pannelloPratiche.css` con soglie del contenitore a 480, 720 e 820px, nuovi campioni e ruoli di colore per gli stati, tipografia `text-totale` e `text-conteggio`, opzione `marginiInclusi` di `contenutoPagina()`.

## Versione 10 — 24/09/2026 11:43

<!-- timbro: versione=10 sha=334d3addd4a81b60fd0ccc2f61bbc8209988af27 -->

### Novità e correzioni

**Aggiunto**

- Nelle schede di sottoscrittori, attuatori e aziende i campi con un'anomalia hanno il bordo giallo e una nota breve sotto, per esempio «Duplicato con 2 anagrafiche» o «Da compilare», che sparisce appena si modifica il campo.
- Nella scheda di un'azienda, sotto il titolo, la ragione sociale è seguita da «Figlia di» e dal nome dell'azienda padre; la ragione sociale sotto il titolo è quella salvata e non cambia mentre si scrive.

**Modificato**

- Tutta l'applicazione adotta il nuovo linguaggio visivo: cambiano colori, caratteri, pulsanti, campi, messaggi, schede e intestazioni delle pagine; menu laterale e barra superiore mantengono la loro struttura e la voce attiva dorata.
- Negli elenchi Sottoscrittori e Attuatori nominativo e azienda vanno a capo al massimo su due righe e si leggono per intero passando il mouse; la testata con ricerca, «Filtri» e «Nuovo», anche quando resta agganciata in alto, forma una sola scheda con l'elenco.
- Negli elenchi il segnale giallo accanto al nome apre, subito sotto, un riquadro con il numero di errori e l'elenco; si chiude cliccando fuori o con Esc e non apre la scheda.
- Su schermi stretti, se non c'è spazio, il numero di risultati va a capo sotto il titolo dell'elenco invece di spezzare il titolo.
- Nella scheda di sottoscrittori e attuatori nome, codice fiscale e stato dell'account stanno su una riga sotto il titolo e non cambiano più mentre si scrive nei campi; «Annulla» e «Salva modifiche» restano visibili in fondo mentre si scorre.
- Nei dati principali email e cellulare stanno in riquadri in evidenza con lo stato di verifica; PEC e telefono sono raccolti in «Altri recapiti».
- Nel curriculum le sotto-schede si scelgono da un selettore, gli altri titoli sono in una tabella e le caselle si attivano anche con un clic sul testo; nella scheda Utente le date della cronologia sono sempre in formato italiano.
- Nella scheda Abilitazioni dell'attuatore ogni abilitazione è un riquadro con l'interruttore, che si attiva anche con un clic sul nome.
- Gli avvisi di un'anagrafica in cima alla scheda del sottoscrittore e dell'azienda hanno lo stesso aspetto degli altri messaggi, con un elenco puntato quando sono più di uno.
- Nella scheda dell'azienda una partita IVA diversa da 11 cifre è segnalata in giallo, come avviso, e non più in rosso; il codice nazionale si può selezionare e copiare, e Codice SDI, PEC, IBAN e Codice BIC mostrano un esempio quando sono vuoti.
- La provincia di un'azienda, ora «Prov.», accetta al massimo 2 caratteri, anche nella creazione rapida dalla scheda Azienda di un attuatore.
- Nella finestra «Nessuna azienda trovata con questa Partita IVA» IBAN e BIC stanno sulla stessa riga e i pulsanti «Annulla» e «Crea e associa» sono in basso a destra.
- Nella pagina Pratiche il pannello degli atenei sta in un riquadro sotto il titolo; nell'elenco delle pratiche il corso va a capo al massimo su due righe e lo stato resta su una.
- I campi numerici, come percentuali, voti, durata e CFU, non mostrano più le frecce per aumentare o diminuire il valore.

### Dettagli tecnici

**Aggiunto**

- In `palette.css` un secondo blocco di campioni con i valori esatti del design (`ardesia`, `indaco`, `ambra`, `muschio`, `mattone`); i ruoli di `colori.css` li richiamano.
- `barraAzioniModulo()` in `superficie.js`, agganciata in fondo alla scheda (`"scheda"`) o semplice in fondo alla pagina (`"pagina"`); `barraAzioni.css` riserva in fondo l'altezza della barra (`scroll-padding-bottom`), così il campo che riceve il fuoco non finisce sotto di essa.
- `tabellaCampi()`, `intestazioneCampi()` e `rigaCampi()` in `tabella.js` per le tabelle di campi a griglia; `pillola.js` per le pillole di stato ed etichetta; `schedaEvidenziata()` e `separatoreTratteggiato()` in `superficie.js`.
- Composizioni per schermata in `config/styles/anagrafica.js`, `config/styles/azienda.js` e `STILI_PANNELLO_PRATICHE` in `pratica.js`; testi in `config/testi/anagrafica.js`, `azienda.js` e `pratiche.js`, più quelli degli elenchi dei clienti in `config/testi/elenco.js`.
- `lib/anomalieCampi.js` ricava dalle anomalie restituite da `GET /clienti/{id}` e `GET /aziende/{id}` le note per campo, con i testi in `config/testi/anomalie.js`, senza modifiche all'API.
- `lib/schedaAnagrafica.js` (stato dell'account, verifica dei recapiti, date) e `lib/schedaAzienda.js` (sottotitolo, controllo della partita IVA, note per campo, lettura del padre), con i test; l'hook `usePadreAzienda` legge il padre una volta per il sottotitolo e per `GerarchiaAzienda`, che lo riceve con `onRicarica`.

**Modificato**

- `tipografia.css` ha nuove dimensioni (`titolo-elenco`, `titolo-evidenziato`, `descrizione`, `dettaglio`, `evidenziato`, `avviso`), con interlinea `normal` dove il design non la fissa; `controlli.css` aggiunge i raggi `evidenza`, `riquadro`, `segmento` e `comando`, le altezze `h-controllo` (42px) e `h-controllo-compatto` (40px) e porta `max-w-pagina` a 1120px e `max-w-modulo` a 1080px.
- `pulsante()` ha le varianti `contorno` (bordo grigio), `contornoPrimario` e `testuale`, le dimensioni `medio` e `minimo` e i sinonimi `barra` e `testata`; il passaggio del puntatore vale anche per i link stilati come pulsante.
- `campo()` ha nuove dimensioni e le opzioni `avviso` e `fuocoAvviso`; `CampoModulo` accetta note sotto il campo; `SezioneModulo` accetta rilievo, etichetta, azioni e contenuto evidenziato; `BarraSchede` ha la variante `segmentata`; `IntestazionePagina` accetta una descrizione composta; `AlertMessage` mostra come elenco puntato un testo fatto di più voci.
- `AvvisoTooltip` usa un popover nativo ancorato al segnale, reso in un portale su `document.body`, al posto della finestra di dialogo, con gli stili in `avvisi.css`; `posizionePopover()` accetta `allinea` e `rientro`.
- `config/campiAzienda.js` contiene solo la struttura (nomi dei campi, `PROPRIETA_CAMPI`, sezioni per chiave); `CampiAzienda` usa `soloLettura` (readOnly) al posto di `disabilita`.
- Negli elenchi i valori `principale` e `secondario` si fermano a due righe (`line-clamp-2` in `righeElenco.css`); una colonna con `righe: 2` in `config/elenchi.js` ha in più il `title` con il valore intero; la tabella usa i bordi separati, con il bordo inferiore sulle celle.

**Rimosso**

- `erroreCampo()`, sostituito da `notaCampo("errore")`, `STILI_AVVISI` di `feedback.js` e il ruolo `accento-tenue-hover`, rimasto senza uso.

## Versione 9 — 23/09/2026 14:50

<!-- timbro: versione=9 sha=deb3259ce5c887c92fa725e0e0f2bd4e002f4c58 -->

### Novità e correzioni

**Aggiunto**

- Accanto al titolo degli elenchi Sottoscrittori e Attuatori compare il numero di risultati, che segue ricerca e filtri.

**Modificato**

- Negli elenchi Sottoscrittori e Attuatori nome e cognome sono in un'unica colonna Nominativo («Cognome Nome»), con le iniziali in un cerchio e il segnale di avviso subito accanto.
- Le verifiche di email, cellulare e diploma sono etichette con il loro nome, verdi con la spunta quando sono a posto; la legenda sopra l'elenco non serve più ed è stata tolta.
- La finestra degli avvisi di un'anagrafica ha come titolo il numero di errori.
- La pagina Modifica azienda è divisa in sezioni (Dati anagrafici, Sede legale, Contatti, Coordinate bancarie, Gerarchia, Convenzioni universitarie) e mostra subito se la partita IVA non ha 11 cifre.
- Le percentuali delle convenzioni universitarie sono in una tabella per ateneo e tipologia di corso, sia nella scheda dell'azienda sia nella scheda Azienda dell'attuatore.
- Le schede di sottoscrittori e attuatori sono divise in sezioni con titolo e descrizione: Informazioni personali, Contatti, Documento, Residenza e Domicilio nei Dati principali; le sezioni del Curriculum formativo; Account e ruolo e Cronologia nella scheda Utente.
- Sotto il titolo della scheda compaiono nome, cognome e codice fiscale, con lo stato dell'account a destra. Email e cellulare verificati hanno l'indicazione accanto all'etichetta.
- Il pulsante di salvataggio della scheda Utente si chiama «Salva utente», per distinguerlo da «Salva modifiche» in fondo alla pagina. Il pulsante di copia del domicilio si chiama «Copia da residenza».
- La scheda Esami mostra «Nessun esame registrato.» al posto del testo provvisorio.

### Dettagli tecnici

**Aggiunto**

- `GET /clienti/conteggio` restituisce `{"totale": n}` con gli stessi filtri e la stessa visibilità di `GET /clienti/`, senza paginazione.
- Componente `shared/SezioneModulo` e `SEZIONI_AZIENDA` in `config/campiAzienda.js`.
- Componenti `shared/SezioneModulo` e `shared/CampoModulo`, stili `sezioneModulo`, `introSezioneModulo`, `campiSezioneModulo` e classe `schede__pannello--sezioni`.

**Modificato**

- I filtri di `GET /clienti/` sono in `_filtra_elenco`, condivisa con il conteggio.
- `DettaglioConvenzioniUniversitarie` accetta `inSezione` per stare dentro una sezione di modulo senza scheda e titolo propri.

## Versione 8 — 23/09/2026 10:04

<!-- timbro: versione=8 sha=bdd9339c896674b2e77d8406dc6eaf70a20bb47d -->

### Novità e correzioni

**Aggiunto**

- Il PDF dei corsi speciali SSML si scarica con il modulo dei corsi di formazione SSML.

### Dettagli tecnici

**Modificato**

- Il registro centrale associa i corsi speciali SSML a `ssml-formazione`, riutilizzando impaginazione e compilazione esistenti.

## Versione 7 — 23/09/2026 10:01

<!-- timbro: versione=7 sha=2f65005d42f15d0772fb7e77017f3838c07f0448 -->

### Novità e correzioni

**Modificato**

- L'elenco Sottoscrittori comprende anche i consulenti.
- L'elenco Attuatori comprende anche gli operatori, che si trovano con il filtro per ruolo; gli operatori continuano a non accedere alla piattaforma.
- Nel menu la voce Attuatori compare anche a Regionale e Provinciale, e la voce Pratiche anche a Regionale, Provinciale e Aderente.
- Il codice nazionale di una nuova azienda viene assegnato automaticamente e non si può più modificare.
- Le percentuali delle convenzioni universitarie stanno nella sezione "Dettaglio convenzioni universitarie": si modificano dalla scheda dell'azienda e si leggono nella scheda Azienda di un attuatore.

**Rimosso**

- Nell'elenco Pratiche non c'è più il filtro per studente.

### Dettagli tecnici

**Aggiunto**

- `GET /clienti/` accetta `solo_sottoscrittori=true` (ruoli Utente e Consulente); `solo_utenti` resta limitato al ruolo Utente, usato dal selettore dello studente nelle pratiche.

**Modificato**

- `solo_attuatori` comprende anche il ruolo Operatore; accesso e recupero della password restano ai ruoli di `RUOLI_ATTUATORE` (Aderente, Regionale, Provinciale, Nazionale).
- `POST /aziende/` genera `azienda_codice_nazionale` (22 caratteri casuali, univoco) e ignora il valore inviato; `PUT /aziende/{id}` non lo modifica più.
- Le voci del menu dichiarano i ruoli che le vedono con `ruoliAmmessi` in `frontend/src/config/routes/rotte.js`.

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
