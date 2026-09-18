# Sicurezza

Questo documento descrive il modello di sicurezza della piattaforma. Spiega come si autentica un utente e come il server protegge le richieste. Spiega anche come tratta password, codici monouso e segreti.

Serve a chi sviluppa, a chi rivede il codice e a chi prepara un rilascio. Descrive il codice del ramo principale.

In fondo ci sono due parti:
- i rilievi dell'analisi del 2026, con lo stato attuale;
- la sezione [Limiti noti](#limiti-noti), l'unico posto che elenca i contrasti fra interfaccia e server.

Altri riferimenti:
- elenco delle API: [riferimenti/api.md](riferimenti/api.md);
- variabili di configurazione: [riferimenti/configurazione.md](riferimenti/configurazione.md);
- flusso visto dall'utente: [accesso-e-sicurezza.md](../funzionale/accesso-e-sicurezza.md).

## Sessione

### Trasporto

- La sessione viaggia solo in un cookie `HttpOnly` (`backend/src/security/browser.py:35-43`).
- Il nome del cookie è `__Host-ersaf_sessione` quando l'ambiente è di produzione o l'indirizzo del frontend è HTTPS (`browser.py:16-22`). Negli altri casi è `ersaf_sessione`.
- Con il nome `__Host-` il cookie è anche `Secure`.
- Gli altri attributi sono `SameSite=Lax`, `Path=/` e un `Max-Age` pari alla finestra di inattività (`browser.py:38-42`).
- Il token non compare mai nel JSON. Il login e `GET /auth/session` restituiscono i dati dell'utente e il token CSRF (`backend/src/auth/accesso.py:40-49`, `90-95`).
- Nel browser i dati della sessione e il token CSRF stanno solo in memoria (`frontend/src/lib/sessione.js:1-2`). Dopo un ricaricamento della pagina il frontend li chiede di nuovo a `GET /auth/session` (`frontend/src/lib/api.js:22-34`).

### Nessun token Bearer

L'intestazione `Authorization` non è un trasporto accettato: il server legge il token solo dal cookie (`browser.py:25-27`). Un test lo verifica: un token valido inviato come Bearer, senza cookie, riceve 401 (`backend/tests/security/test_cookie_csrf.py:64-68`).

### Token e impronta

- Il token è opaco: 32 byte casuali, 43 caratteri (`backend/src/security/tokens.py:32-49`).
- Nel database c'è solo lo SHA-256 del token concatenato a `SESSION_TOKEN_PEPPER` (`tokens.py:70-77`; `backend/src/security/sessioni.py:59-62`). Chi legge un backup non ricava i token.
- Un valore con una forma diversa viene scartato prima di interrogare il database (`tokens.py:80-86`; `sessioni.py:83-84`).

### Validità e scadenza scorrevole

Il codice cita questa decisione come "ADR 0008", ma il documento non è nel repository (`sessioni.py:11`; `browser.py:37`).

- Una sessione è valida se rispetta tutte queste condizioni (`sessioni.py:74-102`):
  - non è revocata;
  - non è scaduta;
  - è nata entro il tetto assoluto;
  - l'utente è attivo;
  - è nata dopo l'ultimo cambio password.
- Con la configurazione predefinita la finestra di inattività è di 14 giorni e il tetto assoluto è di 90 (`backend/src/config.py:91-92`).
- Ogni richiesta autenticata sposta avanti la scadenza, al massimo una volta ogni 5 minuti (`sessioni.py:48`, `105-128`).
- Quando il server sposta la scadenza, rimanda anche il cookie con il `Max-Age` pieno (`backend/src/auth/dipendenze.py:53-56`).
- Ogni errore di sessione risponde 401 con lo stesso messaggio, qualunque sia la causa (`dipendenze.py:36-50`).

### Revoca

- Al login il server revoca la sessione già presente nel cookie, poi ne crea una nuova (`auth/accesso.py:52-60`).
- L'impersonificazione passa dalla stessa funzione, quindi revoca la sessione di chi impersona (`backend/src/auth/routers.py:304`).
- Il logout revoca la sessione e cancella il cookie (`auth/accesso.py:98-108`). Risponde 204 anche con un token inesistente o già revocato, così non dice se quel token è esistito. Se la sessione è ancora valida verifica prima il CSRF e, se manca o non coincide, risponde 403 (`browser.py:72-80`).
- La conferma del recupero password revoca tutte le sessioni dell'utente (`backend/src/auth/servizio_reset.py:393-394`).
- Se una revoca non avvenisse, la condizione sull'ultimo cambio password scarterebbe comunque le sessioni più vecchie (`sessioni.py:77-81`, `96-99`).

## Protezione delle richieste dal browser

### Middleware

Un middleware controlla ogni richiesta con un metodo diverso da GET, HEAD e OPTIONS, anche senza sessione (`backend/src/main.py:96-105`; `browser.py:56-69`). I controlli sono tre:
- l'intestazione `Origin`, se presente, deve essere l'origine di `FRONTEND_BASE_URL` o una di `CORS_ORIGINS`;
- l'intestazione `X-ERSAF-Request: 1` è obbligatoria, e una pagina estranea può inviarla solo superando il preflight CORS;
- `Sec-Fetch-Site: cross-site` con un'origine non ammessa è rifiutato.

Se un controllo fallisce, la risposta è 403.

Il frontend aggiunge `X-ERSAF-Request` a ogni chiamata e invia i cookie con `credentials: "include"` (`frontend/src/lib/api.js:10`, `39`).

### CSRF

- Il token CSRF è un HMAC-SHA256 del token di sessione, con chiave `SESSION_TOKEN_PEPPER` (`browser.py:30-32`). Non autentica: lega la scrittura alla sessione.
- Ogni scrittura autenticata deve inviarlo in `X-CSRF-Token`, e il server lo confronta a tempo costante (`browser.py:72-80`; `dipendenze.py:52`).
- Se il token manca o non coincide, la risposta è 403 con `codice: csrf_non_valido`.
- Il frontend lo aggiunge a ogni scrittura (`api.js:40-43`).

### Cache

- Il middleware imposta `Cache-Control: no-store` in questi casi (`main.py:103-104`):
  - le risposte sotto `/auth/` e `/profilo/`;
  - i percorsi dei contatti;
  - ogni risposta 401, 403 o 429.
- Lo stesso vale quando il server imposta o cancella il cookie (`browser.py:43`, `48`).
- Vale anche per il PDF delle pratiche (`backend/src/documenti/rotte.py:76-83`).

### CORS

- Le origini ammesse vengono da `CORS_ORIGINS` e le credenziali sono ammesse (`main.py:86-93`).
- `Retry-After` è esposta al browser.
- Lo stato di questo punto è nella tabella dei rilievi, alla voce S7.

## Password

### Hash

- Il codice usa bcrypt direttamente, senza librerie intermedie (`backend/src/security/password.py:1-7`).
- Il costo viene da `BCRYPT_COST`, 12 con la configurazione predefinita (`config.py:101`). L'avvio rifiuta valori fuori dall'intervallo 4-16 (`config.py:223-224`).
- La password viene normalizzata in NFKC sia prima dell'hash sia prima della verifica (`password.py:91-99`).
- Una password oltre i 72 byte viene rifiutata, non troncata (`password.py:9-21`, `102-108`).
- La verifica non solleva mai eccezioni: oltre il limite restituisce falso (`password.py:111-128`).
- Con un utente inesistente o disattivato il server esegue comunque un bcrypt su un hash fittizio, con lo stesso costo (`password.py:139-156`; `backend/src/auth/servizio_login.py:85-113`). Così il tempo di risposta non distingue i casi.
- Una funzione segnala gli hash con un costo inferiore a quello configurato, ma il login non la usa (`password.py:131-136`; `servizio_login.py:96-97`). Quindi alzare il costo non cambia gli hash già scritti.

### Conversione pigra e colonna legacy

- La tabella degli utenti conserva la colonna della password in chiaro della piattaforma precedente (`backend/src/utenti/models.py:20`).
- È un debito aperto. Le regole operative sono in [db/README.md](../../db/README.md).
- Al primo login riuscito di un utente legacy il server converte la sua riga: scrive l'hash bcrypt e svuota la colonna in chiaro (`servizio_login.py:48-82`, `114-116`).
- La conversione riguarda una riga per volta e filtra sulla chiave primaria.
- La conversione non tocca la data dell'ultimo cambio password, che decide la validità delle sessioni (`servizio_login.py:51-63`).
- Una colonna in chiaro vuota non autentica mai (`servizio_login.py:99-106`).
- Il confronto con il valore legacy avviene a tempo costante (`servizio_login.py:108-110`).
- Le nuove anagrafiche nascono con l'hash di un valore casuale (`backend/src/clienti/servizio.py:147-174`).
- La password vera nasce all'attivazione e non viene mai salvata in chiaro (`clienti/servizio.py:177-188`).

### Regole

Le regole si applicano alla conferma del recupero password e alla creazione diretta di un utente (`auth/routers.py:163-179`; `backend/src/utenti/routers.py:68-79`):
- lunghezza minima da `PASSWORD_MIN_LENGTH`, 8 con la configurazione predefinita; l'avvio rifiuta valori inferiori a 8 (`config.py:102`, `225-232`);
- al massimo 72 byte;
- diversa dallo username e dall'email, anche dalla sola parte prima della chiocciola;
- non troppo comune: il controllo usa un elenco esatto, un elenco di radici vietate e rifiuta le password fatte di un solo carattere (`password.py:43-88`, `164-200`). L'elenco esatto contiene solo voci lunghe, da 12 caratteri in su, e il confronto con le radici vietate guarda le sole lettere: vedi [Limiti noti](#limiti-noti).

Le regole non impongono una composizione né una scadenza periodica (`password.py:43-44`).

### Regole duplicate nel frontend

- L'interfaccia ha una copia delle stesse regole, per mostrarle mentre l'utente scrive (`frontend/src/lib/passwordPolicy.js`).
- La copia è voluta: un endpoint pubblico esporrebbe l'elenco delle password vietate (`backend/tests/unit/test_policy_allineata.py:1-12`).
- Un test sorveglia l'allineamento (`test_policy_allineata.py:54-69`, `124`):
  - confronta le costanti;
  - se `node` è disponibile, esegue il modulo JavaScript e confronta gli esiti.
- Nel browser la regola "diversa da username ed email" non si può verificare, perché il client non sa a chi appartiene il link. La pagina la indica come verificata al salvataggio (`frontend/src/config/testi/accesso.js:52-53`).

### Nessuna riscrittura massiva

- Il codice può scrivere nella colonna in chiaro solo in punti elencati. Un test esamina i sorgenti e fallisce se ne compare un altro (`backend/tests/security/test_nessun_plaintext.py:169-185`).
- Un secondo test fallisce se codice, script o migrazioni contengono un aggiornamento delle password senza filtro sull'utente (`test_nessun_plaintext.py:189-212`).

## Recupero password

### Richiesta

- `POST /auth/password-reset/request` risponde sempre 200, con un corpo serializzato una volta sola (`auth/routers.py:73-121`; `backend/src/auth/schemas.py:29-36`).
- Il campo email è una stringa semplice (`auth/schemas.py:15-20`). Un indirizzo malformato non produce un errore di validazione: il server lo tratta come sconosciuto (`servizio_reset.py:180`, `192-193`).
- La risposta ha una durata minima, così il tempo non dipende dal ramo eseguito (`config.py:79-83`; `backend/src/security/tempo.py:78-110`). La durata è `PASSWORD_RESET_BUDGET_MS`, 900 ms con la configurazione predefinita.
- L'attesa sta in un `finally` e non occupa thread, per questo la rotta è `async` (`auth/routers.py:86-91`).
- Un'eccezione interna non produce un 500: il server registra l'esito in una sessione separata e risponde come sempre (`auth/routers.py:98-110`).
- La mail parte in background, dopo il commit (`auth/routers.py:112-115`).

### Limiti e ordine delle operazioni

- Il limite orario vale per IP e per impronta dell'indirizzo (`config.py:78`; `servizio_reset.py:184-191`). È `PASSWORD_RESET_RATE_LIMIT_PER_HOUR`, 5 con la configurazione predefinita.
- L'impronta dell'indirizzo usa `PASSWORD_RESET_TOKEN_PEPPER` (`servizio_reset.py:181-182`).
- Il limite si applica prima di cercare l'indirizzo (`servizio_reset.py:163-208`).
- Ogni richiesta lascia una riga di audit. La riga indica l'utente solo quando la mail parte.
- Conteggio e inserimento non sono atomici: richieste simultanee possono superare il limite di poco. È una scelta dichiarata nel codice (`servizio_reset.py:69-72`).

### Destinatari ammessi

La mail parte solo se tutte queste condizioni valgono (`servizio_reset.py:125-160`; `backend/src/auth/models.py:58-61`):
- fra le anagrafiche con quell'indirizzo c'è almeno un utente con ruolo attuatore (Aderente, Regionale, Provinciale, Nazionale);
- fra questi, gli utenti attivi sono esattamente uno;
- l'indirizzo ha una forma valida.

Le anagrafiche senza ruolo attuatore con lo stesso indirizzo non contano.

Negli altri casi la risposta non cambia e la mail non parte.

### Token

- Il token è opaco, da 32 byte. Nel database c'è solo la sua impronta con `PASSWORD_RESET_TOKEN_PEPPER` (`servizio_reset.py:228-241`).
- Dura `PASSWORD_RESET_TOKEN_TTL_MINUTES`, 60 minuti con la configurazione predefinita (`config.py:77`).
- Una nuova richiesta revoca i token precedenti, nella stessa transazione (`servizio_reset.py:211-226`).
- Il link si costruisce da `FRONTEND_BASE_URL`, mai dall'intestazione `Host` (`backend/src/notifiche/email.py:63-68`).
- `GET /auth/password-reset/validate` è in sola lettura, quindi l'anteprima di un client di posta non consuma il token (`auth/routers.py:124-131`).
- La validazione distingue link scaduto, già usato e non valido. Un token revocato risulta non valido (`servizio_reset.py:285-321`).

### Conferma

- Il server verifica le regole della password prima di consumare il token, con username ed email del proprietario (`auth/routers.py:163-179`).
- bcrypt si calcola fuori dalla transazione (`auth/routers.py:181-184`).
- Il consumo del token è atomico (`servizio_reset.py:324-351`). Le condizioni di stato stanno nella `WHERE`, perché il driver conta le righe trovate e non quelle modificate.
- Una sola transazione applica la nuova password, revoca gli altri token e revoca tutte le sessioni (`servizio_reset.py:354-394`).
- L'utente non viene autenticato: la risposta lo rimanda al login (`auth/routers.py:228-231`).
- Una mail di conferma va all'indirizzo a cui era stato spedito il link (`auth/routers.py:216-226`).

### Token nell'indirizzo

Il token arriva nella query string del link. Le difese sono tre:
- il frontend lo legge una sola volta e lo toglie subito dall'indirizzo (`frontend/src/lib/resetToken.js:19-46`);
- la politica del referrer è `no-referrer`:
  - nella pagina, con un tag `meta` che precede ogni sottorisorsa (`frontend/index.html:20`);
  - nel server web, con un'intestazione (`frontend/nginx.conf:28`);
- il server web registra gli accessi senza query string (`nginx.conf:6`, `22`), e il log di uvicorn passa dalla redazione descritta nella sezione Log.

Oggi il token non sta nel frammento dell'indirizzo. Nel frammento resterebbe fuori da ogni richiesta.

## Limiti dei tentativi

### Login

- Il server prenota il tentativo prima di verificare la password, sia per IP sia per account (`auth/accesso.py:65`; `backend/src/auth/limiti_login.py:83-110`).
- Le chiavi sono HMAC con `SESSION_TOKEN_PEPPER` (`limiti_login.py:36-55`).
- La chiave dell'account usa lo username normalizzato e ricondotto alla forma registrata, così tutte le varianti condividono il contatore.
- La prenotazione è atomica anche fra processi (`limiti_login.py:58-63`, `88-107`):
  - la riga resta bloccata con `SELECT ... FOR UPDATE`;
  - il server blocca sempre prima l'IP, poi l'account;
  - l'ora viene dall'orologio del database.
- Il blocco finisce prima del bcrypt.
- Con la configurazione predefinita la finestra è di 900 secondi e l'attesa massima è di 60 secondi (`config.py:95-98`).
- Con la configurazione predefinita la soglia è di 5 tentativi per account e di 50 per IP.
- Dalla soglia in poi l'attesa raddoppia a ogni tentativo, fino al massimo (`limiti_login.py:76-80`).
- Allo scadere della finestra i contatori ripartono (`limiti_login.py:66-73`).
- Durante l'attesa la risposta è 429 con `Retry-After` (`limiti_login.py:108-109`).
- Un login riuscito azzera il contatore dell'account, non quello dell'IP (`limiti_login.py:113-121`; `auth/accesso.py:81`, `85`).
- Per il Nazionale l'azzeramento avviene dopo la password, prima del secondo fattore (`auth/accesso.py:80-81`).

### Invio dei codici

I limiti per ogni invio di un codice via email o SMS sono tre (`backend/src/otp/limiti.py:9-27`):
- per anagrafica e tipo di contatto, 5 invii all'ora, con almeno 60 secondi fra un invio e il successivo: il contatore è legato all'anagrafica, non al recapito (`otp/limiti.py:11`; `backend/src/otp/servizio.py:31`);
- per IP, 30 invii all'ora;
- per chi chiede l'invio, 30 invii all'ora.

Oltre il limite la risposta è 429 con `Retry-After`.

Se l'invio fallisce, il server marca la sfida come fallita e risponde 503 (`backend/src/otp/invio.py:30-34`).

### Sfide

- Una sfida con codice (email o SMS) dura 10 minuti e ammette 5 tentativi (`backend/src/otp/servizio.py:11-12`, `52-73`).
- Ogni errore consuma un tentativo, con un commit immediato.
- Le sfide dei metodi da app (authenticator e passkey) durano 300 secondi e ammettono 5 tentativi (`otp/servizio.py:81-119`).
- Queste sfide non hanno limiti d'invio. Secondo il commento del codice, a frenare i tentativi bastano i cinque per sfida e i limiti del login sulla password (`otp/servizio.py:81-83`).
- I cinque tentativi per sfida non limitano però il totale dei codici provabili dopo una password corretta: vedi [Limiti noti](#limiti-noti).
- Il codice non è salvato: nel database c'è un HMAC legato al token della sfida (`otp/servizio.py:34-38`; `backend/src/otp/identita.py:8-10`).

### Gestione del secondo fattore

- Password e codici chiesti nel profilo passano dagli stessi limiti del login (`backend/src/mfa/gestione.py:60-64`, `96`, `107`).
- Le chiavi d'account sono proprie: `mfa:` o `totp:` seguito dallo username.
- La chiave per IP è la stessa del login, quindi questi tentativi contano anche nel limite per IP (`limiti_login.py:85`).

### Indirizzo del chiamante

- L'IP viene da `request.client.host` e il codice lo converte in byte (`backend/src/security/rete.py:42-51`).
- Un indirizzo IPv4 mappato su IPv6 finisce nello stesso contenitore del corrispondente IPv4.
- Dietro il proxy l'IP arriva dalle intestazioni inoltrate.
- Il container accetta queste intestazioni da qualunque mittente (`backend/Dockerfile:34-38`; `frontend/nginx.conf:50`). La scelta si regge su due condizioni:
  - l'API è raggiungibile solo dal server web;
  - il server web riscrive `X-Forwarded-For`.
- Il commento di `rete.py:20-24` indica invece di ammettere solo l'IP del proxy.
- La configurazione del rilascio è in [deploy.md](deploy.md).

## Secondo fattore

Il codice cita questa decisione come "ADR 0009", ma il documento non è nel repository (`backend/src/mfa/metodi.py:1`; `config.py:72`, `104`).

### Chi

- Il secondo fattore riguarda solo il ruolo Nazionale (`auth/accesso.py:67-82`).
- Dopo la password il server non emette la sessione. Ricontrolla stato, password e ruolo, poi apre una sfida.
- Il server riconosce il ruolo dal suo codice testuale, confrontato in minuscolo (`auth/accesso.py:67`, `76`).
- La sfida prova il primo fattore ed è legata all'impronta della password: un cambio password la invalida (`identita.py:34-47`; `backend/src/otp/accesso.py:17-35`).
- La sessione nasce solo dopo il superamento della sfida (`otp/accesso.py:38-44`; `backend/src/mfa/accesso.py:43-60`).

### Metodi e priorità

- Il server propone il metodo migliore fra quelli posseduti, in quest'ordine: passkey, authenticator, codice via email (`metodi.py:25`, `82-86`).
- "Usa un altro metodo" apre una sfida nuova per un metodo posseduto, anche quello già in corso. La sfida precedente decade (`metodi.py:89-97`).
- L'email conta come metodo solo se è verificata (`metodi.py:45-46`). L'email in anagrafica e la sua verifica sono però modificabili da ogni utente autenticato: vedi [Limiti noti](#limiti-noti).
- Senza alcun metodo parte la verifica dell'email: il codice confermato verifica l'email e apre la sessione (`metodi.py:8-11`; `otp/servizio.py:68-72`).
- Senza un'email valida in anagrafica la risposta è 409, con l'invito a rivolgersi a un amministratore (`metodi.py:26-28`, `63-70`).

### Authenticator (TOTP)

- Segue la RFC 6238: SHA-1, 6 cifre, passo di 30 secondi, tolleranza di un passo (`backend/src/mfa/totp.py:1-6`, `29-33`).
- Un passo già accettato non vale più (`totp.py:66-83`; `backend/src/mfa/servizio_totp.py:87-97`).
- Il segreto è cifrato a riposo con AES-GCM (`totp.py:86-100`):
  - la chiave è derivata da `TOTP_CHIAVE`;
  - il nonce è di 12 byte;
  - il contesto è fisso.
- L'attivazione avviene in due passi (`servizio_totp.py:55-84`):
  1. il server mostra una volta il segreto pendente, come codice QR generato dal server e come chiave testuale;
  2. il primo codice valido attiva il segreto.
- Un evento del database cancella dopo un giorno le attivazioni mai confermate (`db/migrations/015_secondo_fattore.sql:47-52`).

### Passkey

- Nel database resta la chiave pubblica (`backend/src/mfa/servizio_passkey.py:1-9`, `46-48`).
- La challenge non si conserva: il server la deriva dal token della sfida, con il pepper.
- In registrazione valgono queste regole (`servizio_passkey.py:82-101`):
  - dispositivo esterno;
  - credenziale residente;
  - verifica dell'utente obbligatoria;
  - nessuna attestazione.
- In verifica il server usa la stessa challenge derivata, richiede la verifica dell'utente e aggiorna il contatore delle firme (`servizio_passkey.py:142-169`).
- L'avvio controlla `WEBAUTHN_RP_ID` e `WEBAUTHN_ORIGINI`. Fuori da localhost serve HTTPS (`config.py:253-269`).

### Gestione dal profilo

- Tutte le rotte di gestione richiedono la sessione e il ruolo Nazionale (`gestione.py:31`, `55-57`).
- Attivare l'authenticator richiede la password corrente (`gestione.py:84-140`). Lo stesso vale per aggiungere o rimuovere una passkey.
- Disattivare l'authenticator richiede password e codice.
- Non esiste una rotta di azzeramento per un amministratore. Le funzioni ci sono, ma nessuna rotta le usa (`servizio_totp.py:113-120`; `servizio_passkey.py:183-188`). Vedi [Limiti noti](#limiti-noti).

### Impersonificazione

- Possono impersonare solo il Regionale e il Nazionale (`auth/routers.py:267-270`; `backend/src/auth/autorizzazioni.py:54-75`).
- Il bersaglio deve rispettare quattro condizioni (`auth/routers.py:235-245`, `273-288`):
  - esistere;
  - essere attivo;
  - avere un'anagrafica;
  - avere un ruolo con accesso.
- I quattro controlli sul bersaglio condividono lo stesso 404, per non dire quale ha fallito (`auth/routers.py:235-245`).
- Il rifiuto per il ruolo di chi chiama è invece un 403 con un messaggio proprio (`autorizzazioni.py:64-74`).
- Anche un bersaglio Nazionale riceve un 403 distinto, altrimenti l'impersonificazione aggirerebbe il secondo fattore (`auth/routers.py:290-302`).
- Il log registra l'operazione con entrambi gli identificativi (`auth/routers.py:305-312`).
- La sessione di chi impersona viene revocata (`auth/accesso.py:53-55`).

## Codici OTP dei contatti e attivazione

Il flusso visto dall'utente è in [sottoscrittori-e-attuatori.md](../funzionale/sottoscrittori-e-attuatori.md). Questi sono gli aspetti di sicurezza.

- Le rotte stanno sotto `/clienti/{id}/contatti` e sono protette dalla sola sessione (`backend/src/otp/contatti.py:15`, `58-88`).
- Il codice parte solo se il valore inviato coincide con quello salvato e non è già verificato (`contatti.py:64-72`).
- La verifica è legata al valore esatto del contatto: se il valore cambia, la verifica decade (`identita.py:44-47`; `otp/servizio.py:76-78`).
- Una modifica di email o cellulare cancella anche la verifica salvata e le sfide aperte (`backend/src/clienti/routers.py:254-259`).
- Quando email e cellulare risultano verificati e l'attivazione è in attesa, l'account si attiva con una password generata (`backend/src/otp/attivazione.py:11-35`; `clienti/servizio.py:135-144`, `177-188`). La password parte una sola volta, per email.
- I valori inseriti nei modelli di email vengono sottoposti a escape HTML (`email.py:71-114`).
- Dall'oggetto delle email si tolgono gli a capo.
- Una verifica avviata dalla scheda cliente non vale mai come sfida di accesso (`otp/accesso.py:17-32`; `identita.py:29-36`).

## Log

- La redazione toglie dal testo del log, nell'ordine (`backend/src/logging_config.py:42-86`):
  1. i valori di chiavi sensibili, come `password`, `token` e `pepper`;
  2. gli hash bcrypt;
  3. i token da 43 caratteri;
  4. le impronte SHA-256 esadecimali;
  5. gli indirizzi email.
- Filtro e formatter stanno sugli handler, quindi coprono anche i messaggi propagati e i traceback (`logging_config.py:89-117`).
- I logger di uvicorn passano dal logger radice (`logging_config.py:146-151`). Così la redazione copre anche l'access log, che contiene la query string di `validate`.
- `sqlalchemy.engine` e `sqlalchemy.pool` restano a livello WARNING (`logging_config.py:153-155`).
- L'engine usa `hide_parameters=True` ed `echo=False` (`backend/src/database.py:23-39`).
- Il logging si configura per primo all'avvio, così anche un errore di configurazione passa dalla redazione (`main.py:68-70`).
- La redazione è solo una rete di sicurezza. La regola resta: nei log vanno solo identificativi come `prr_id`, `prt_id`, `sess_id` e `utente_id`, mai token, impronte, password o email (`logging_config.py:27-29`; `servizio_reset.py:251-254`).
- Il test di riferimento è `backend/tests/security/test_log_senza_segreti.py`.
- Un'eccezione a questa regola è descritta in [Limiti noti](#limiti-noti).

## Segreti e verifica all'avvio

### I tre segreti

| Variabile | Uso |
|---|---|
| `SESSION_TOKEN_PEPPER` | Impronta dei token di sessione, HMAC del CSRF, chiavi dei limiti del login, impronte di sfide, codici e limiti OTP, versione delle verifiche dei contatti, challenge delle passkey |
| `PASSWORD_RESET_TOKEN_PEPPER` | Impronta dei token di recupero e dell'indirizzo nei limiti del recupero |
| `TOTP_CHIAVE` | Cifratura dei segreti degli authenticator |

Riscontri: `tokens.py:52-77`; `browser.py:30-32`; `limiti_login.py:42-45`; `identita.py:8-10`, `44-47`; `servizio_passkey.py:46-48`; `servizio_reset.py:181-182`; `totp.py:86-100`.

Cambiare un segreto ha queste conseguenze:
- cambiare `SESSION_TOKEN_PEPPER` invalida le sessioni e le sfide aperte;
- invalida anche le verifiche dei contatti già registrate, perché la loro versione è un'impronta con quel pepper (`identita.py:44-47`; `otp/servizio.py:76-78`);
- cambiare `PASSWORD_RESET_TOKEN_PEPPER` invalida i link di recupero in corso;
- perdere `TOTP_CHIAVE` obbliga tutti a riattivare l'authenticator, quindi la chiave va nel backup dei segreti del server (`config.py:72-73`).

I valori non stanno nel repository. L'elenco delle variabili è in [riferimenti/configurazione.md](riferimenti/configurazione.md).

### Verifica in due strati

- `Impostazioni` non ha campi obbligatori né controlli propri sui valori: manca un segreto e la costruzione riesce comunque (`config.py:1-19`, `49-58`). Serve perché il motore del database si crea all'import.
- Restano però i vincoli di tipo, elenchi chiusi e numeri (`config.py:61`, `91-102`, `120`, `127`): un valore malformato nel file di configurazione fa fallire la costruzione prima della verifica d'avvio.
- `verifica_configurazione` è severa: raccoglie tutti i problemi, poi solleva un solo errore (`config.py:185-300`).
- La verifica gira all'avvio: se fallisce, l'applicazione non parte (`main.py:56-81`).
- Ogni segreto deve rispettare questi requisiti (`config.py:169-213`):
  - essere presente;
  - non avere il prefisso segnaposto dei file di esempio;
  - non avere spazi ai bordi;
  - essere lungo almeno 32 byte.
- I due pepper devono essere diversi fra loro, e `TOTP_CHIAVE` deve essere diversa da entrambi.
- La verifica controlla anche questi punti (`config.py:215-278`):
  - `DATABASE_URL` è presente e non contiene la credenziale predefinita storica;
  - i valori numerici stanno negli intervalli ammessi;
  - `CORS_ORIGINS` non contiene `*`;
  - le origini WebAuthn sono coerenti;
  - HTTP è ammesso solo su loopback.
- In produzione servono anche:
  - l'invio email via SMTP con un host (`config.py:280-291`);
  - un frontend in HTTPS;
  - il fornitore SMS reale con le sue credenziali (`main.py:71-74`; `backend/src/notifiche/config_sms.py:16-19`).
- Le funzioni che usano pepper e chiave rifiutano da sole i valori assenti o corti, anche se la verifica all'avvio non è girata (`tokens.py:52-67`; `totp.py:86-91`).

## Rilievi dell'analisi del 2026

L'analisi di settembre 2026 elencava sette rilievi di sicurezza. Questa è la situazione attuale.

| Rilievo | Stato attuale | Riscontro |
|---|---|---|
| S1. Password in chiaro | Aperto per le righe legacy non ancora convertite. La riga di chi accede viene convertita. Nessun percorso scrive password in chiaro e non ci sono riscritture massive. Il codice non dice quante righe restano: è un dato di produzione. | `utenti/models.py:20`; `servizio_login.py:48-82`; `test_nessun_plaintext.py:169-212` |
| S2. Autenticazione falsificabile | Risolto. La sessione usa un token opaco e revocabile, in un cookie `HttpOnly`, con il CSRF. `Authorization` non vale come trasporto. L'autenticazione è dichiarata sul router. Un test percorre l'elenco delle rotte e chiama senza sessione ogni rotta non dichiarata pubblica: si aspetta 401. L'elenco delle rotte pubbliche ammesse sta nel test stesso. L'impersonificazione richiede sessione e ruolo amministrativo. | `browser.py:25-27`; `backend/tests/security/test_rotte_protette.py:20-70`; `auth/routers.py:248-270` |
| S2-bis. Autorizzazione per ruolo | Parziale. Il ruolo si controlla solo in quattro casi: impersonificazione, modifica di un altro utente, cambio del padre di un'azienda, gestione del secondo fattore. Esiste un filtro di visibilità solo sulle aziende. Il resto richiede solo la sessione. Il dettaglio è in [Limiti noti](#limiti-noti). | `autorizzazioni.py:25-95`; `utenti/routers.py:154-160`; `backend/src/aziende_xcod/router.py:53`; `gestione.py:55-57`; `backend/src/aziende_xcod/servizi.py:73-88` |
| S3. Stato dell'account | Risolto. Un utente disattivato riceve lo stesso 401 di una password errata. Le sessioni, l'impersonificazione e le sfide lo escludono. | `servizio_login.py:92-94`; `sessioni.py:95`; `auth/routers.py:280-281`; `otp/accesso.py:29` |
| S4. Errore 500 come oracolo | Risolto, con un'eccezione. Chi non ha un'anagrafica, o ha un ruolo senza accesso, riceve il 401 generico. L'anagrafica si sceglie con un ordine esplicito. La verifica della password non solleva eccezioni e il recupero non risponde mai 500. Gli errori del database hanno messaggi generici. Eccezione: le rotte dei prodotti formativi restituiscono il testo dell'errore del database. | `auth/accesso.py:28-37`; `servizio_login.py:128-150`; `password.py:111-128`; `auth/routers.py:98-110`; `main.py:124-177`; `backend/src/listini_testa/routers.py:94-100` |
| S5. Credenziali SMTP nel database | Il codice non legge credenziali di posta dal database: le prende dalla configurazione. Il contenuto delle tabelle legacy non si verifica dal codice. | `config.py:119-128`; `backend/src/notifiche/backend_invio.py:36-62` |
| S6. Credenziali predefinite | Risolto. Il codice non ha un ripiego con credenziali. Senza `DATABASE_URL` l'import usa un database in memoria inerte e l'avvio fallisce. L'avvio rifiuta la credenziale storica. Il motore però usa `TEST_DATABASE_URL` quando è impostata, prima di `DATABASE_URL`, mentre la verifica d'avvio guarda solo `DATABASE_URL`: una variabile d'ambiente rimasta impostata dirotta l'applicazione senza che la verifica se ne accorga. | `database.py:10-21`, `17-21`; `config.py:63-66`, `215-221` |
| S7. CORS | Parzialmente aperto. Le origini vengono dalla configurazione e `*` è rifiutato in ogni ambiente. Restano ammessi le credenziali e i metodi e le intestazioni `*`. Il rischio è contenuto da tre difese: `X-ERSAF-Request`, il controllo di `Origin` e il CSRF. | `main.py:86-93`; `config.py:250-251`, `290-291`; `browser.py:56-80` |

## Limiti noti

Questa sezione elenca i difetti noti di autorizzazione, visibilità e coerenza, e i contrasti fra interfaccia e server. Ogni voce indica il difetto e il punto del codice, senza istruzioni per riprodurlo. I documenti funzionali rimandano qui con una riga.

Nota: un lavoro in corso, non ancora unito a main, riguarda la visibilità dei clienti e l'assegnazione dei ruoli. Chiuderà una parte delle voci sotto. La pull request che lo unirà dovrà aggiornare questa sezione.

### Sessione, ruoli e secondo fattore

- **Cambio di ruolo e sessioni aperte.**
  - La validazione della sessione non controlla il ruolo.
  - Un ruolo revocato o cambiato ha effetto solo al nuovo accesso: chi perde l'accesso resta collegato, e chi diventa Nazionale usa la sessione precedente senza il secondo fattore, che è applicato solo al login.
  - `security/sessioni.py:74-102`; `auth/accesso.py:62-82`.
- **Tentativi sul secondo fattore.**
  - Il limite di cinque tentativi vale per singola sfida e non limita il numero complessivo di codici provati dopo una password corretta.
  - Il commento del codice dice il contrario (`otp/servizio.py:81-83`).
  - Punti interessati: `metodi.py:89-97`; `otp/accesso.py:17-51`; `mfa/accesso.py:43-66`.

### Autorizzazione applicata solo dall'interfaccia

- **Pagine riservate al Nazionale solo nel menu.**
  - Attuatori, Aziende e Prodotti formativi sono nascosti nel menu agli altri ruoli.
  - Le pagine però si aprono dall'indirizzo con qualunque sessione valida.
  - `frontend/src/config/routes/rotte.js:20-47`; `frontend/src/App.jsx:35-71`.
- **Anagrafiche senza controllo di ruolo.**
  - Creazione, lettura e modifica di sottoscrittori, attuatori e curriculum richiedono solo la sessione.
  - Lo stesso vale per la creazione diretta di utenti, che l'interfaccia non usa.
  - `backend/src/clienti/routers.py:39-43`, `88-292`; `backend/src/universita/routers.py:18-22`, `58`, `78`, `84`, `108`; `backend/src/utenti/routers.py:51-100`.
- **Ruolo assegnabile da chiunque.**
  - Il server accetta qualunque ruolo, in creazione e in modifica di un'anagrafica, da qualunque utente autenticato, anche sulla propria anagrafica.
  - La scheda Utente offre tutti i ruoli. La scheda Dati principali degli attuatori offre anche Regionale e Nazionale.
  - `backend/src/clienti/schemas.py:163`, `232`; `clienti/servizio.py:197-216`, `254-257`; `clienti/routers.py:260-261`; `frontend/src/components/SchedaUtente.jsx:254-273`; `frontend/src/components/NuovoSottoscrittore.jsx:404-431`.
- **Tabella dei ruoli modificabile da ogni utente autenticato.**
  - Creazione e modifica dei ruoli richiedono solo la sessione.
  - Eppure il codice del ruolo decide l'obbligo del secondo fattore e i permessi amministrativi.
  - `backend/src/ruolo/routers.py:10-18`, `47-87`; `auth/accesso.py:67`; `autorizzazioni.py:32`.
- **Abilitazioni alle pratiche.**
  - La scheda Abilitazioni compare solo al Nazionale, in modifica di un attuatore.
  - Il server accetta i cinque campi, in creazione e in modifica, da ogni utente autenticato.
  - `NuovoSottoscrittore.jsx:38-41`, `256-271`, `343-345`; `clienti/schemas.py:168-173`, `237-242`; `clienti/servizio.py:211-214`.
- **Pratiche.**
  - La Dashboard abilita i pulsanti solo con l'abilitazione generale e quella dell'ateneo.
  - Elenco, dettaglio, creazione, modifica e PDF delle pratiche non controllano né abilitazioni né ruolo.
  - La pagina Pratiche non è nel menu, ma si apre dall'indirizzo.
  - `frontend/src/components/PannelloPratiche.jsx:39-41`, `94`; `backend/src/pratiche/routers.py:14-22`, `53-102`; `documenti/rotte.py:51-83`; `rotte.js:20-41`; `App.jsx:56`.
- **Prodotti formativi e tipi di corso.**
  - La voce di menu è solo per il Nazionale.
  - Creazione e modifica sono aperte a ogni utente autenticato.
  - `listini_testa/routers.py:17-21`, `49`, `174`; `backend/src/listino_tipoCorso/routers.py:8-12`, `15`, `38`.
- **Aziende.**
  - La voce Aziende è solo per il Nazionale.
  - Ogni utente autenticato può creare aziende e modificare dati e percentuali di quelle che vede: la propria e le discendenti.
  - `backend/src/aziende/routers.py:138-166`, `229-295`; `aziende_xcod/servizi.py:73-88`.
- **Verifica dei contatti.**
  - Le rotte di stato, invio e conferma dei codici non controllano il ruolo.
  - Non controllano nemmeno a chi appartiene l'anagrafica.
  - L'email dell'anagrafica e la sua verifica decidono anche il metodo del secondo fattore del Nazionale (`metodi.py:45-46`): finché queste rotte e la modifica dell'anagrafica non controllano ruolo e appartenenza, il secondo fattore non è più robusto della scheda anagrafica.
  - `otp/contatti.py:15`, `58-88`; `clienti/routers.py:39-43`, `254-261`.

### Visibilità dei dati

Su main il filtro di visibilità esiste solo per le aziende.

- **Anagrafiche.**
  - Nessun filtro per ruolo, azienda o gerarchia: ogni utente autenticato elenca e legge tutte le anagrafiche, con contatti, documento, azienda e username.
  - Anche l'elenco degli utenti è completo, e il campo "utente padre" non limita nulla.
  - `clienti/routers.py:126-177`; `clienti/schemas.py:249-255`; `utenti/routers.py:112-143`.
- **Colonna Azienda.**
  - L'elenco attuatori mostra la colonna solo al Nazionale.
  - L'API però restituisce l'azienda in ogni riga.
  - `frontend/src/components/ElencoClienti.jsx:31-33`; `clienti/schemas.py:253`.
- **Pratiche.**
  - Nessun filtro: ogni utente autenticato vede tutte le pratiche.
  - Lo stesso vale per le opzioni dei filtri.
  - `pratiche/routers.py:72-83`; `backend/src/pratiche/filtri.py:23-44`; `backend/src/pratiche/opzioni.py:35-66`.
- **Documento PDF della pratica.**
  - Ogni utente autenticato può scaricarlo, per qualunque pratica.
  - Contiene dati anagrafici, estremi del documento e firma.
  - `documenti/rotte.py:51-83`; `backend/src/documenti/dati.py:93-100`, `140-162`.
- **Padre di un'azienda.**
  - La lettura del padre non applica il filtro di visibilità.
  - Il dettaglio dell'azienda invece lo applica e risponde 404.
  - `aziende_xcod/router.py:32-42`; `aziende/routers.py:71-77`.
- **Esistenza di un'azienda.**
  - La ricerca per partita IVA rispetta la visibilità.
  - La creazione invece rifiuta con un messaggio esplicito un valore univoco già presente, anche se l'azienda non è visibile, e così ne rivela l'esistenza.
  - `aziende/routers.py:37-68`, `144`, `194-213`.
- **Anomalie delle aziende.**
  - Il controllo dei codici fiscali duplicati legge tutta la tabella.
  - Riporta la ragione sociale delle aziende in conflitto anche quando sono fuori dalla visibilità di chi guarda.
  - Il testo compare nell'elenco e nella scheda.
  - `aziende/routers.py:94-134`, `165`, `189`, `212`, `224`, `258`; `frontend/src/lib/righeElenco.js:50`; `frontend/src/components/SchedaAzienda.jsx:112-121`.
- **Aziende invisibili a chi le crea.**
  - Un utente non Nazionale senza azienda crea aziende radice.
  - Poi non le vede.
  - `aziende/routers.py:151-152`; `aziende_xcod/servizi.py:84-87`.
- **Consulenti e Operatori.**
  - Non compaiono in nessun elenco.
  - Un'anagrafica a cui la scheda Utente assegna uno di questi ruoli sparisce sia da Sottoscrittori sia da Attuatori.
  - `clienti/routers.py:141-150`; `SchedaUtente.jsx:269`, `271`.

### Incoerenze dell'interfaccia

- **Pulsante "Accedi con questo utente".**
  - Compare a qualunque utente collegato, senza guardare il suo ruolo, e anche quando il bersaglio è Nazionale. Il filtro dell'interfaccia riguarda solo il bersaglio: attivo e con un ruolo da attuatore.
  - Il server lo consente solo a Regionale e Nazionale e rifiuta sempre il bersaglio Nazionale.
  - `SchedaUtente.jsx:213-218`, `347-355`; `auth/routers.py:267-270`, `290-302`.
- **Salvataggio a metà nella scheda Utente.**
  - La scheda salva prima il ruolo, poi username, stato e padre.
  - Per chi non è Regionale o Nazionale, e modifica un altro utente, il ruolo viene salvato e il resto rifiutato con 403.
  - `SchedaUtente.jsx:111-138`; `utenti/routers.py:154-160`.
- **Attivazione annullata dal salvataggio della scheda Utente.**
  - La scheda invia sempre lo stato dell'account.
  - Il server allora cancella l'attivazione in attesa, e la verifica dei contatti non attiva più l'account.
  - Il comportamento è dedotto dalla lettura del codice, non da un'esecuzione.
  - `SchedaUtente.jsx:126-133`; `utenti/routers.py:172-174`; `otp/attivazione.py:11-16`.
- **Due pulsanti "Salva Modifiche" nella stessa scheda.**
  - Il pulsante del modulo salva l'anagrafica, ma non username, stato e padre.
  - Per gli attuatori rimanda il ruolo letto all'apertura della pagina. Così sovrascrive un ruolo cambiato nel frattempo dalla scheda Utente.
  - Il commento del codice dice che il ruolo parte solo se cambiato.
  - `SchedaUtente.jsx:337-345`; `NuovoSottoscrittore.jsx:93-95`, `224-233`, `484-495`.
- **Contatti mostrati come verificati.**
  - Un account attivo senza alcuna verifica registrata vede email e cellulare come "Verificato", con il pulsante disabilitato.
  - Il server non li considera verificati. Per esempio, non li conta come metodo del secondo fattore.
  - `otp/contatti.py:33-51`; `frontend/src/components/contatti/CampoContatto.jsx:5-6`, `24-31`; `otp/servizio.py:76-78`; `metodi.py:45-46`.
- **Codice fiscale segnato come obbligatorio.**
  - Il campo ha l'asterisco.
  - Né l'interfaccia né il server lo richiedono.
  - `frontend/src/components/FormInformazioniPersonali.jsx:12-20`; `clienti/schemas.py:100-101`, `133`.
- **Pulsante "Prevalutazione".**
  - Porta a una pagina che non esiste, quindi a "Pagina non trovata".
  - `PannelloPratiche.jsx:46-48`; `frontend/src/lib/configPratiche.js:18-22`, `101-105`; `App.jsx:73`.
- **Tendina "Tipologia corso".**
  - Nessun blocco della Dashboard attiva l'opzione che la mostra.
  - Quindi, dalla Dashboard, la tendina non compare mai.
  - `PannelloPratiche.jsx:56`; `configPratiche.js:10-147`; `frontend/src/components/FiltriPratiche.jsx:40`.
- **Ricerca "per codice" degli studenti.**
  - Nella scheda pratica la ricerca promette il codice, ma il server cerca solo per nome e cognome.
  - Nel filtro Studenti dell'elenco il "codice" è il codice cliente. Per le anagrafiche nuove è un codice interno casuale, non il codice fiscale.
  - `frontend/src/config/pratica.js:3-4`; `clienti/routers.py:152-169`; `frontend/src/config/filtriPratiche.js:1-6`; `pratiche/opzioni.py:41-58`; `clienti/servizio.py:102-111`, `266`.
- **Filtro dei percorsi.**
  - Il server offre le opzioni dei percorsi per l'elenco pratiche.
  - L'interfaccia non le usa.
  - `pratiche/opzioni.py:61-66`.
- **Scheda Esami.**
  - Mostra "Sezione in fase di sviluppo".
  - Le schede ammesse nell'indirizzo comprendono anche "prevalutazioni", che non ha una scheda.
  - `NuovoSottoscrittore.jsx:340-342`, `470-481`; `frontend/src/config/routes/query.js:39-51`.
- **Campi svuotati nella scheda azienda.**
  - L'interfaccia non invia i campi vuoti, e il server aggiorna solo i campi ricevuti.
  - Svuotare un campo facoltativo non lo cancella: il valore precedente resta salvato e ricompare al ricaricamento.
  - `SchedaAzienda.jsx:73`; `aziende/routers.py:238-242`.
- **Dettaglio degli azzeramenti a cascata.**
  - Quando un cambio di percentuali ne azzererebbe altre, il server non scrive e risponde con l'elenco delle aziende e dei campi interessati.
  - L'interfaccia ignora l'elenco e mostra solo un avviso generico.
  - `aziende/routers.py:285-288`; `aziende_xcod/servizi.py:197-208`; `frontend/src/components/SchedaAziendaAttuatori.jsx:376-381`.
- **Campi obbligatori dell'anagrafica.**
  - I campi obbligatori sono marcati solo con l'attributo del browser, e le schede si rendono una per volta: salvando da una scheda diversa da Dati Principali quei campi non sono nel documento e il controllo non scatta.
  - Lo schema di modifica ha tutti i campi opzionali, per non bloccare le anagrafiche storiche: in modifica l'obbligo è quindi solo dell'interfaccia.
  - `NuovoSottoscrittore.jsx:376`, `391-394`; `FormInformazioniPersonali.jsx:50`, `63`, `78`, `93`, `118`; `clienti/schemas.py:189-247`.
- **Messaggi dopo la disattivazione dell'app.**
  - La finestra di disattivazione annuncia il codice via email dal prossimo accesso.
  - Il server propone invece il primo metodo rimasto, per priorità; senza metodi chiede la verifica dell'email.
  - `frontend/src/config/testi/sicurezza.js:38`; `metodi.py:82-86`.
- **Invio non riuscito e troppe richieste.**
  - Il server distingue i due casi con messaggi propri: 503 con l'invito ad attendere un minuto, 429 con `Retry-After`.
  - L'interfaccia sostituisce ogni 5xx con "Servizio temporaneamente non disponibile" e ogni 429 con "Troppi tentativi", perdendo il motivo.
  - `invio.py:34`; `otp/limiti.py:25`; `frontend/src/lib/erroriApi.js:16-21`.
- **Cambio padre di un'azienda.**
  - La finestra esclude solo l'azienda stessa.
  - Il server rifiuta anche le sue discendenti, perché creerebbero un ciclo.
  - `frontend/src/components/ModalCambiaPadreAzienda.jsx:36-40`; `aziende_xcod/router.py:67-71`.
- **Generazione del codice prodotto.**
  - Il campo dice "Inserisci o genera codice", ma non c'è un pulsante per generarlo.
  - La funzione arriva al modulo e resta inutilizzata.
  - `frontend/src/components/ProdottoFormInfo.jsx:4`, `19`; `frontend/src/components/InserimentoProdotto.jsx:139`, `343`.
- **Convenzione -1/0 letta in modi diversi.**
  - L'elenco prodotti considera attivo solo -1, e così anche gli interruttori delle Abilitazioni.
  - La regola generale del frontend e il pannello della Dashboard considerano vero ogni valore diverso da zero.
  - `righeElenco.js:72`; `frontend/src/components/SchedaAbilitazioniPratiche.jsx:25`; `frontend/src/lib/flagLegacy.js:16-21`; `clienti/routers.py:53-59`.
- **Messaggio uniforme del recupero password.**
  - Una persona senza ruolo attuatore, o con l'indirizzo condiviso con un altro attuatore attivo, vede lo stesso messaggio degli altri ma non riceve la mail.
  - È una scelta voluta contro l'enumerazione degli account.
  - `servizio_reset.py:125-160`; `auth/schemas.py:29`.
- **Pagina dopo l'accesso.**
  - Dopo il login, e dopo un'impersonificazione, si arriva a Sottoscrittori e non alla Dashboard.
  - Eppure la Dashboard è l'unico accesso alle Pratiche dal menu.
  - `frontend/src/config/routes/percorsi.js:14`; `SchedaUtente.jsx:165`.
- **Una sola data per tre titoli.**
  - Diploma, anno integrativo e titolo universitario scrivono la stessa data.
  - `frontend/src/components/SezioneTitoli.jsx:36`, `178`, `283`.
- **Durata del link di recupero.**
  - I testi dicono "60 minuti", un valore fisso.
  - Nel server la durata è configurabile.
  - `frontend/src/config/testi/accesso.js:61`, `67`, `82`; `config.py:77`.
- **Lunghezza minima della password.**
  - Nel frontend è fissa a 8.
  - Nel server è configurabile, con minimo 8.
  - Il test di allineamento confronta il frontend con la configurazione attiva.
  - `frontend/src/lib/passwordPolicy.js:12`; `config.py:102`, `225`; `test_policy_allineata.py:54-57`.
- **Indirizzo di creazione dei prodotti.**
  - L'interfaccia invia la creazione a un indirizzo senza barra finale.
  - La rotta del server ha la barra finale.
  - `InserimentoProdotto.jsx:289`; `listini_testa/routers.py:49`.

### Valori cablati e dati

- **Elenco delle password vietate.**
  - L'elenco esatto e il controllo sul nucleo di lettere sono tarati su un minimo di 12 caratteri.
  - Con il minimo predefinito di 8, una password senza lettere più corta di 12 caratteri non viene intercettata.
  - `security/password.py:46-61`, `159-198`; `config.py:102`.
- **Valori fissi nel modulo prodotto.**
  - Il codice del modulo contiene tipo di corso, università, livello, modalità, facoltà, corso di laurea e durata.
  - I filtri dell'elenco invece leggono università e tipi di corso dal server.
  - `ProdottoFormInfo.jsx:31-46`, `74-86`, `113-250`; `frontend/src/components/ElencoProdottiFormativi.jsx:46-51`.
- **Abbinamenti fra pulsanti e tipi di corso.**
  - Il codice li marca "DA CONFERMARE".
  - `configPratiche.js:40`, `46`, `94`, `111`, `144`.
- **Autore del prodotto.**
  - L'autore della creazione arriva dal browser. In modifica, se manca, il frontend usa 1.
  - Il campo dell'ultima modifica non viene mai valorizzato.
  - `InserimentoProdotto.jsx:36`, `112`; `backend/src/listini_testa/models.py:59-61`, `75`.
- **Righe di prezzo del prodotto.**
  - Un salvataggio con righe di prezzo cancella tutte le righe e le reinserisce.
  - I controlli su prezzo e tasse stanno solo nell'interfaccia: prezzo presente, maggiore di zero per le righe nuove, tasse non negative. Lo schema del server accetta un prezzo assente, che diventa zero, e valori negativi sia di prezzo sia di tasse. Uno schema con il vincolo sul prezzo esiste ma nessuna rotta lo usa.
  - `listini_testa/routers.py:208-216`; `backend/src/listini_dettagli/models.py:39-46`, `48-55`; `InserimentoProdotto.jsx:225-259`.
- **Università del prodotto ed errori del database.**
  - Nel modulo l'università è facoltativa e il frontend la invia come valore nullo quando il campo è vuoto.
  - In creazione lo schema vuole un intero e non ammette il valore nullo.
  - In modifica lo schema lo ammette, ma la colonna è dichiarata non nulla: l'esito dipende dalla configurazione del database.
  - Se il database rifiuta la scrittura, il router traduce l'errore in un 400 "Errore di unicità sul codice" con il testo del database, qualunque sia il vincolo violato.
  - Le rotte dei prodotti restituiscono in generale il testo degli errori del database.
  - `ProdottoFormInfo.jsx:74-86`; `frontend/src/lib/prodottoPayload.js:37-40`; `listini_testa/models.py:23`, `56`, `73`; `listini_testa/routers.py:85-100`, `230-235`.
- **Pratiche.**
  - Nessuna regola limita i passaggi di stato.
  - Lo storico degli stati esiste solo come modello e nessuno lo scrive.
  - L'autore della pratica non viene mai registrato.
  - Il prezzo è obbligatorio solo nell'interfaccia.
  - In modifica lo schema accetta ogni campo che dichiara, azienda, consulente e tipo di corso compresi, mentre la scheda ne cambia solo una parte. Il router applica quanto arriva, senza confrontarlo con quello che la scheda mostra.
  - `pratiche/routers.py:53-102`, `87-101`; `backend/src/pratiche_stati_storico/models.py:16-19`; `backend/src/pratiche/models.py:80-82`, `109-110`, `240`, `280-303`; `frontend/src/lib/praticaForm.js:26-32`.
- **Abilitazione ai corsi speciali.**
  - In creazione, se la richiesta non invia i cinque campi, gli altri quattro nascono accesi per gli attuatori e i corsi speciali spenti; il valore predefinito del database è invece -1. È un valore predefinito, non una forzatura: una richiesta che invia il valore lo mantiene.
  - Dall'interfaccia il caso non si presenta in creazione, perché i cinque campi non vengono inviati.
  - Il pannello della Dashboard legge i permessi da una relazione non deterministica per chi ha più anagrafiche.
  - `clienti/servizio.py:56-64`, `211-214`; `backend/src/clienti/models.py:82-86`; `clienti/routers.py:45-59`; `utenti/models.py:73-79`; `servizio_login.py:128-135`.
- **Controllo del codice fiscale.**
  - In creazione il server controlla struttura e carattere di controllo.
  - In modifica controlla solo la lunghezza di 16 caratteri, e solo se il valore cambia.
  - `clienti/schemas.py:90-120`, `185`, `273`; `clienti/routers.py:225-232`.
- **Unicità in modifica.**
  - Il controllo di unicità considera anche i campi non modificati, e l'interfaccia rimanda sempre tutti i campi.
  - Un'anagrafica che condivide già un contatto o un documento con un'altra non si può salvare.
  - `clienti/routers.py:204`; `clienti/servizio.py:47-54`, `70-96`; `NuovoSottoscrittore.jsx:208-272`.
- **Codice cliente.**
  - Il server lo genera in creazione.
  - La modifica però accetta ancora un valore inviato dal client.
  - `clienti/servizio.py:200-208`, `266`; `clienti/schemas.py:203`; `clienti/routers.py:234-244`, `260-261`.
- **Date obbligatorie svuotate.**
  - In modifica il router riempie con la stringa vuota i soli campi di testo dichiarati non nulli; le date non sono in quell'elenco.
  - Una data inviata vuota arriva quindi al database come valore nullo su una colonna dichiarata non nulla. L'esito dipende dalla configurazione del database.
  - `clienti/routers.py:234-245`, `279-289`; `clienti/models.py:44`, `54-57`.
- **Username.**
  - La creazione controlla che lo username sia unico. La modifica no.
  - Un doppione rende ambigue le due identità, e il login le rifiuta entrambe.
  - `utenti/routers.py:56-64`, `171-179`; `backend/src/utenti/schemas.py:42-44`; `servizio_login.py:25-45`.
- **Utente padre.**
  - La creazione diretta di un utente valida il padre inviato, poi lo sovrascrive con chi crea.
  - La modifica controlla solo che il padre esista e non sia l'utente stesso. I cicli non sono controllati.
  - `utenti/routers.py:25-47`, `81-87`, `175-176`.
- **Casella condivisa nel recupero password.**
  - Un indirizzo può essere condiviso fra un solo attuatore attivo e anagrafiche senza ruolo attuatore.
  - In questo caso il link parte verso quella casella.
  - `servizio_reset.py:130-150`.
- **Azzeramento del secondo fattore.**
  - Manca una rotta per l'amministratore.
  - Un Nazionale che perde il dispositivo può ripiegare solo sull'email, e solo se è verificata.
  - `servizio_totp.py:113-120`; `servizio_passkey.py:183-188`; `metodi.py:45-46`.
- **Percentuali delle aziende.**
  - L'interfaccia limita i valori a 0-100.
  - Il server accetta qualunque intero, e un'azienda radice non ha un tetto.
  - `frontend/src/components/SchedaAziendaAttuatori.jsx:365-366`; `backend/src/aziende/schemas.py:105-115`; `aziende_xcod/servizi.py:130-140`.
- **Traccia di audit dei prodotti.**
  - Il cambio di codice di un prodotto si registra con `print`, non con il logging.
  - Quindi la traccia non passa dalla redazione e non arriva ai file di log.
  - `listini_testa/routers.py:203`.
- **Commenti e messaggi superati.**
  - `autorizzazioni.py:29-31` dice che il Nazionale oggi non può accedere, ma il secondo fattore esiste.
  - `password.py:20`, `46` e `passwordPolicy.js:25` parlano di un minimo di 12 caratteri.
  - Il messaggio d'errore all'avvio parla di "due pepper", ma i segreti sono tre (`config.py:297-299`).
  - `NuovoSottoscrittore.jsx:209-210` dice che il codice cliente deriva dall'identificativo, ma è casuale.
