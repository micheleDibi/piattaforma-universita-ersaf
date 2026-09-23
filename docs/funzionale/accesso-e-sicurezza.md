# Accesso e sicurezza

Questo documento descrive come si entra nella piattaforma, come si protegge l'accesso e come si recupera la password. Chi può entrare e con quali permessi è spiegato in [Ruoli e permessi](ruoli-e-permessi.md).

## Entrare nella piattaforma

La pagina "Accedi all'area riservata" chiede **Nome utente** e **Password**. Il pulsante è "Accedi". Sotto c'è il collegamento "Hai dimenticato la password?".

Se l'accesso non riesce, il messaggio è sempre lo stesso: **"Username o password errati"**. Compare quando:

- nome utente o password sono sbagliati;
- l'account è disattivato;
- lo stesso nome utente appartiene a più account;
- la persona non ha un'anagrafica;
- il ruolo non permette l'accesso (Utente, Consulente, Operatore).

Il messaggio non dice quale sia il motivo: è una scelta voluta, per non dare indizi a chi prova ad indovinare.

Dopo l'accesso si arriva all'elenco dei Sottoscrittori. Chi rientra dopo una sessione scaduta torna invece alla pagina che aveva aperto.

Chi ha già una sessione valida e apre la pagina di accesso entra direttamente, senza rivedere il modulo.

### Troppi tentativi

Con la configurazione predefinita valgono queste regole:

- i tentativi si contano per **nome utente** e per **indirizzo di rete**, in una finestra di 15 minuti dal primo tentativo;
- dal quinto tentativo sullo stesso nome utente scatta un'attesa prima del successivo: 1 secondo, poi 2, 4, 8 e così via, fino a un massimo di 60 secondi;
- per lo stesso indirizzo di rete l'attesa scatta dal cinquantesimo tentativo;
- trascorsa la finestra, i conteggi ripartono da zero;
- un accesso riuscito azzera il conteggio del nome utente, non quello dell'indirizzo di rete.

Il messaggio dell'attesa non compare subito dopo il tentativo che la fa scattare: quel tentativo mostra ancora "Username o password errati". Se si riprova prima che l'attesa sia finita, la pagina mostra "Troppi tentativi di accesso. Attendi prima di riprovare." e un conto alla rovescia, "Puoi riprovare tra N s.". Il pulsante "Accedi" resta disattivato. Alla fine compare "Ora puoi riprovare ad accedere.".

## Il secondo fattore del Nazionale

Il Nazionale, dopo la password corretta, non entra subito: deve confermare l'accesso con un secondo fattore. Gli altri ruoli non lo usano.

### I metodi

I metodi sono tre. Il sistema propone il primo disponibile, in quest'ordine:

1. **passkey sul telefono**;
2. **app di autenticazione**;
3. **codice via email**, che vale come metodo solo se l'email in anagrafica è verificata.

Sotto il metodo proposto c'è il collegamento **"Usa un altro metodo"**. Mostra gli altri metodi che la persona possiede, e permette di sceglierne uno. Se la persona ha un solo metodo, il collegamento non compare.

Il collegamento "Indietro" riporta al modulo con nome utente e password.

### Codice via email

La pagina "Verifica il tuo accesso" indica a quale indirizzo è partito il codice, in parte nascosto.

- Il codice ha **6 cifre** ed è valido **10 minuti**.
- Si può sbagliare al massimo **5 volte**. Poi serve un nuovo codice.
- Il pulsante "Invia un nuovo codice" si attiva dopo **60 secondi**; nel frattempo mostra "Reinvia tra N s".
- Ogni nuovo codice annulla il precedente.
- Si possono ricevere al massimo 5 codici all'ora. Conta anche il codice spedito a ogni nuovo accesso.
- Passati i 10 minuti bisogna ripetere l'accesso dall'inizio.

In alcuni casi il codice non parte affatto: se si ripete l'accesso prima che siano passati 60 secondi dall'ultimo codice, per esempio dopo aver premuto "Indietro"; se si è già oltre il quinto codice dell'ora; se dalla stessa rete si è superato il tetto di 30 codici all'ora. In tutti questi casi la pagina di accesso mostra "Troppi tentativi di accesso. Attendi prima di riprovare." con il conto alla rovescia.

Nota: il messaggio parla di tentativi di accesso, mentre il motivo è il limite sull'invio dei codici, e il server dà un messaggio diverso; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### App di autenticazione

La pagina chiede il codice mostrato dall'app sul telefono.

- Il codice ha 6 cifre e cambia ogni 30 secondi. Viene accettato anche quello immediatamente precedente o successivo, per piccole differenze di orario fra telefono e server.
- Un codice già usato non vale una seconda volta.
- La verifica va completata entro **5 minuti**, con al massimo 5 errori. Poi bisogna ripetere l'accesso.
- Non c'è un pulsante di reinvio: il codice lo produce il telefono.

### Passkey sul telefono

Dopo la password il browser chiede subito il telefono: mostra un codice da inquadrare, oppure una notifica se il telefono è già collegato. Si conferma sul telefono con impronta, volto o PIN.

- Se Windows propone una chiave USB, si preme "Cambia" e si sceglie il telefono.
- Il pulsante "Riprova con il telefono" ripete la richiesta.
- La verifica va completata entro **5 minuti**, con al massimo 5 errori.
- Se il browser non supporta le passkey, la pagina lo dice e invita a scegliere un altro metodo.

### Primo accesso senza metodi

Un Nazionale che non ha ancora nessun metodo vede la pagina **"Verifica la tua email"**. Il codice arriva all'email in anagrafica, con le stesse regole del codice via email.

Confermando il codice, l'email risulta verificata e la persona entra. Dagli accessi successivi il metodo proposto è il codice via email, finché non ne aggiunge altri dal profilo.

Se in anagrafica non c'è un'email valida, compare **"Per accedere serve un'email valida in anagrafica: rivolgiti a un amministratore."**. Serve che un amministratore inserisca un'email valida nella scheda della persona.

Nota: una persona già attiva prima dell'introduzione della verifica, oppure il cui indirizzo email è stato cambiato dopo l'attivazione, può avere nella sua scheda l'email indicata come "Verificata" anche se la verifica non risulta registrata; per il secondo fattore quell'email non conta; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Gestire i metodi dal profilo

I metodi si gestiscono da "Il mio profilo", scheda **"Sicurezza"**. La scheda esiste solo per il Nazionale.

In alto la pagina dice quale metodo verrà chiesto al prossimo accesso. Se non ce n'è nessuno, avvisa che verrà chiesta la verifica dell'email.

| Operazione | Cosa serve |
|---|---|
| Aggiungere una passkey | Un nome (fino a 80 caratteri; viene proposto "Il mio telefono") e la password. Poi il browser chiede il telefono: servono Bluetooth acceso su computer e telefono e la connessione a internet. |
| Rimuovere una passkey | Solo la password, perché il telefono potrebbe non essere più disponibile. |
| Attivare l'app di autenticazione | La password. Poi compare un codice QR da inquadrare con l'app, oppure una chiave da inserire a mano. Infine il codice mostrato dall'app e "Conferma e attiva". |
| Disattivare l'app di autenticazione | La password e un codice corrente dell'app. |
| Codice via email | Non si attiva da qui: l'email si verifica all'accesso solo quando non c'è nessun altro metodo. |

Nota: la scheda scrive che l'email non ancora verificata "la verifichi al prossimo accesso" anche quando questo non succede, perché all'accesso l'email si verifica solo in assenza di altri metodi; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Altre regole:

- Per ogni passkey l'elenco mostra il nome, la data in cui è stata aggiunta e l'ultimo uso. L'etichetta "Sincronizzata" indica che la passkey è disponibile anche sugli altri dispositivi dello stesso account del telefono.
- Se il telefono non risponde, "Riprova con il telefono" ripete la richiesta senza chiedere di nuovo la password, entro 5 minuti.
- Una passkey già registrata non si aggiunge due volte: compare "Questa passkey è già registrata.".
- Un'app di autenticazione già attiva va disattivata prima di registrarne un'altra.
- Un'attivazione dell'app avviata e non completata compare come "Attivazione da completare" e viene annullata dopo un giorno.
- Con una password sbagliata compare "Password non corretta.". Dopo alcuni errori bisogna attendere prima di riprovare, come all'accesso.

Due testi della scheda promettono un metodo che non sempre è quello che verrà chiesto:

- la finestra di disattivazione dell'app, prima di premere "Disattiva l'app", dice che dal prossimo accesso verrà chiesto il codice via email. Dopo la disattivazione il messaggio è solo "App di autenticazione disattivata.", e al prossimo accesso viene proposto il primo metodo rimasto, nell'ordine descritto sopra; se non ne resta nessuno, viene chiesta la verifica dell'email;
- il messaggio che segue l'attivazione dell'app dice che dal prossimo accesso verrà chiesto il suo codice. Non vale se c'è anche una passkey: in quel caso viene proposta la passkey.

Nota: questi testi dell'interfaccia non corrispondono sempre a ciò che fa il server; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Non esiste una funzione con cui un amministratore azzera i metodi di un'altra persona. Chi perde il telefono può entrare solo con il codice via email, e solo se la sua email è verificata.

Nota: se l'email non è verificata, non esiste una procedura prevista per rientrare; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## La sessione

Dopo l'accesso la piattaforma ricorda la persona collegata: è la **sessione**.

Con la configurazione predefinita:

- la sessione resta valida finché la si usa;
- scade dopo **14 giorni** senza attività;
- scade comunque **90 giorni** dopo l'accesso, anche se usata ogni giorno.

Chiudere il browser non chiude la sessione. Su un computer condiviso bisogna usare "Esci".

### Quando scade

Alla prima azione dopo la scadenza, la piattaforma porta alla pagina di accesso con il messaggio "La sessione è scaduta o non è più valida. Accedi di nuovo per riprendere dalla pagina che avevi aperto.". I dati non salvati della pagina vanno persi.

Dopo il nuovo accesso si torna alla pagina che era aperta, se si rientra dalla stessa scheda del browser.

### Quando termina prima

La sessione termina anche quando:

- si usa "Esci";
- la password viene cambiata con il recupero: si chiudono le sessioni su tutti i dispositivi;
- l'account viene disattivato;
- dallo stesso browser si accede di nuovo, anche come un altro utente.

Ogni dispositivo ha la sua sessione: accedere da un altro computer non chiude quella già aperta.

Le schede dello stesso browser condividono la sessione. Se in una scheda si accede di nuovo, le altre schede già aperte mostrano "La sessione è cambiata. Ricarica la pagina prima di riprovare." al primo salvataggio.

## Uscire

Il pulsante **"Esci"** sta in fondo al menu. Chiude la sessione sul server e riporta alla pagina di accesso.

Se il server non conferma l'uscita, compare "Uscita non riuscita. Riprova." e si resta dentro.

## Recuperare la password

Il recupero funziona solo per gli attuatori: Aderente, Provinciale, Regionale e Nazionale.

### 1. La richiesta

Dal collegamento "Hai dimenticato la password?" si apre "Recupera la password". Si inserisce l'**indirizzo email** e si preme "Invia il link di recupero".

La risposta è sempre la stessa: **"Se l'indirizzo è associato a un account riceverai una mail"**. Compare anche se l'indirizzo non esiste, e anche se la connessione non funziona. Il modulo poi resta bloccato su "Richiesta inviata": per una nuova richiesta si ricarica la pagina.

### 2. Chi riceve davvero la mail

La mail parte solo se:

- l'indirizzo appartiene a un attuatore con account attivo;
- nessun altro attuatore attivo usa lo stesso indirizzo;
- non si è superato il limite di richieste: con la configurazione predefinita, 5 all'ora per lo stesso indirizzo email e 5 all'ora dalla stessa rete.

Negli altri casi non parte nulla, ma il messaggio a video non cambia. Un sottoscrittore, un Consulente o un Operatore non riceve mai la mail.

Nota: il messaggio a video è uguale anche quando la mail non parte, per non rivelare quali indirizzi sono registrati; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### 3. Il link

- Con la configurazione predefinita il link è valido **60 minuti**.
- Si usa **una sola volta**.
- Una nuova richiesta annulla i link precedenti.

Aprendo il link compare "Verifica del link in corso…". Se il link non vale più, la pagina "Link non disponibile" spiega il motivo e offre "Richiedi un nuovo link":

| Messaggio | Significato |
|---|---|
| "Il link è scaduto: era valido per 60 minuti dalla richiesta." | Il tempo è passato. |
| "Questo link è già stato usato: la password è già stata cambiata." | Il link è già servito. |
| "Il link non è valido. Può essere stato copiato male, oppure una richiesta più recente lo ha sostituito." | Link incompleto, oppure annullato da una richiesta più recente. |
| "Non è stato possibile verificare il link. Controlla la connessione e riapri il link dalla mail." | Problema di rete. |

Il link sparisce dalla barra degli indirizzi appena la pagina si apre. Se si ricarica la pagina, il link risulta non valido: va riaperto dalla mail.

Nota: la pagina scrive sempre "60 minuti", anche se la durata sul server è configurabile; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### 4. La nuova password

Si scrive la nuova password in "Nuova password" e di nuovo in "Conferma la password". La pagina mostra i requisiti man mano e un indicatore di robustezza, solo orientativo. Il pulsante "Salva la nuova password" si attiva quando i requisiti sono soddisfatti e le due password coincidono.

La nuova password:

- deve avere almeno **8 caratteri**, con la configurazione predefinita;
- non può superare 72 byte: le lettere accentate valgono due;
- non può coincidere con il nome utente;
- non può coincidere con l'indirizzo email, né con la sua parte che precede la chiocciola;
- non può essere troppo comune o prevedibile: per esempio una password che, tolti numeri e simboli, è solo "password" o "ersaf", oppure fatta di un solo carattere ripetuto. Una parola vietata dentro una password più lunga non basta a farla rifiutare.

Non servono maiuscole, cifre o simboli. La password non scade.

Nota: l'interfaccia controlla sempre un minimo di 8 caratteri, mentre il minimo sul server è configurabile; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### 5. Dopo il cambio

- Si torna alla pagina di accesso con il messaggio "Password aggiornata. Accedi con le nuove credenziali.". Non si entra automaticamente.
- Tutte le sessioni aperte dell'account si chiudono, su ogni dispositivo.
- Gli altri link di recupero ancora validi vengono annullati.
- Una mail di conferma arriva all'indirizzo a cui era stato mandato il link.
- Il Nazionale, al nuovo accesso, ripete anche il secondo fattore.

## Verifica di email e cellulare

La verifica conferma che email e cellulare di una persona sono davvero suoi. Riguarda la scheda di una persona, non l'accesso. Il flusso completo, le regole del codice e cosa accade quando un contatto cambia sono descritti in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

Quello che conta per questo documento è un solo punto: per il Nazionale l'email verificata vale anche come metodo del secondo fattore. Se l'email cambia, la verifica decade e quel metodo viene a mancare, anche se la scheda continua a mostrare "Verificata".

Nota: la scheda mostra come verificato un contatto che il server non considera verificato; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Nell'ambiente di collaudo email e SMS possono essere registrati sul server invece che spediti, secondo come è configurato. In quel caso codici e link vanno chiesti a chi gestisce il collaudo. Vedi [Deploy](../tecnica/deploy.md).

## Il mio profilo

Il profilo si apre dal proprio nome in fondo al menu. Su uno schermo piccolo si apre anche dall'icona in alto a destra.

| Scheda | Contenuto |
|---|---|
| Dati principali | Informazioni personali (nome, cognome, codice fiscale, cittadinanza), contatti (email, PEC, telefono, cellulare), residenza e domicilio (indirizzo, numero civico, comune, CAP, provincia). |
| Utente | Nome utente, ruolo e, se c'è, azienda. |
| Sicurezza | Solo per il Nazionale: i metodi del secondo fattore, descritti sopra. |

- I campi vuoti mostrano "Non indicato".
- Il profilo è **in sola lettura**: da qui non si modificano i dati.
- La password non si cambia dal profilo. L'unico modo è il recupero della password descritto sopra.

## Messaggi principali

| Messaggio | Quando compare |
|---|---|
| "Username o password errati" | Accesso non riuscito, per uno qualunque dei motivi elencati all'inizio. |
| "Troppi tentativi di accesso. Attendi prima di riprovare." | Troppi tentativi di accesso; segue il conto alla rovescia. |
| "Troppi tentativi. Riprova tra N secondi." | Troppe richieste altrove, per esempio troppi codici chiesti o troppe password sbagliate nel profilo. |
| "Per accedere serve un'email valida in anagrafica: rivolgiti a un amministratore." | Un Nazionale senza metodi e senza un'email valida in anagrafica. |
| "Codice non valido o scaduto. Richiedine uno nuovo." | Codice via email sbagliato o con i tentativi esauriti. All'accesso un codice scaduto dà invece "Verifica scaduta. Ripeti l'accesso.", perché il tempo si controlla prima del codice; la parola "scaduto" riguarda la verifica dei contatti. |
| "Codice non valido. Riprova." | Codice dell'app sbagliato, oppure risposta della passkey non accettata al momento dell'accesso. |
| "Verifica scaduta. Ripeti l'accesso." | Il tempo per il secondo fattore è finito. |
| "Verifica non valida. Ripeti l'accesso." oppure "Verifica non valida o scaduta. Ripeti l'accesso." | La verifica in corso non è più utilizzabile, per esempio dopo troppi errori. Si ricomincia dal nome utente. |
| "Operazione annullata o non completata sul telefono. Riprova." | La passkey non è stata confermata sul telefono. |
| "Il sito non corrisponde a quello per cui la passkey è stata creata." | Il browser ha rifiutato la passkey perché l'indirizzo del sito non corrisponde. |
| "Verifica della passkey non riuscita. Riprova." | Nel profilo, la nuova passkey non è stata accettata. |
| "Codice non valido: controlla l'ora del telefono e riprova." | Nel profilo, codice dell'app sbagliato durante l'attivazione o la disattivazione. |
| "Password non corretta." | Nel profilo, password sbagliata. |
| "La sessione è scaduta o non è più valida. Accedi di nuovo per riprendere dalla pagina che avevi aperto." | Sessione scaduta o chiusa. |
| "La sessione è cambiata. Ricarica la pagina prima di riprovare." | In un'altra scheda dello stesso browser si è acceduto di nuovo. |
| "Non hai i permessi per questa operazione." | Accesso come altro utente tentato da chi non è Regionale o Nazionale. |
| "Non hai i permessi per modificare un altro utente." | Salvataggio della scheda "Utente" di un'altra persona da parte di chi non è Regionale o Nazionale. |
| "Solo il nazionale può eseguire questa operazione." | Operazione riservata al Nazionale. |
| "Il ruolo Nazionale richiede la verifica a due fattori." | Tentativo di accedere come un Nazionale. |
| "Utente non trovato o non impersonabile." | La persona scelta non può essere usata per l'accesso come altro utente. |
| "Uscita non riuscita. Riprova." | Il server non ha confermato l'uscita. |
| "Connessione non riuscita. Controlla la rete e riprova." | Il browser non raggiunge il server. |
| "Connessione non riuscita. Riprova." | Il browser non raggiunge il server durante il salvataggio della nuova password. |
| "Servizio temporaneamente non disponibile. Riprova tra poco." | Errore del server, compreso un invio di codice non riuscito: in quel caso si può riprovare dopo 60 secondi. |
| "Se l'indirizzo è associato a un account riceverai una mail" | Sempre, dopo una richiesta di recupero password. |
| "Le password non coincidono." | Nel recupero, la conferma è diversa dalla nuova password; il salvataggio resta disattivato. |
| "Il link non e' piu' valido. Richiedine uno nuovo." | Nel recupero, il link è scaduto o già usato al momento del salvataggio. |
| "Password aggiornata. Accedi con le nuove credenziali." | Recupero completato. |

Nota: per un invio di codice non riuscito o per troppe richieste il server dà un messaggio specifico, ma l'interfaccia mostra uno dei due messaggi generici qui sopra; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).
