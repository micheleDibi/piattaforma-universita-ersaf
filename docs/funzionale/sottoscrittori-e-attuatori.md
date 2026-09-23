# Sottoscrittori e attuatori

Questa pagina descrive le anagrafiche delle persone: come si cercano, come si
creano, cosa contiene la scheda e come si attiva l'account.

Nel testo, «interfaccia» indica le pagine che si usano nel browser. «Server»
indica il sistema che salva i dati e applica le regole.

## Due tipi di anagrafica

Ogni anagrafica riguarda una persona. Contiene i dati personali, il curriculum
formativo e un utente, cioè le credenziali con cui la persona può accedere.

- **Sottoscrittori**: anagrafiche con ruolo Utente o Consulente. Con questi
  ruoli non si accede alla piattaforma.
- **Attuatori**: anagrafiche con ruolo Aderente, Provinciale, Regionale,
  Nazionale o Operatore. Con i primi quattro ruoli si accede alla
  piattaforma; con il ruolo Operatore no. Il Nazionale accede con un secondo
  fattore: vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

Le differenze fra i due tipi:

| | Sottoscrittore | Attuatore |
|---|---|---|
| Schede | Dati principali, Curriculum formativo, Utente, Esami | Dati principali, Curriculum formativo, Utente, Azienda, più Abilitazioni (vedi sotto) |
| Ruolo alla creazione | Utente | quello scelto nella tendina «Ruolo attuatore»; se non si sceglie nulla, Aderente |
| Abilitazioni alle pratiche alla creazione | tutte spente | tutte accese, tranne SSML Lamezia Terme |

Per i permessi dei singoli ruoli vedi [Ruoli e permessi](ruoli-e-permessi.md).

## Elenchi

Il menu mostra «Sottoscrittori» a tutti e «Attuatori» a Nazionale, Regionale e Provinciale.

Nota: questo limite è applicato solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Ricerca e filtri

- La ricerca divide il testo in parole. Ogni parola deve comparire, anche solo
  in parte, nel nome o nel cognome. Maiuscole e minuscole sono indifferenti.
- Negli Attuatori ogni parola può comparire anche nella ragione sociale
  dell'azienda associata.
- Negli Attuatori il pulsante «Filtri» apre la tendina «Ruolo»: Tutti i ruoli,
  Aderente, Provinciale, Regionale, Nazionale, Operatore. «Azzera filtri» toglie il
  filtro.

### Colonne

Accanto al titolo compare il numero di risultati, calcolato con la stessa
ricerca e gli stessi filtri dell'elenco.

- Sottoscrittori: Nominativo e Verifiche.
- Attuatori: Nominativo, Ruolo e Verifiche. Il Nazionale vede anche la colonna
  Azienda, fra Ruolo e Verifiche.
- Il **Nominativo** è «Cognome Nome», preceduto da un cerchio con le iniziali.
  Se l'anagrafica ha delle anomalie, subito dopo il nome compare il segnale di
  avviso: un clic apre l'elenco degli errori, con il loro numero come titolo.
- Su uno schermo stretto le righe diventano riquadri, con il nominativo in
  evidenza.

La colonna **Verifiche** è una fila di etichette, verdi e con la spunta
quando la cosa è a posto, grigie quando non lo è:

| Etichetta | Verde quando |
|---|---|
| Email | l'indirizzo è stato verificato con un codice |
| Cellulare | il numero è stato verificato con un codice |
| Diploma | i dati del diploma sono completi (solo nei Sottoscrittori) |

I dati del diploma si considerano completi quando ci sono tutti e cinque:
diploma, anno di conseguimento, istituto, voto ricevuto e voto massimo. Via,
città e provincia dell'istituto non contano. Uno zero come voto vale come
valorizzato.

Il significato non dipende solo dal colore: l'etichetta verde ha la spunta e
il bordo pieno, passandoci sopra con il mouse compare la descrizione a
parole, e chi usa un lettore di schermo la sente leggere insieme alla riga.

Nota: la colonna Azienda è nascosta solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Scorrimento

- L'elenco segue l'ordine di inserimento.
- Le righe arrivano a blocchi. Il blocco successivo si carica scorrendo fino
  in fondo alla pagina oppure con «Carica altri elementi».
- Alla fine compare «Hai raggiunto la fine dell'elenco». Se un caricamento
  non riesce compare «Riprova».
- Un clic sulla riga apre la scheda.

### Chi vede quali anagrafiche

- Il Nazionale vede tutte le anagrafiche.
- Chiunque altro vede la propria e quelle delle persone che dipendono da lui o
  da una persona della sua stessa azienda, seguendo la catena dell'utente
  padre fino in fondo, a qualunque profondità. La catena vale anche quando
  attraversa una persona senza anagrafica.
- Le persone della stessa azienda non compaiono per il solo fatto di esserlo:
  compaiono se a loro volta dipendono da qualcuno del gruppo.
- Chi non ha un'azienda vede solo la propria anagrafica e chi dipende da lui.

La stessa regola vale per aprire una scheda: un'anagrafica che non si vede
nell'elenco risponde «non trovata» anche aprendola dall'indirizzo, con lo
stesso messaggio di un'anagrafica inesistente.

## Creare un'anagrafica

Il pulsante «Nuovo», in alto nell'elenco, apre una scheda vuota. Chi usa un
lettore di schermo sente la forma estesa, «Nuovo sottoscrittore» o «Nuovo
attuatore». Il pulsante è visibile a chiunque apra l'elenco.

### Cosa si compila

Nella scheda Dati principali, divisa in sezioni con titolo e descrizione a
sinistra e campi a destra:

- **Informazioni personali**: nome, cognome, codice fiscale, genere, data di
  nascita, luogo e provincia di nascita, cittadinanza.
- **Ruolo**, solo per gli attuatori: tendina «Ruolo attuatore» con la voce
  iniziale «Aderente (default)», seguita da Aderente, Regionale, Provinciale e
  Nazionale, nell'ordine in cui i ruoli sono registrati.
- **Contatti**: email e cellulare, con lo stato di verifica accanto
  all'etichetta; poi PEC e telefono.
- **Documento**: tipo (carta d'identità, passaporto, patente), numero, comune
  di rilascio, data di rilascio, data di scadenza.
- **Residenza** e **Domicilio**: indirizzo, civico, comune, CAP, provincia.
  «Copia da residenza», nella sezione Domicilio, copia i cinque campi della
  residenza su quelli del domicilio.

Già in creazione si possono compilare il Curriculum formativo e, per un
attuatore, la scheda Azienda. La scheda Utente mostra «Nessun utente
selezionato.» finché l'anagrafica non è salvata.

«Crea Sottoscrittore» o «Crea Attuatore» salva tutto insieme.

Chiunque arrivi alla pagina può scegliere qualunque ruolo da attuatore,
Nazionale compreso.

Nota: né l'interfaccia né il server limitano chi può assegnare un ruolo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Campi obbligatori

| Campo | Interfaccia | Server |
|---|---|---|
| Nome, cognome, cittadinanza, luogo di nascita, data di nascita | obbligatorio | obbligatorio |
| Numero, comune di rilascio, data di rilascio e data di scadenza del documento | obbligatorio | obbligatorio |
| Indirizzo, civico e comune di residenza | obbligatorio | obbligatorio |
| Codice fiscale | segnato con l'asterisco, ma non richiesto | facoltativo |
| Tutti gli altri campi | facoltativo | facoltativo |

Email e cellulare sono facoltativi, ma senza tutti e due l'account non si
attiva: vedi più avanti la verifica dei contatti.

Nota: l'asterisco sul codice fiscale non corrisponde a un obbligo reale; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Il server controlla anche:

- **il codice fiscale**, se compilato: lunghezza di 16 caratteri, struttura e
  carattere di controllo. Il controllo accetta le lettere che sostituiscono
  le cifre nei casi di omocodia e presuppone un codice fiscale italiano. I
  messaggi sono «Codice fiscale non valido: deve essere lungo 16 caratteri.»,
  «Codice fiscale non valido: formato non conforme.» e «Codice fiscale non
  valido: carattere di controllo errato.»;
- **la scadenza del documento**: non può essere già passata. Il messaggio è
  «Il documento è scaduto: inserisci una data di scadenza valida.»

Il browser segnala i campi obbligatori vuoti solo se si salva mentre è aperta
la scheda Dati principali. Da un'altra scheda la richiesta arriva al server.
Il server risponde con i problemi separati da punto e virgola. Per un campo
mancante il messaggio è un testo tecnico in inglese, che non nomina il campo;
i messaggi identici compaiono una volta sola, quindi più campi vuoti dello
stesso tipo danno una sola riga.

Nota: il controllo dei campi obbligatori dipende dalla scheda aperta; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Controlli di unicità

Il server rifiuta il salvataggio se un'altra anagrafica ha già lo stesso
valore in uno di questi campi: codice fiscale, email, telefono, cellulare,
PEC, numero di documento. Il messaggio nomina il campo, per esempio «Esiste
già un cliente registrato con questa email.» oppure «Esiste già un cliente con
questo numero di documento.». Lo stesso controllo vale in modifica, senza
confrontare l'anagrafica con sé stessa.

In modifica l'interfaccia rimanda tutti i campi, non solo quelli cambiati, e
il controllo li riguarda tutti. Se l'anagrafica condivide già uno di questi
valori con un'altra, la scheda non si salva più, anche lavorando su un campo
diverso, finché quel valore resta com'è.

Nota: il controllo di unicità riguarda anche i campi non toccati; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Cosa succede al salvataggio

Il server esegue tutti i passi insieme: se uno fallisce, non salva nulla.

1. Crea l'utente **disattivato**. Il nome utente unisce nome e cognome,
   ciascuno con la sola iniziale maiuscola. Se è già usato, riceve un numero
   in coda, a partire da 2. Il numero in coda scatta solo se il nome utente
   esistente è scritto allo stesso modo: se ne esiste uno uguale con maiuscole
   e minuscole diverse, il nuovo nasce doppio, e da quel momento nessuno dei
   due account riesce più ad accedere. La password è un valore casuale che
   nessuno conosce.
2. Registra come utente padre chi ha creato l'anagrafica.
3. Crea l'anagrafica, con un codice cliente interno generato a caso.
4. Salva il curriculum formativo.
5. Mette l'account in attesa di attivazione.

Nota: il controllo del nome utente distingue maiuscole e minuscole, la ricerca all'accesso no; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Poi si apre la scheda della nuova anagrafica. Nella sezione Contatti compare
«Verifica email e cellulare per attivare l'account. Le credenziali saranno
inviate via email.»

## La scheda

Un clic sull'elenco apre la scheda, con il titolo «Modifica sottoscrittore» o
«Modifica attuatore». Sotto il titolo compaiono nome, cognome e codice
fiscale; a destra lo stato dell'account («Attivo» o «Disattivo»). Un indirizzo che non corrisponde a un'anagrafica mostra
«Pagina non trovata».

In fondo ci sono «Annulla» e «Salva modifiche». Questo «Salva modifiche»
salva Dati principali, Curriculum formativo, l'azienda collegata e le
Abilitazioni. Poi torna all'elenco, senza mostrare alcun messaggio di
conferma.

### Dati principali

I campi sono quelli della creazione. In modifica il server applica regole
diverse:

- tutti i campi sono facoltativi: un campo di testo obbligatorio svuotato
  viene salvato vuoto. Una data obbligatoria svuotata invece fa fallire il
  salvataggio: dalla scheda Dati principali il browser lo impedisce, da
  un'altra scheda la richiesta arriva al server e a video compare «Servizio
  temporaneamente non disponibile. Riprova tra poco.»;
- il codice fiscale, se cambia, viene controllato per lunghezza, struttura e
  carattere di controllo; anche una nuova email deve avere formato valido;
- la scadenza del documento, se cambia, non può essere già passata;
- un codice fiscale, un’email o una scadenza già salvati e non toccati non bloccano il
  salvataggio, anche se non rispettano queste regole;
- cambiare email o cellulare annulla la verifica di quel contatto (vedi più
  avanti).

Nota: in modifica l'obbligo dei campi è controllato solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Curriculum formativo

La scheda ha quattro sotto-schede, ognuna divisa in sezioni:

- **Titoli**:
  - Diploma di istruzione secondaria: diploma, anno di conseguimento, istituto con
    indirizzo, città e provincia, voto ricevuto e voto massimo; anno
    integrativo, con gli stessi dati;
  - Titolo universitario: tipo di titolo, corso di laurea, università, data di
    conseguimento, voti;
  - Altri titoli: fino a due titoli post-laurea e due
    altri titoli di studio, ciascuno con istituto e data.
- **Immatricolazioni ed iscrizioni**:
  - Anagrafe Nazionale Studenti: stato (immatricolato o no), tipo di corso
    (prima o dopo la riforma del D.M. 509/99), data di immatricolazione,
    ateneo, conclusione della carriera (titolo finale, rinuncia, decadenza,
    trasferimento) e relativa data;
  - Iscrizione in corso, il corso a cui la persona è attualmente iscritta: casella «Iscritto ad altro
    corso di studi di altre Università», tipo, classe di laurea,
    denominazione, università, anno di iscrizione, modalità (full-time o
    part-time), città e provincia.
- **Abilitazioni professionali**: abilitazione professionale e qualifica
  professionale con data e luogo; albo o elenco; forze dell'ordine; richiesta
  di convalida di attività professionalizzanti, corsi di formazione e altre
  attività certificate.
- **Invalidità**: percentuale e tipo.

Il curriculum si salva con il «Salva modifiche» in fondo alla pagina, oppure
con la creazione. Se per la stessa persona esistono più curricula, la scheda
mostra il più recente.

I due «Anno di conseguimento», quello del diploma e quello dell'anno
integrativo, si scrivono liberamente: va bene sia un anno solo sia un anno
scolastico, come ricorda il suggerimento nel campo. Il limite è di 45
caratteri. Sono due dati distinti, e nessuno dei due ha a che vedere con la
«Data di conseguimento» del titolo universitario.

### Utente

La scheda ha due sezioni. «Account e ruolo» contiene:

- il nome utente, modificabile;
- lo stato, un pulsante che passa da «Attivo» a «Disattivo» e viceversa;
- il ruolo, con tutti i ruoli: Utente, Aderente, Regionale, Provinciale,
  Consulente, Nazionale, Operatore;
- l'utente padre, con il pulsante «Cambia padre».

«Cronologia» mostra data di creazione, ultimo aggiornamento e «aggiornato da»,
in sola lettura.

La scheda ha un proprio pulsante «Salva utente». Come si salva il ruolo, chi può
salvare gli altri campi e cosa cambia per la persona dopo un cambio di ruolo
sono descritti in [Ruoli e permessi](ruoli-e-permessi.md). Nella stessa pagina
è descritto il pulsante «Accedi con questo utente», che compare qui per un
utente attivo con un ruolo da attuatore.

Quando il salvataggio di questa scheda riesce, la pagina resta aperta e mostra
«Modifiche salvate con successo!».

Restano quattro comportamenti propri di questa pagina:

- se chi salva non può modificare nome utente, stato e utente padre, il ruolo
  viene comunque salvato per primo: dopo il messaggio di errore il ruolo
  risulta cambiato e il resto no;
- il «Salva modifiche» in fondo alla pagina è visibile anche da qui, ma non
  salva nome utente, stato e utente padre. Per un attuatore rimanda invece il
  ruolo scelto nei Dati principali: se il ruolo è stato cambiato da questa
  scheda, quel salvataggio riporta il valore di partenza;
- il nome utente si può cambiare anche in uno già usato da un altro utente. In
  quel caso nessuno dei due riesce più ad accedere;
- il salvataggio di questa scheda invia sempre lo stato. Su un account ancora
  in attesa, annulla l'attivazione automatica (vedi più avanti).

Nota: su questi punti interfaccia e server non sono allineati; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Azienda

Solo per gli attuatori. Collega l'attuatore alla sua azienda e mostra le
percentuali delle convenzioni universitarie. È descritta in
[Aziende](aziende.md).

### Abilitazioni

Solo per gli attuatori, solo per il Nazionale e solo su un'anagrafica già
salvata. Contiene cinque interruttori:

- Abilitazione generale pratiche universitarie;
- Università Telematica eCampus;
- Link Campus University;
- SSML Lamezia Terme;
- Avatar4University.

Gli interruttori si salvano con il «Salva modifiche» in fondo alla pagina.
Nella Dashboard i pulsanti delle pratiche di un ateneo sono attivi solo con
l'abilitazione generale e con quella dell'ateneo: vedi [Pratiche](pratiche.md).

Nota: questo limite è applicato solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Esami

Solo per i sottoscrittori. Mostra «Sezione in fase di sviluppo».

## Verifica di email e cellulare

L'account di una nuova anagrafica si attiva quando sono verificati sia
l'email sia il cellulare. La verifica si avvia dalla scheda: il codice arriva
alla persona dell'anagrafica, e chi lavora sulla scheda lo inserisce.

### Quando si può verificare

- Solo su un'anagrafica già salvata: in creazione il pulsante «Verifica» non
  c'è.
- Il pulsante è attivo se il campo non è vuoto, se il valore a video è quello
  salvato e se il contatto non è già verificato.
- Se il valore a video è diverso da quello salvato compare «Salva le modifiche
  per verificare questo contatto.»
- Un contatto verificato mostra «Verificato». Se la data è nota, sotto compare
  «Verificato il» con data e ora.
- Solo su un'anagrafica che si vede: su una che non si vede, chiedere lo stato,
  far partire un codice o confermarlo rispondono «Anagrafica non trovata.».

### Come si svolge

1. «Verifica» apre la finestra «Verifica email» o «Verifica cellulare», con il
   valore a cui arriverà il codice.
2. «Invia codice» spedisce un codice di 6 cifre: per SMS al cellulare, per
   email all'indirizzo.
3. La finestra mostra il destinatario, in parte nascosto, e ricorda che il
   codice vale 10 minuti.
4. Si scrive il codice e si preme «Conferma codice».

«Invia un nuovo codice» spedisce un altro codice: quello precedente non vale
più. «Indietro» chiude la finestra.

Il cellulare deve avere il prefisso internazionale. A un numero italiano che
inizia per 3 il prefisso +39 viene aggiunto in automatico. Spazi, punti,
trattini e parentesi non contano, e il prefisso 00 vale come +. Un valore non
accettabile produce «Inserisci un cellulare valido con prefisso
internazionale.» oppure «Inserisci un indirizzo email valido.».

### Limiti sui codici

- Un codice vale 10 minuti e ammette 5 tentativi. Dopo serve un codice nuovo.
  Il messaggio è «Codice non valido o scaduto. Richiedine uno nuovo.»
- Fra due invii per lo stesso contatto passano almeno 60 secondi. Il pulsante
  mostra l'attesa, per esempio «Reinvia tra 42 s».
- Per ogni anagrafica si possono spedire al massimo 5 codici all'ora per
  l'email e 5 per il cellulare. Ogni operatore, e ogni indirizzo di rete, può
  spedire al massimo 30 codici all'ora. Oltre, la finestra mostra «Troppi
  tentativi. Riprova tra» seguito dai secondi da attendere.
- Se la spedizione non riesce, la finestra mostra «Servizio temporaneamente
  non disponibile. Riprova tra poco.»
- Se il contatto salvato è cambiato nel frattempo compare «Il contatto è
  cambiato. Salva e ricarica la scheda prima della verifica.». Se è già
  verificato compare «Il contatto è già verificato.».

### Se il contatto cambia

Una verifica vale solo per il valore verificato. Quando si salva
un'anagrafica con un'email o un cellulare diversi, il server cancella la
verifica di quel contatto e annulla i codici non ancora usati.

- Per un account in attesa di attivazione, il nuovo valore va verificato di
  nuovo.
- Un account già attivo resta attivo. La scheda però mostra il nuovo contatto
  come «Verificato», senza data, e il pulsante resta disattivato.

Nota: l'interfaccia mostra come verificato un contatto che il server non ha verificato; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Anagrafiche precedenti a questo sistema

- Un account già attivo, per il quale non risulta nessuna verifica, mostra i
  contatti come «Verificato», senza data.
- Le verifiche fatte con il sistema precedente si possono recuperare con
  un'operazione tecnica. Per ogni anagrafica si prende l'ultima verifica
  riuscita dell'email e quella del cellulare. Ciascuna viene riportata solo se
  il valore è ancora quello attuale; per l'email non contano maiuscole e
  minuscole. Le verifiche recuperate mostrano la data originale.
  L'operazione non modifica le verifiche già presenti.
- Queste anagrafiche non hanno un'attivazione in attesa: verificarne i
  contatti non attiva l'account.

### Attivazione automatica

Quando si verifica il secondo dei due contatti, se l'account è disattivato e
ancora in attesa di attivazione:

- l'account diventa attivo;
- il server crea una password casuale di almeno 24 caratteri;
- all'email dell'anagrafica parte un messaggio con nome utente e password. Per
  i ruoli che accedono alla piattaforma il messaggio indica l'indirizzo della
  piattaforma; per gli altri dice che le credenziali valgono nei servizi
  abilitati per il profilo;
- l'attesa di attivazione si chiude.

Dopo una verifica la scheda mostra uno di questi messaggi:

- «Contatto verificato.»: la verifica è riuscita, l'account non è stato
  attivato;
- «Contatti verificati: account attivato e credenziali inviate via email.»;
- «Account attivato, ma invio delle credenziali non riuscito. Contatta il tuo
  referente ERSAF.»: l'account è attivo, ma la password non è arrivata. Il
  recupero della password esiste solo per gli attuatori: vedi
  [Accesso e sicurezza](accesso-e-sicurezza.md).

L'attivazione automatica non avviene se:

- uno dei due contatti non è verificato;
- l'account è già attivo, anche perché attivato a mano;
- l'attesa è stata annullata salvando la scheda Utente.

## Utente padre

Che cosa sia l'utente padre, chi può salvarlo e il fatto che oggi non limiti
ciò che si vede sono descritti in
[Ruoli e permessi](ruoli-e-permessi.md). Qui contano la finestra di scelta e i
controlli del server.

- «Cambia Padre» apre la finestra «Seleziona Nuovo Utente Padre». La finestra
  elenca gli attuatori con nome, cognome, ruolo e azienda. Si può cercare per
  nome, cognome o azienda e filtrare per ruolo. Scorrendo in fondo si
  caricano altri risultati.
- «Seleziona» cambia solo ciò che si vede. Il cambio si salva con il «Salva
  Modifiche» della scheda Utente.
- Se l'attuatore scelto non ha un utente compare «L'attuatore selezionato non
  ha un utente associato.»
- Il server accetta solo un utente esistente e rifiuta l'utente stesso con
  «Un utente non può essere padre di se stesso.». Non controlla i giri, per
  esempio A padre di B e B padre di A.

Nota: la finestra mostra l'azienda a tutti e il server non impedisce i giri; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Attivazione e disattivazione

- Lo stato si cambia nella scheda Utente e si salva con il suo «Salva
  Modifiche».
- Un utente disattivato non può accedere. I suoi accessi già aperti smettono
  di funzionare alla richiesta successiva.
- Attivare a mano un account in attesa non spedisce credenziali: la password
  resta un valore che nessuno conosce. Un attuatore può impostarne una con il
  recupero della password: vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

## Eliminazione

Le anagrafiche non si possono eliminare, né dall'interfaccia né dal server.
Si può solo disattivare l'utente.

## Avvisi sulle anomalie storiche

Un'icona accanto al nominativo nell'elenco apre gli avvisi, sia su desktop sia
su mobile, senza aprire la scheda. Il dialogo si chiude con il pulsante dedicato
o con Escape. Gli stessi avvisi compaiono anche nella scheda anagrafica.

Si segnalano codice fiscale o email non validi e duplicati di codice fiscale,
email, telefono, cellulare, PEC e documento. Il confronto include altre pagine
dell'elenco, ma solo anagrafiche visibili all'operatore: non rivela nomi di
clienti fuori dalla sua portata. Il Nazionale confronta l'intero archivio.

In modifica codice fiscale ed email vengono validati nel formato completo
solo se cambiati; una nuova scadenza del documento non può essere passata.
I valori storici invariati non falliscono la validazione del formato.
Resta il controllo di unicità descritto sopra, anche per i valori invariati.
