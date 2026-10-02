# Registro delle modifiche

Le novità della Piattaforma Università, versione per versione, dalla più recente.

Una versione è una pubblicazione riuscita sul collaudo: numero, data e ora sono gli stessi che l'applicazione mostra in fondo al menu. Ogni versione ha due parti:

- **Novità e correzioni**: cosa cambia per chi usa la piattaforma.
- **Dettagli tecnici**: migrazioni del database, API cambiate, modifiche incompatibili, sicurezza.

Il file non si modifica a mano. Chi fa una modifica scrive un frammento in `changelog/non-pubblicato/` (formato ed esempi in [changelog/MODELLO.md](changelog/MODELLO.md)); alla pubblicazione il deploy raccoglie i frammenti e scrive qui la versione. Il meccanismo è descritto in [documentazione](docs/tecnica/documentazione.md) e in [deploy](docs/tecnica/deploy.md).

<!-- nuove-versioni: il timbro del deploy inserisce qui sotto le versioni pubblicate; non spostare questa riga -->

## Versione 21 — 02/10/2026 13:55

<!-- timbro: versione=21 sha=8d9e2702bb32ee487e7821fc8d0d074ae5142e66 -->

### Novità e correzioni

**Aggiunto**

- Nella scheda Utente di un attuatore, Regionale e Provinciale possono riportare a Utente chi sta sotto di loro (il Regionale un Aderente o un Provinciale, il Provinciale un Aderente).
- Un pallino verde accanto agli altri autori indica quando sono online.

**Modificato**

- Il ruolo di una persona si assegna secondo chi lo assegna, sia creando un attuatore sia nella scheda Utente di sottoscrittori e attuatori: il Nazionale assegna qualunque ruolo, il Regionale solo Provinciale o Aderente, il Provinciale solo Aderente; l'Aderente non cambia ruoli. Le tendine mostrano solo le scelte ammesse.
- Dove c'è una sola scelta possibile il ruolo non ha la tendina e compare come valore bloccato: per esempio un Provinciale che crea un attuatore (solo Aderente), la propria scheda (tranne che per il Nazionale), la scheda di chi ha un ruolo più alto (un Regionale che apre un altro Regionale) e ogni scheda vista da un Aderente.
- Un nuovo sottoscrittore nasce sempre con ruolo Utente, chiunque lo crei.
- Nella chat delle pratiche i propri messaggi compaiono a destra e quelli ricevuti a sinistra.
- Il campo messaggio cresce con il testo e il pulsante d'invio resta esterno a destra, allineato in basso.
- Le schede mostrano solo l'indicatore della selezione, senza un divisore continuo.

**Rimosso**

- La chat non mostra più descrizioni superflue o lo stato generico di connessione.

### Dettagli tecnici

**Aggiunto**

- Presenza condivisa fra socket cookie delle pratiche e sessioni realtime, con verifica dei partecipanti e dei criteri comuni di revoca.
- Prove di presenza, revoca, cleanup delle connessioni, quorum e tastiera. Nessuna nuova migrazione o configurazione.

**Modificato**

- `verifica_ruolo_assegnabile` (`backend/src/clienti/servizio.py`) applica `RUOLI_ASSEGNABILI` (`auth/autorizzazioni.py`) in `POST /clienti/con-utente` e `PUT /clienti/{id}`; un ruolo non ammesso risponde 403 "Non puoi assegnare questo ruolo.". Gemella lato client in `frontend/src/lib/permessiSchedaUtente.js`.
- Quote e ordine dei lock delle connessioni sono comuni ai due trasporti; le lease cookie sono escluse dal quorum ACK Bearer.
- Il composer gestisce crescita limitata, invio desktop, nuova riga mobile e composizione IME senza duplicare gli invii o cancellare nuove bozze.

## Versione 20 — 01/10/2026 20:21

<!-- timbro: versione=20 sha=dc04a99b510b0b575e86da23cd2c035996d67a87 -->

Nessuna modifica documentata.

## Versione 19 — 01/10/2026 20:06

<!-- timbro: versione=19 sha=03f0af263e9a278337829aab88e017271633a76d -->

Nessuna modifica documentata.

## Versione 18 — 01/10/2026 16:11

<!-- timbro: versione=18 sha=2982a755bd129cd6640b78cf20afc900086fd112 -->

### Novità e correzioni

**Aggiunto**

- Nell'elenco del Nazionale ci sono le colonne Ultima modifica, Tipo corso e Università (al posto della data di creazione), la ricerca per sottoscrittore e i filtri Codice pratica e Stato.
- Nell'elenco del Nazionale, sotto il titolo, i loghi dei quattro atenei filtrano le pratiche per ateneo; scorrendo restano in alto, più piccoli, accanto al titolo.
- Nella scheda di una pratica eCampus il Nazionale vede e modifica il Codice ASG; gli altri ruoli non lo vedono.

**Modificato**

- Nella scheda Utente il pulsante "Accedi con questo utente" compare solo al Nazionale.
- Per il Nazionale la pagina Pratiche non mostra più il pannello degli atenei ma un unico elenco con tutte le pratiche tranne le Bozze, ordinate per stato (Caricata, In lavorazione, In attesa di modifica, Conclusa, Rifiutata) e, dentro ogni stato, dalla modifica più recente. Senza ricerca né filtri l'elenco ha in testa "Tutte le pratiche" con il totale; con la ricerca o un filtro si divide in un gruppo per stato, con il numero di pratiche accanto a ogni stato.
- In fondo a tutti gli elenchi la scritta "Hai raggiunto la fine dell'elenco", il caricamento e il pulsante "Carica altri elementi" sono centrati e staccati dall'ultima riga.
- Nella scheda azienda, se una percentuale supera quella dell'azienda padre non viene più proposto di azzerarla: il salvataggio si ferma con un errore che indica i campi da correggere e il massimo ammesso per ciascuno.
- La richiesta di conferma nel salvataggio delle percentuali ora compare solo quando i nuovi valori, più bassi, azzererebbero quelli di aziende figlie, e nomina sia gli atenei sia le aziende coinvolte. Il cambio di padre resta invariato.

**Rimosso**

- Il Nazionale non ha più il pulsante "Nuova" nelle pratiche: le gestisce, non le crea.

### Dettagli tecnici

**Aggiunto**

- `GET /pratiche/` accetta `escludi_bozze` e `ordine=stato` (gruppi Caricata, In lavorazione, In attesa di modifica, Conclusa, Rifiutata, poi `COALESCE(pratica_updated_at, pratica_created_at, pratica_dataCreazione)` decrescente): l'ordine sta nella query, quindi la paginazione non spezza i gruppi.
- `GET /pratiche/conteggi/stati`, il numero di pratiche per stato con gli stessi filtri dell'elenco.
- `ElencoPraticheNazionale.jsx` e `useFiltriPraticheNazionale.js`; `SchedaPratica.jsx` riporta il Nazionale all'elenco da `/pratiche/nuova`.
- `ConRuoloVerificato.jsx` e `ricaricaSessione` in `lib/api.js`: elenco e scheda pratica rileggono il ruolo da `GET /auth/session` prima di scegliere la vista, perché quello in memoria resta quello dell'accesso anche se il ruolo cambia dopo.
- `messaggioSuperamento` e `messaggioAzzeramentoFiglie` in `frontend/src/lib/schedaAzienda.js`; `messaggioAzzeramento` resta per il cambio di padre.

**Modificato**

- `SchedaUtente.jsx`, il pulsante dipende anche dal ruolo di chi guarda; `POST /auth/login-as/{id}` resta invariato (accetta ancora Regionale e Nazionale).
- `PUT /aziende/{id}/dettagli` risponde 422 con `detail.messaggio` e `detail.superamenti` (`campo`, `valore`, `limite`) quando un valore supera quello del padre, prima di calcolare la cascata; il 409 con `reset` riguarda ora solo le discendenti. Nuova `superamenti_padre` in `backend/src/aziende_xcod/servizi.py`.

**Sicurezza**

- `pratica_codiceASG` esce nelle risposte delle pratiche solo per il Nazionale (`null` per gli altri ruoli); `PUT /pratiche/{id}` lo accetta solo dal Nazionale e solo su pratiche eCampus (`nome_universita_id` 1), e lo ignora in silenzio negli altri casi; `POST /pratiche/` lo ignora sempre.

## Versione 17 — 01/10/2026 11:26

<!-- timbro: versione=17 sha=5378e95aed4d4a5c0a23053eb99f9f79219f585b -->

### Novità e correzioni

**Aggiunto**

- Nella scheda di una pratica Corsi Speciali compare la sezione "Caratteristiche del percorso" con Modalità di erogazione e CFU, come per i Corsi di perfezionamento.
- Nella selezione dei Corsi Singoli di una pratica, sotto l'elenco compare un riquadro fisso "Corsi selezionati" con un'etichetta per ogni corso già scelto (passandoci sopra si vedono codice e prezzo); la X su ogni etichetta toglie il corso dalla selezione senza doverlo ritrovare nell'elenco.
- Nella finestra di selezione dello studente di una pratica nuova c'è una colonna con la matita che apre la scheda del sottoscrittore, anche per chi non è ancora selezionabile. Prima di lasciare la pratica viene chiesta conferma, perché le modifiche non salvate andrebbero perse.

**Modificato**

- Nella scheda di una pratica Corsi Singoli la sezione "Caratteristiche del percorso" è sostituita da "Corsi selezionati": una riga per corso con codice, denominazione, corso di laurea, CFU e prezzo; in creazione ogni riga ha una X per togliere il corso. Nel campo "Corsi" della sezione Iscrizione resta il numero dei corsi scelti.
- Nella scheda Utente i campi che non si hanno i permessi di modificare sono bloccati: nome utente, stato e "Cambia padre" per chi non è Regionale o Nazionale (sulle schede degli altri), il ruolo sulla propria scheda per chi non è Nazionale, e la voce Nazionale delle tendine del ruolo per chi non è Nazionale.

**Corretto**

- Aprendo una pratica Corsi Singoli già salvata si vedono tutti i corsi scelti, non più solo il primo.
- Cambiare il ruolo dalla scheda Utente di un attuatore ora viene salvato: prima "Salva modifiche" lo riportava al valore della tendina "Ruolo attuatore" di Dati principali. Le due tendine mostrano sempre lo stesso ruolo e funzionano entrambe.
- All'apertura della finestra di selezione dello studente non compaiono più due barre di scorrimento, una per l'elenco e una per la finestra.

**Rimosso**

- Gli avvisi "Correggi l'errore nella scheda Utente prima di salvare." e "Non hai i permessi per modificare un altro utente." non compaiono più.

### Dettagli tecnici

**Aggiunto**

- `GET /pratiche/{id}` (e la risposta di creazione e modifica) restituisce `corsi`, l'elenco delle righe di `pratiche_listini` con codice, descrizione, prezzo salvato, CFU del dettaglio di listino valido alla data di creazione e corso di laurea; `null` nell'elenco `GET /pratiche/`, che non carica la relazione. Le 12 pratiche Corsi Singoli del 2022 senza righe in `pratiche_listini` hanno `corsi` vuoto e la scheda mostra il solo corso principale; per 4 di queste gli altri corsi in `listTesta_corso2_id`/`listTesta_corso3_id`, senza prezzo per corso, restano esclusi per scelta.
- `ElencoCorsiPratica.jsx`; `SchedaPratica.jsx` riconosce una pratica Corsi Singoli salvata anche dal suo `listino_tipo_corso_id`, quando l'indirizzo non porta il contesto. `formattaImporto` spostata in `lib/praticaForm.js`.
- `lib/permessiSchedaUtente.js`, con i test, rispecchia i controlli di `PUT /utenti/{id}` e `verifica_ruolo_assegnabile`; `SchedaUtente.salva()` non manda `PUT /utenti/{id}` senza il permesso sull'account.

**Modificato**

- `config/pratica.js`, il tipo di corso 10 (Corsi speciali) usa i campi del gruppo `perfezionamento`.
- `GET /listini-testa/` carica il corso di laurea con un join, per la selezione dei Corsi Singoli.
- Il ruolo è uno stato di `NuovoSottoscrittore.jsx` passato a `SchedaUtente.jsx` (`ruoloId`, `onCambiaRuolo`), invece di due stati separati.
- `ModaleSelezionePercorso.jsx`, solo con `multipla`: riepilogo a pillole fuori dal corpo scorrevole, alto al massimo circa tre righe e poi scorrevole; la X usa lo stesso `clicca()` delle righe dell'elenco.

## Versione 16 — 30/09/2026 19:04

<!-- timbro: versione=16 sha=db8bf9d2767e3ca2be00695b163b5bf6a1b45e65 -->

### Novità e correzioni

**Aggiunto**

- Creando una pratica SSML o A4U si creano anche il suo articolo e il suo partitario nella gestione pagamenti, con il prezzo della pratica e una numerazione che continua quella esistente. Per A4U il codice pratica viene registrato anche come codice definitivo.

**Modificato**

- Se manca un dato che serve alla parte contabile, per esempio chi crea la pratica non ha una scheda cliente, la pratica SSML o A4U non viene salvata e compare un errore.

### Dettagli tecnici

**Aggiunto**

- `POST /pratiche/` per SSML e A4U scrive `articolo`, `articolo_pratica`, `documento` (partitario) e `documento_articolo` nello schema dei pagamenti, e per A4U una riga in `pratica_codice`, nella stessa transazione della pratica (`pratiche/dopo_salvataggio.py`, porting di `Pratica.AfterSave`). Un dato di riferimento mancante risponde 400 e non scrive nulla.
- Configurazione `SCHEMA_GESTIONE_PAGAMENTI` (predefinito `admin_gestione_pagamenti`): nome dello schema dei pagamenti sullo stesso server, letto con la connessione di `DATABASE_URL`, il cui utente deve poterci scrivere.
- Migrazione `022_contatori_articolo_partitario.sql`, con rollback: porta `pratiche_contatori.prefisso` a 32 caratteri. I contatori `ARTICOLO_PRATICA_` e `PARTITARIO_PRATICA_` si riallineano nel codice al massimo esistente a ogni uso (`prossimo_numero_oltre`).

**Modificato**

- Il gruppo articolo si sceglie dall'id del tipo di corso: Master area scuola e Master classi di concorso vanno su `PRATICA MASTER`, Corsi di formazione su `PRATICA CORSI DI ALTA FORMAZIONE`.

**Rimosso**

- Rispetto all'originale restano fuori le cartelle FTP della pratica (`ftp_path` non ha percorsi per le pratiche e il backend non gestisce ancora i file) e l'azzeramento di `pratica_pathFile` al cambio di stato (PDF del gestionale precedente, non usato da questo backend).

## Versione 15 — 30/09/2026 16:41

<!-- timbro: versione=15 sha=e805d86accaa0adfddcddcfe4d8750ecdd7cdce5 -->

### Dettagli tecnici

**Aggiunto**

- Il compilatore PDF scrive su stderr solo una categoria dell'errore, che `documenti/esecuzione.py` registra nel log con il codice d'uscita; anche l'interruzione per tempo scaduto finisce nel log.

**Corretto**

- La cache dei modelli PDF sotto la cartella temporanea si confronta con il modello a ogni composizione, file per file con la dimensione, e si rifà se ne manca qualcuno: prima una cartella rimasta senza `modulo.typ` o senza immagini, per esempio dopo la pulizia automatica dei temporanei di Windows, restava in uso e ogni PDF di quel modello falliva.

## Versione 14 — 30/09/2026 16:23

<!-- timbro: versione=14 sha=796e4e7e7ad0ccf01c4b761caed283a6b52a95c3 -->

### Novità e correzioni

**Modificato**

- L'avviso prima di azzerare delle percentuali (nella scheda dell'azienda e nel cambio di padre) ora indica quali atenei verrebbero coinvolti, invece del generico "Alcune percentuali verranno azzerate", con una nota più piccola che ricorda che una percentuale non può superare quella dell'azienda padre.
- Nella scheda dell'azienda il pulsante "Salva percentuali" non c'è più: "Salva modifiche" salva anche le percentuali delle convenzioni universitarie. Se il salvataggio azzererebbe delle percentuali a cascata sulle aziende figlie, compare comunque la richiesta di conferma, e finché non si conferma non si salva niente (né le percentuali né il resto della scheda).
- Nella scheda di un sottoscrittore o attuatore il pulsante "Salva utente" non c'è più: "Salva modifiche" salva anche username, stato dell'account, utente padre e ruolo della scheda Utente, qualunque sia la scheda aperta al momento.
- La tendina "Ruolo attuatore" (Dati principali) parte già su Aderente, senza la voce segnaposto "Aderente (default)".

### Dettagli tecnici

**Aggiunto**

- `messaggioAzzeramento` in `frontend/src/lib/schedaAzienda.js`, che compone il testo dell'avviso a partire dal campo `reset` già restituito dal server con il 409 (prima ignorato); usato sia da `DettaglioConvenzioniUniversitarie.jsx` sia da `GerarchiaAzienda.jsx`. Nessuna modifica al backend.
- `AlertMessage` accetta ora `message.nota`, una riga più piccola sotto il testo principale ma dentro lo stesso riquadro colorato (nuovo `notaFeedback` in `frontend/src/config/styles/feedback.js`).
- `caricaDettaglioConvenzioni`/`salvaDettaglioConvenzioni` in `frontend/src/lib/schedaAzienda.js`.

**Modificato**

- `DettaglioConvenzioniUniversitarie.jsx` non ha più stato o effetti propri: lettura, scrittura e conferma dell'azzeramento a cascata vivono nel nuovo hook `useDettaglioConvenzioni` (`frontend/src/hooks/useDettaglioConvenzioni.js`), usato sia da `SchedaAzienda.jsx` (in scrittura) sia da `SchedaAziendaAttuatori.jsx` (in sola lettura).
- `SchedaAzienda.jsx` salva prima le percentuali (l'unica parte che può chiedere conferma) e solo dopo l'anagrafica; nessuna modifica al backend, restano due `PUT` distinte in sequenza.
- `SchedaUtente.jsx` non ha più un pulsante di salvataggio proprio: espone `salva()` tramite `useImperativeHandle` (ref come prop, React 19), chiamata da `NuovoSottoscrittore.jsx` in `handleSubmit` prima del resto del salvataggio. Il componente resta sempre montato (nascosto con `hidden` quando non è la scheda attiva, non smontato): altrimenti cambiare scheda prima di salvare avrebbe perso le sue modifiche non ancora salvate.
- La tendina "Ruolo attuatore" di `NuovoSottoscrittore.jsx` parte su Aderente già in creazione, letto da `GET /ruoli/`, invece di una voce segnaposto vuota.

## Versione 13 — 30/09/2026 10:41

<!-- timbro: versione=13 sha=7f7bd2b66581e30032064787ece50cb26ec181e6 -->

### Novità e correzioni

**Aggiunto**

- Nel menu, dopo le altre voci, c'è la voce EduNews24, per tutti i ruoli che accedono: apre una pagina con notizie, interpelli e annunci di selezione del personale del portale EduNews24, con i filtri per categoria, video e area e il pulsante «Carica altri elementi».
- Quando EduNews24 è attivo, la Dashboard mostra un riquadro con l'articolo in evidenza, con immagine o video, e una fascia di notizie da scorrere a mano da cui si sceglie quale mettere in evidenza; per interpelli e selezione mostra la voce più recente e un breve elenco delle successive.
- Le voci di EduNews24 riportano «Fonte: EduNews24» e il loro titolo apre l'articolo originale in una nuova scheda; i video partono solo premendo il pulsante di riproduzione, uno alla volta.
- La testata di EduNews24 ha i collegamenti ai profili Facebook e Instagram del portale.
- Se EduNews24 non risponde si vedono gli ultimi contenuti ricevuti, segnalati come non aggiornati dopo qualche minuto, oppure un avviso con «Riprova».
- La sezione EduNews24 è attiva subito, anche sul collaudo, senza bisogno di configurarla; se viene spenta, la pagina EduNews24 lo spiega e la Dashboard non mostra il riquadro.
- Nelle pratiche Lauree si può scegliere il rinnovo del primo, secondo o terzo anno; la selezione di un anno esclude gli altri.
- Lo studente riceve una conferma al primo ingresso della pratica in Bozza; l'ufficio pratiche riceve una notifica al primo passaggio in Caricata.

**Modificato**

- Dopo l'accesso, e dopo «Accedi con questo utente», si arriva alla Dashboard per tutti i ruoli; chi era stato mandato all'accesso da un indirizzo diretto o da una sessione scaduta torna ancora alla pagina richiesta.
- La Dashboard accoglie con un benvenuto e con le scorciatoie alle voci del menu del proprio ruolo, ciascuna con una breve descrizione.
- Nella pagina non trovata, «Torna all'applicazione» porta alla Dashboard.
- Le nuove pratiche nascono in Bozza; solo il Nazionale può cambiarne lo stato.

**Corretto**

- Gli aggiornamenti parziali non possono lasciare due anni di rinnovo selezionati contemporaneamente. I valori storici restano consultabili.
- Salvataggi contemporanei della stessa pratica non duplicano le notifiche di cambio stato.

### Dettagli tecnici

**Aggiunto**

- Modulo `backend/src/edunews24/`: proxy di sola lettura verso l'API di EduNews24, con le rotte `GET /edunews24/notizie`, `GET /edunews24/interpelli`, `GET /edunews24/selezione-personale` e `GET /edunews24/categorie` protette dalla sessione e sempre `Cache-Control: no-store`; cache in memoria condivisa che segue `Cache-Control` (`s-maxage`, `stale-while-revalidate`, `stale-if-error`) ed `ETag`, un solo rinnovo per chiave, semaforo non bloccante, budget in uscita e pause che rispettano `Retry-After`.
- Risposte delle rotte EduNews24: `{attiva, elementi, meta}`, con 200 e `meta.stantio: true` per una copia servita oltre la finestra di `stale-while-revalidate` o marcata stantia a monte; 200 con `attiva: false` a funzione spenta; 503 con `Retry-After` senza copia, anche per un 429 di EduNews24; 409 per un cursore non emesso dal backend o rifiutato a monte; 400 per l'area nazionale sugli interpelli o per una categoria sconosciuta; 422 per un parametro fuori elenco. Le notizie portano anche `titolo_breve`; interpelli e selezione `sintesi`, `classe_concorso` (solo interpelli), `figura` e `posti` (solo selezione).
- Variabili nuove, facoltative, con la sezione attiva per impostazione predefinita: `EDUNEWS24_BACKEND` (`http`, `memoria`, `disabilitato`; predefinito `http`, `disabilitato` la spegne); `EDUNEWS24_URL_BASE` ed `EDUNEWS24_HOST_MEDIA`, che per difetto valgono l'API pubblica e l'host dei media di EduNews24 (valori solo in `backend/src/config.py` e `backend/.env.example`); `EDUNEWS24_CONTATTO`, che per difetto vale l'indirizzo generico dell'ente e, se svuotato, lascia lo User-Agent a `PiattaformaUniversita/1.0`; sette valori numerici (`EDUNEWS24_TIMEOUT_*`, `EDUNEWS24_TTL_RIPIEGO_SECONDI`, `EDUNEWS24_STANTIO_MASSIMO_SECONDI`, `EDUNEWS24_PAUSA_RIPIEGO_SECONDI`, `EDUNEWS24_RICHIESTE_AL_MINUTO`). Con `http` l'avvio controlla URL base, contatto se presente, host dei media e numeri, e in produzione rifiuta `memoria`. Una riga `EDUNEWS24_*` vuota in `shared/api.env` o in `backend/.env` prevale sul predefinito.
- Frontend: componenti in `components/edunews24/` e `components/dashboard/`, logica in `lib/edunews24.js`, `lib/edunews24Api.js`, `lib/edunews24Paginazione.js`, `lib/videoEsclusivo.js` e `lib/dashboard.js`; identità EduNews24 in `config/tokens/edunews24.css` e `config/styles/edunews24.css`, applicata solo dentro `.edunews24`. Le scorciatoie della Dashboard derivano da `vociMenuPerRuolo`: una voce di menu nuova richiede la sua descrizione in `config/testi/dashboard.js`, e `tests/dashboard.test.js` lo controlla.
- Le 20 regioni di EduNews24 stanno sia in `backend/src/edunews24/costanti.py` sia in `frontend/src/config/edunews24.js`; `backend/tests/unit/test_regioni_allineate.py` le confronta.
- Deploy: overlay `deploy/compose.edunews24.yml` con una rete di uscita solo HTTPS (e DNS verso i nameserver dell'host), attiva per impostazione predefinita: `USCITA_EDUNEWS24` assente, vuota o `si` in `shared/compose.env` la lascia attiva, qualunque altro valore (per esempio `no`) la spegne (`uscita_edunews24_attiva` in `deploy/remote/00-lib.sh`; `compose.env.example` riporta `USCITA_EDUNEWS24=si`). `deploy/remote/27-edunews24.sh` installa il firewall durante il solo `deploy` e poi copia l'overlay in `shared/`, ma non installa nulla e toglie la copia se l'overlay della release non usa il bridge filtrato dalle regole. `compose_rel` collega la rete solo se valgono quattro condizioni: la chiave assente, vuota o a `si`, `NOTIFICHE_REALI` diverso da `si`, niente `SMS_BACKEND=skebby` in `shared/api.env` e la copia in `shared/`; altrimenti avvisa senza fermarsi. Su un collaudo senza la chiave il primo deploy installa da solo il firewall e collega la rete.
- Test di `compose_rel`, di `prepara_edunews24` con gli SMS reali (più forme della chiave `SMS_BACKEND`, un solo avviso, copia tolta) e con `USCITA_EDUNEWS24` assente, vuota, a `si` o con un altro valore, e dello script del firewall con `docker` e `iptables` finti in `scripts/documentazione/tests/test_deploy_edunews24.py`; in `backend/tests/unit/test_config.py` i predefiniti di EduNews24 superano la verifica anche in produzione e `backend/.env.example` li riporta uguali; `test_env_example_contiene_ogni_impostazione` riconosce ora i nomi con cifre (`^([A-Z][A-Z0-9_]*)=`).
- Test sui flag legacy, sulla modifica parziale del rinnovo e sulla conservazione dei campi non visibili; nessuna nuova migrazione.
- Storico degli stati nella transazione della pratica, template email esistenti e destinazione dell'ufficio configurabile tramite `EMAIL_NOTIFICHE_PRATICHE`; nessuna nuova migrazione.

**Modificato**

- I logger `httpx` e `httpcore` stanno a WARNING in `configura_logging`: a INFO registravano l'URL completo di ogni chiamata esterna, comprese quelle degli SMS.
- `ROTTA_INIZIALE` vale `ROTTE.dashboard`; nuova rotta `/edunews24` con la voce in fondo a `VOCI_MENU`, senza flag, e `QUERY_EDUNEWS24` in `config/routes/query.js`.
- Le icone dei marchi social sono SVG in `frontend/src/assets/edunews24/` usati come maschera CSS con `currentColor`: è un'eccezione scritta alla regola delle sole icone Lucide, e la regola ESLint non cambia.
- Contratti HTTP della pratica separati dalla mappatura ORM; regola di rinnovo centralizzata e verificata sotto il blocco della pratica.
- Invio email dopo il commit tramite `BackgroundTasks`, con errori registrati e senza ritentativi persistenti.

**Corretto**

- Il frontend invia i flag di rinnovo solo quando sono visibili per il percorso Lauree, conservando quelli storici degli altri percorsi.
- Test degli script di deploy eseguibili su Windows con Git Bash e percorsi normalizzati; fixture di overlay e firewall separate e condivise.

**Sicurezza**

- Collegamenti, immagini e video di ogni voce si validano nel backend (solo https sulla porta 443, host esattamente in elenco, niente credenziali né caratteri ambigui); le voci senza un collegamento valido si scartano, il player accetta solo MP4 e WebM, il corpo delle risposte ha un tetto sui byte decompressi e il browser carica i media solo dagli host di `EDUNEWS24_HOST_MEDIA`, che per impostazione predefinita contiene solo l'host dei media di EduNews24.
- Nel repository non c'è una Content Security Policy; se il reverse proxy esterno ne aggiunge una, `img-src` deve ammettere `'self'`, `data:` e gli host di `EDUNEWS24_HOST_MEDIA` in https, e `media-src` gli stessi host (dettagli in `docs/tecnica/deploy.md`).
- La porta HTTPS della rete EduNews24 vale per tutta l'API, quindi anche per il fornitore SMS: con `SMS_BACKEND=skebby` in `shared/api.env` e senza `NOTIFICHE_REALI=si` gli script di deploy non collegano la rete e avvisano, e il deploy toglie la copia dell'overlay in `shared/`, che solo un deploy successivo ricrea. Il controllo sta negli script, non nell'API, e riconosce la chiave `SMS_BACKEND` nelle forme che accetta Docker Compose (limiti in `docs/tecnica/sicurezza.md`).
- Letture correnti sotto blocco per stato, storico e visibilità della pratica, senza riutilizzare snapshot precedenti a una modifica concorrente.

## Versione 12 — 29/09/2026 09:32

<!-- timbro: versione=12 sha=a536652fc4463a38f886fd14c7fcd2d7747ee579 -->

### Novità e correzioni

**Aggiunto**

- Nella scheda della pratica si può consultare e utilizzare la conversazione condivisa con Universo, quando il collegamento è configurato.
- La firma della pratica si può disegnare con mouse, dito o penna e usare nei documenti generati successivamente.
- Codice automatico per le nuove pratiche SSML e A4U, con progressivi distinti per tipo di corso.

**Modificato**

- Le chat delle pratiche sono gestite dal backend della piattaforma, mantenendo lo storico condiviso con Universo.
- La creazione pratica propone studenti verificati e percorsi validi, con scelta multipla per i corsi singoli e relativo totale.

**Corretto**

- I tentativi ripetuti dopo un'interruzione della connessione non duplicano messaggi e notifiche.
- Negli elenchi Sottoscrittori e Attuatori gli indicatori di verifica dei contatti seguono la stessa regola della scheda, anche per gli account attivi precedenti al sistema OTP.
- Le finestre di selezione usano la gestione condivisa di focus ed Escape e si adattano all'altezza disponibile.
- Il totale dei corsi mantiene i decimali esatti; la nuova pratica collega il creatore anche ai permessi della conversazione.

**Sicurezza**

- Il salvataggio avvisa se la firma è stata modificata nel frattempo da un'altra finestra.

### Dettagli tecnici

**Aggiunto**

- Ponte FastAPI verso le API e il WebSocket Java esistenti, con sessione interna breve e controllo dei partecipanti alla pratica.
- Configurazione facoltativa CHAT_JAVA_URL, CHAT_JAVA_ORIGINE, CHAT_JAVA_SECRET_FILE e CHAT_DATASET; attivazione subordinata alla pubblicazione del delta Java e alla configurazione della rete privata.
- API dedicate per firma PNG con CSRF e versione ottimistica; riutilizzato il campo pratica_firma senza nuove migrazioni.
- **Incompatibile.** Migrazione additiva 017, grant storici, coda durevole, limite per utente e verifiche di revoca.
- **Incompatibile.** Blocco configurabile del vecchio writer Java per un passaggio senza due percorsi di inserimento attivi.
- DATABASE_URL_GESTIONE_PAGAMENTI e DATABASE_URL_SYS_ADMIN predispongono due connessioni facoltative, inizializzate solo al primo utilizzo e ancora prive di funzionalità collegate.
- **Incompatibile.** Servizio realtime FastAPI completo per sessioni, chat personali, pratiche, ticket pubblici e privati, notifiche, presenza, letture e recupero delle consegne.
- **Incompatibile.** Migrazione `018_realtime_completo.sql`, additiva e senza rollback distruttivo degli archivi condivisi; applicarla dopo la 017 e prima del backend aggiornato.
- **Incompatibile.** Configurazione `REALTIME_SCHEMA_TICKET`, `REALTIME_ACCESSO_SECONDI`, `REALTIME_REFRESH_GIORNI`, `REALTIME_PRODUCER_TOKEN_FILE` e `REALTIME_MANUTENZIONE_SECONDI`. API, WebSocket, invio e lavori periodici partono con il backend senza flag applicativi; schema e chiavi sono richiesti all'avvio, indipendentemente dall'integrazione di Universo.
- **Incompatibile.** Migrazione `019_realtime_consegne_connessioni.sql`, da applicare dopo la 018, per le conferme di consegna di ogni connessione. Una conferma non interrompe il recapito agli altri dispositivi attivi; chiusure e nuovi collegamenti aggiornano il quorum.
- **Incompatibile.** Migrazione `021_capienza_notifiche.sql` per il ciphertext nel corpo delle notifiche legacy; il rollback conserva la capienza per non perdere dati.

**Modificato**

- Nginx e proxy di sviluppo inoltrano l'upgrade WebSocket; il container API limita dimensione e coda dei frame.
- Indici della documentazione e specifiche storiche riordinati; chiarito il riuso del ramo personale e il ciclo di vita dei checkout temporanei.
- **Incompatibile.** Dominio FastAPI comune a sessione cookie e token Universo esistente; rimossi sessioni delegate e trasporto verso Java.
- **Incompatibile.** Attivazione coordinata tramite configurazione e delta Flutter; nessuna migrazione automatica tra dataset e nessun deploy implicito.
- Lo stato dei contatti mostrato nell'anagrafica è calcolato da una funzione condivisa; restano distinte le verifiche richieste per l'accesso e il secondo fattore.
- **Incompatibile.** Il namespace `/realtime` sostituisce `/chat-universo`; la scrittura delle pratiche con cookie riusa il medesimo dominio. L'integrazione del client e il passaggio dal servizio precedente richiedono un rilascio coordinato.
- **Incompatibile.** Integrato il commit `41665a5` di Login con chat, firma e realtime completo; la migrazione dei contatori diventa `020_contatori_codice_pratica.sql` per conservare la 017 della chat.
- **Incompatibile.** Lo staging del realtime richiede anche l'archivio ticket clonato sullo stesso MariaDB, il keyring storico e una configurazione privata completa. Il client Universo e il servizio Java restano indipendenti dal rilascio.

**Sicurezza**

- Le connessioni facoltative ignorano la configurazione ordinaria durante i test e accettano solo il database locale usa-e-getta. Gli errori di configurazione non espongono indirizzi o credenziali.
- **Incompatibile.** Sessioni revocabili, rotazione del refresh con rilevamento del riuso, ACL condivise, limiti persistenti e snapshot di lettura immutabili; cookie applicativi e token realtime restano distinti.
- **Incompatibile.** Ripresi limiti per tipo di comando, ammissione dei collegamenti, code limitate, invii serializzati, watchdog, rotazioni limitate e conservazione degli archivi. Validazione UTF-8/JSON e snapshot rigorosa; compatibilità crittografica e dei dati verificata con vettori Java sintetici.
- **Incompatibile.** Policy DB comune con pool e timeout limitati. In produzione `DATABASE_TRASPORTO=verify-full` richiede `DATABASE_CA_FILE`; l'eccezione `rete-privata` richiede IPv4 RFC1918 letterali. Predisporre la configurazione privata prima del rilascio: nessun fallback TLS silenzioso.
- **Incompatibile.** Overlay `compose.tls.yml` per la CA e i certificati del clone; `verify-full` verifica la connessione dell'API al database.

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
