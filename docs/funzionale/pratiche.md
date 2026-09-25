# Pratiche

Questa pagina descrive le pratiche come le vede chi usa la piattaforma: la
pagina Pratiche, l'elenco, la scheda e il documento PDF.

## Cos'è una pratica

Una pratica registra l'iscrizione di uno studente a un percorso formativo.
Collega:

- lo studente, cioè un sottoscrittore;
- l'aderente emittente, cioè l'attuatore con ruolo Aderente che emette la
  pratica;
- il percorso formativo, scelto fra i [prodotti formativi](prodotti-formativi.md);
- l'università e il tipo di corso, ricavati dal percorso;
- il numero della pratica, il prezzo e lo stato.

Il tipo di corso non compare nella scheda. Serve ai filtri che la pagina Pratiche
applica all'elenco. Università e tipo di corso si copiano dal percorso alla
creazione della pratica: poi restano quelli, anche se il prodotto formativo
cambia.

## Come si arriva alle pratiche

La voce "Pratiche" è nel menu per Nazionale, Regionale, Provinciale e
Aderente. Vedi [Ruoli e permessi](ruoli-e-permessi.md). Senza un ateneo
selezionato, la pagina mostra il pannello degli atenei, con il numero di
pratiche per tipologia di corso e stato; scegliendo una riga si apre l'elenco
filtrato. La pagina si apre anche scrivendo il suo indirizzo
nel browser: il backend limita comunque le pratiche all'azienda visibile
all'utente.

## Pannello degli atenei

Il pannello è stato spostato dalla Dashboard alla pagina Pratiche. La Dashboard
mostra soltanto il titolo e il messaggio di benvenuto.

Sotto il titolo "Pratiche" la frase "Numero di pratiche per ateneo, tipologia
di corso e stato." introduce i numeri delle pratiche.

### Totali

In cima una striscia riporta il totale delle pratiche e, accanto, il totale di
ciascuno stato: Bozza, In lavorazione, In attesa di modifica, Conclusa,
Caricata e Rifiutata. Ogni stato ha un pallino colorato, lo stesso delle
tabelle degli atenei. Quando lo spazio è poco, i totali degli stati vanno su
tre o due colonne, sotto il totale delle pratiche.

### Un riquadro per ateneo

Sotto la striscia c'è un riquadro per ateneo, con il logo, il nome e un
riepilogo come "120 pratiche · 6 tipologie". Nel riquadro, una tabella ha una
riga per tipologia di corso, una colonna per stato e il totale della riga; in
fondo, la riga "Totale ateneo". I numeri degli stati a zero sono in grigio
chiaro; i totali restano scuri.

| Ateneo | Abilitazione dell'ateneo | Righe, in quest'ordine |
|---|---|---|
| Università Telematica eCampus | Università Telematica eCampus | Prevalutazione, Corso di Laurea, Master, Corsi di Perfezionamento, Formazione ed Alta Formazione, Corsi Singoli |
| Link Campus University | Link Campus University | Corsi di Perfezionamento, Corsi Singoli |
| SSML Lamezia Terme | SSML Lamezia Terme | Prevalutazione, Corso di Laurea, Master, Corsi di Perfezionamento, Alta Formazione per Lauree, Corsi Singoli, Corsi Speciali |
| Avatar4University | Avatar4University | Master, Corsi di Perfezionamento |

Quando lo spazio è poco, per esempio sul telefono, la tabella diventa un
elenco: per ogni tipologia il nome e il totale, e sotto i sei stati con il loro
numero.

### Come si contano le pratiche

- Si contano solo le pratiche che l'utente vede, le stesse dell'elenco: vedi
  [Chi vede le pratiche](#chi-vede-le-pratiche).
- Una riga somma le pratiche dei tipi di corso della sua tipologia. Due righe
  raggruppano più tipi di corso:
  - "Master" conta insieme master, master area scuola e master classi di
    concorso;
  - "Formazione ed Alta Formazione" conta insieme i corsi di formazione e i
    corsi di alta formazione.
- Ogni totale, dell'ateneo e della striscia, è la somma delle righe. Una
  pratica che non cade in nessuna riga non si conta: per esempio una pratica
  senza tipo di corso, o di un tipo di corso che l'ateneo non ha fra le sue
  righe, come il percorso docenti. Per questo il totale può essere minore del
  numero di pratiche dell'elenco completo.
- Si contano solo i sei stati delle colonne.
- La riga "Prevalutazione" è sempre a zero: le prevalutazioni non sono pratiche
  e la piattaforma non le gestisce.

### Quando una riga si apre

Le abilitazioni sono quelle dell'utente collegato. Una riga si apre solo se
l'utente ha entrambe:

- l'abilitazione generale alle pratiche universitarie;
- l'abilitazione dell'ateneo.

Negli altri casi le righe restano visibili, con i loro numeri, ma sono
sbiadite e non si aprono. Senza l'abilitazione generale, sopra la striscia
compare un riquadro giallo con il messaggio "Non hai l'abilitazione generale
alle pratiche universitarie."

Mentre legge i numeri e le abilitazioni, la pagina Pratiche mostra
"Caricamento pratiche…". Se non riesce a leggerli, al posto della striscia e
dei riquadri mostra un riquadro rosso con il messaggio di errore.

Le abilitazioni si impostano nella scheda di un attuatore: vedi
[Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

### Dove portano le righe

Ogni riga apre l'elenco delle pratiche già filtrato per l'ateneo e per i tipi
di corso della riga. Il titolo dell'elenco lo ricorda: "Elenco Pratiche",
seguito dal nome dell'ateneo e dai tipi di corso.

Una pratica creata da un percorso senza tipo di corso non compare in nessuno di
questi elenchi.

La riga "Prevalutazione" apre la pagina "Pagina non trovata": la funzione
non esiste nella piattaforma.

Nota: la riga porta a una pagina che non esiste; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Elenco delle pratiche

L'elenco si intitola "Elenco Pratiche". Se si arriva dalla pagina Pratiche, il
titolo aggiunge l'ateneo e i tipi di corso. Il pulsante "Nuova" apre una
pratica nuova. Selezionando una riga si apre la scheda della pratica.

### Colonne

- **Codice**: il numero della pratica.
- **Data creazione**: nel formato giorno-mese-anno.
- **Sottoscrittore**: nome e cognome dello studente.
- **Corso**: la denominazione del percorso formativo. Nella tabella un nome
  lungo va a capo al massimo su due righe; passando il mouse compare per
  intero.
- **Stato**: sempre su una riga. Se lo spazio non basta, il nome si accorcia
  con i puntini.

Se un valore manca, compare un trattino.

### Ricerca

Il campo "Cerca per sottoscrittore" cerca nel nome e nel cognome dello
studente. Con più parole, ognuna deve comparire nel nome o nel cognome.
Maiuscole e minuscole non contano.

### Filtri

Il pulsante "Filtri" apre questi filtri:

- **Numero pratica**: mostra le pratiche il cui numero contiene il testo
  scritto.
- **Stato**: uno degli stati disponibili, oppure "Tutti gli stati".
- **Tipologia corso**: è pensato per le righe che raggruppano più tipi di
  corso. Nessuna riga della pagina Pratiche lo attiva, quindi non compare.

L'ateneo e i tipi di corso scelti dalla pagina Pratiche non compaiono fra i filtri.
Per cambiarli si torna alla pagina Pratiche e si sceglie un'altra riga.

Accanto alla scritta "Filtri" compare il numero dei filtri attivi. Il
conteggio e il pulsante "Azzera filtri" riguardano solo numero, stato e
tipologia. Non toccano la ricerca, né l'ateneo e i tipi di corso scelti dalla
pagina Pratiche.

Ricerca e filtri restano nell'indirizzo della pagina. Chi torna dalla scheda
ritrova l'elenco con le stesse scelte.

### Ordine e caricamento

Le pratiche sono ordinate per data di creazione, dalla più recente. A parità
di data viene prima la pratica inserita per ultima.

L'elenco si carica a blocchi. Il blocco successivo arriva scorrendo verso il
fondo della pagina, oppure con il pulsante "Carica altri elementi". Alla fine
compare "Hai raggiunto la fine dell'elenco". Se nessuna pratica corrisponde,
compare "Nessuna pratica trovata."

## Scheda della pratica

La scheda si intitola "Nuova pratica", oppure "Pratica" seguito dal numero.
Ha due sezioni: "Iscrizione" e "Dati della pratica".

### Iscrizione

| Campo | Come si sceglie |
|---|---|
| Studente | Si cerca fra i sottoscrittori, per nome e cognome |
| Aderente emittente | Si cerca fra gli attuatori con ruolo Aderente, per nome e cognome |
| Percorso formativo | Si cerca fra i prodotti formativi, per denominazione o codice. Compaiono anche i prodotti non attivi |
| Università | Non si sceglie: dopo la scelta del percorso compare l'università del percorso |

Il campo Studente invita a cercare anche per codice, ma la ricerca guarda
solo nome e cognome.

Nota: la ricerca per codice promessa dal campo non esiste; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

In una pratica già salvata questi quattro valori sono solo in lettura: non si
possono cambiare.

### Dati della pratica

| Campo | Regole |
|---|---|
| Numero pratica | Obbligatorio, al massimo 45 caratteri. Gli spazi all'inizio e alla fine si tolgono |
| Anno accademico | Facoltativo, al massimo 45 caratteri |
| Sede di erogazione | Facoltativa, al massimo 255 caratteri |
| Prezzo (€) | Obbligatorio. Un numero non negativo, con al massimo dodici cifre intere e otto decimali |
| Stato | Obbligatorio, da scegliere nell'elenco degli stati |
| Data di creazione | Obbligatoria. Propone la data di oggi. In una pratica già salvata non si cambia |
| Note | Testo libero |

Il prezzo si scrive a mano: la piattaforma non lo ricava dalle righe di prezzo
del prodotto formativo.

L'applicazione non controlla che il numero della pratica sia unico.

Nota: l'obbligo di numero, stato, prezzo e data di creazione, e il formato del prezzo, sono applicati solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Una pratica può contenere anche dati che la scheda non mostra e non modifica:
per esempio la firma, gli allegati, l'azienda, il consulente e l'indicazione
di rinnovo. Alcuni di questi dati finiscono nel documento PDF.

Nota: in modifica la scheda cambia solo i campi elencati sopra, ma il sistema ne accetta anche altri, fra cui l'azienda, il consulente e il tipo di corso che decide i filtri della pagina Pratiche; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Salvataggio

Il pulsante "Salva pratica" controlla i dati e salva. Durante il salvataggio
mostra "Salvataggio…". I messaggi di controllo sono:

- "Inserisci il numero della pratica."
- "Seleziona lo stato della pratica."
- "Inserisci un prezzo valido, con al massimo otto decimali."

Solo per una pratica nuova:

- "Seleziona lo studente."
- "Seleziona l'aderente emittente."
- "Seleziona il percorso formativo."
- "Il percorso deve avere un'università associata."
- "Inserisci la data di creazione."

Dopo una modifica riuscita compare "Pratica salvata.". Dopo una creazione
riuscita si apre direttamente la scheda della nuova pratica, senza messaggio.

Il pulsante "Annulla" torna all'elenco senza salvare.

## Documento PDF

### Quando è disponibile

Il pulsante "Scarica PDF" compare nell'intestazione della scheda solo se per
la pratica esiste un modulo stampabile.

Sono disponibili i moduli originali per queste combinazioni:

| Ente | Tipi di corso |
|---|---|
| eCampus | Lauree, master (anche area scuola e classi di concorso), perfezionamento, formazione e alta formazione, corsi singoli |
| SSML | Lauree, master, perfezionamento, formazione e alta formazione, corsi speciali, corsi singoli |
| Link Campus | Perfezionamento, corsi singoli |
| Avatar4University | Perfezionamento, con il modulo Fenice presente fra gli originali |

I corsi speciali SSML usano lo stesso modulo dei corsi di formazione SSML,
secondo la corrispondenza confermata il 18 settembre 2026.

Percorso docenti e corsi speciali eCampus, e master Avatar4University restano senza PDF:
non è stato individuato un modulo corrispondente nell'archivio fornito.
Non viene usato un modulo di un altro tipo come ripiego. Nel confronto dei
nomi non contano maiuscole, accenti, spazi e punteggiatura.

Il documento guarda l'università e il tipo di corso attuali del prodotto
formativo, non quelli copiati nella pratica alla creazione. Se il prodotto
cambia università o tipo di corso, una pratica può comparire sotto una riga
della pagina Pratiche senza avere il documento, oppure avere il documento senza
comparire sotto la riga corrispondente.

Nota: la pagina Pratiche e il documento possono quindi non concordare; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Il pulsante non c'è in una pratica nuova non ancora salvata. Se la piattaforma
non riesce a verificare la disponibilità, il pulsante non compare.

### Come si scarica

Premendo "Scarica PDF", il pulsante diventa "Preparazione del PDF…" e resta
bloccato fino alla fine. Il file si salva con il nome "pratica-" seguito dal
numero della pratica e dall'estensione ".pdf". Nel nome, i caratteri diversi
da lettere, cifre, trattino e trattino basso diventano trattini; se il numero
manca o è fatto solo di caratteri non ammessi, al suo posto compare il numero
interno della pratica.

Il documento è in formato PDF/A, adatto all'archiviazione a lungo termine.

Il documento si compone al momento, con i dati salvati. Le modifiche non
ancora salvate nella scheda non compaiono: prima di scaricare conviene
salvare.

Se il download non riesce, sopra la scheda compare un messaggio:

- "Per questo tipo di pratica il documento non è ancora disponibile." se per
  la pratica non c'è un modulo;
- "Servizio temporaneamente non disponibile. Riprova tra poco." se il
  documento non si riesce a comporre;
- "Connessione non riuscita. Controlla la rete e riprova." se manca la
  connessione.

### Cosa contiene

Il documento riproduce il modulo cartaceo del tipo di corso, con i campi già
compilati. Le pagine cambiano secondo il modulo originale. Per le lauree sono:

- la domanda di immatricolazione: dati anagrafici, residenza, recapiti, anno
  accademico, immatricolazione o iscrizione ad anni successivi, corso,
  livello e retta;
- il regolamento;
- l'informativa sulla privacy;
- l'autocertificazione: diploma e anno integrativo, invalidità, carriera
  universitaria, eventuale iscrizione in corso a un altro corso universitario,
  abilitazioni professionali, albi, qualifiche ed esami sostenuti;
- la pagina con i dati del documento di identità;
- il contratto con lo studente.

Da dove arrivano i dati:

| Dati | Provenienza |
|---|---|
| Anagrafica, recapiti, documento di identità | Scheda del sottoscrittore |
| Studi e carriera universitaria | Curriculum formativo del sottoscrittore |
| Esami | Esami registrati per lo studente, dal più vecchio |
| Numero, anno accademico, data di creazione | Pratica |
| Retta | Prezzo della pratica; resta vuota se il prezzo è zero |
| Corso | Denominazione del percorso formativo |
| Livello | Durata della laurea del percorso: triennale, magistrale o ciclo unico |

Il numero della pratica compare in alto a destra su tutte le pagine, tranne il
regolamento. Sulle pagine da firmare c'è la riga con luogo, data e firma:

- **luogo**: la città dell'azienda collegata alla pratica. Sul regolamento il
  luogo non c'è;
- **data**: la data di creazione della pratica;
- **firma**: l'immagine della firma registrata nella pratica.

Le pagine centrali del contratto non hanno questa riga. L'ultima pagina del
contratto ha anche una seconda firma, per l'approvazione delle clausole.

### Da sapere

- Un dato che manca lascia vuoto il campo o la casella.
- Nei moduli eCampus il consenso al trattamento dei dati e la non adesione
  ai servizi integrativi mantengono le scelte del gestionale precedente. Per
  gli altri enti le caselle restano vuote: non si presume un consenso assente.
- Alcuni campi restano sempre vuoti, perché la piattaforma non raccoglie quei
  dati: stato di nascita, curriculum del corso, servizi integrativi, corso
  innovativo, scuola statale o paritaria.
- Come recapito telefonico si usa il cellulare; se manca, il telefono.
- L'indirizzo per la corrispondenza è il domicilio, solo se è diverso dalla
  residenza. Resta vuoto anche se il curriculum indica la residenza come
  indirizzo per la corrispondenza.
- L'anno accademico scritto come "2025/26" o "2025-2026" si divide in anno di
  inizio e anno di fine. Scritto in altro modo, si riporta com'è.
- La tabella degli esami ha quindici righe. Se gli esami sono di più, l'ultima
  riga indica quanti ne restano fuori.
- Gli esami non si inseriscono dalla piattaforma: non sono ancora gestiti
  nella scheda del sottoscrittore, e la sezione "Esami" mostra sempre "Nessun
  esame registrato.". Nel documento compaiono solo gli esami già registrati.
- La scheda della pratica non permette di indicare firma, azienda e rinnovo.
  Una pratica creata dalla piattaforma produce quindi un documento senza firma
  e senza luogo, e risulta sempre come immatricolazione. Firma, luogo e
  rinnovo compaiono solo nelle pratiche che li contengono già.

### Corsi singoli e dati che non entrano nel modulo

Gli insegnamenti richiesti provengono dalla scheda dei corsi singoli della
pratica; in sua assenza si usano il percorso principale e gli eventuali due
corsi aggiuntivi già collegati. Sono distinti dagli esami sostenuti dallo
studente. Il modulo eCampus contiene tre righe, Link quattro, SSML sei:
gli insegnamenti ulteriori proseguono su una pagina aggiuntiva della domanda.

CFU e SSD degli insegnamenti richiesti restano vuoti se il catalogo non li
raccoglie. Nei moduli SSML si riportano invece i CFU degli esami già sostenuti,
quando registrati. Un valore più lungo delle caselle prestampate viene scritto
per intero come testo nella stessa riga, riducendone la dimensione.

Il vecchio modulo Link per i corsi singoli viene compilato con l'anno
accademico della pratica al posto di quello prestampato. Le altre condizioni,
informative e indicazioni di pagamento restano quelle degli originali forniti.
Nuovi allegati, acquisizione della firma nell'applicazione e salvataggio remoto
del documento non fanno parte di questa generazione.

### Accordo di rateizzazione eCampus

Per tutti i tipi eCampus supportati, se la pratica ha rate della retta salvate,
il PDF include anche l'accordo di rateizzazione sul modulo originale. Riporta
studente, residenza, corso, prezzo della pratica, importi e scadenze registrati,
data della pratica, luogo e firma quando presenti. Le rate sono ordinate per
scadenza; quelle con la stessa data mantengono l'ordine di inserimento.

Il modulo contiene dodici rate. Quelle successive proseguono su pagine
aggiuntive numerate per rata, senza perdere importi o scadenze. Le righe
contrassegnate come tasse non vengono inserite fra le rate della retta.
Le indicazioni prestampate sulle tasse restano quelle dell'originale fornito.

Senza rate non viene aggiunto un accordo vuoto. Importi e date non vengono
ricalcolati: un dato mancante resta vuoto e un importo zero resta zero.
Questa funzione stampa i piani già registrati; non introduce la creazione
o la modifica dei piani di pagamento nell'interfaccia.

## Stati della pratica

Lo stato si sceglie da un elenco. Gli stati sono registrati nell'archivio
della piattaforma, ma non c'è una pagina per gestirli: aggiungerli o
rinominarli si può solo agendo direttamente sull'archivio.

La pagina Pratiche conta le pratiche di sei stati, con nomi brevi: Bozza, In
lavorazione, In attesa di modifica, Conclusa, Caricata e Rifiutata. Una
pratica in uno stato diverso non compare nei suoi numeri.

- Qualunque stato si può impostare in qualunque momento. Non c'è un percorso
  obbligato da uno stato all'altro.
- Il cambio di stato non attiva altre azioni.
- Non si tiene uno storico dei cambi di stato.
- Lo stato si usa come filtro nell'elenco.

## Cosa non si può fare

- Eliminare una pratica: non c'è un pulsante e il sistema non prevede
  l'operazione.
- Sapere chi ha creato o modificato una pratica: la piattaforma non lo
  registra.
- Cambiare studente, aderente emittente, percorso formativo, università o data
  di creazione di una pratica già salvata.

## Chi vede le pratiche

- Il Nazionale vede tutte le pratiche.
- Chiunque altro vede solo le pratiche della propria azienda.
- Chi non ha un'azienda non vede nessuna pratica, e non può crearne: il
  tentativo viene rifiutato.

La regola vale per l'elenco, i numeri della pagina Pratiche, la scheda, la
disponibilità e il download del PDF e le tendine dei filtri, che propongono
solo studenti e percorsi presenti fra le pratiche che si vedono. Una pratica che non si vede risponde «non trovata» anche aprendola
dall'indirizzo. Per sapere chi accede, vedi
[Ruoli e permessi](ruoli-e-permessi.md).

Creando una pratica, l'azienda è sempre la propria: non si può indicarne
un'altra, e nemmeno spostarla in un'altra azienda modificandola. Il Nazionale
invece può.

Le abilitazioni sono un'altra cosa e limitano solo le righe della pagina
Pratiche, che senza abilitazione non si aprono: i numeri, l'elenco, la scheda,
il pulsante "Nuova" e il documento PDF restano disponibili anche a chi non ne
ha.

Nota: le abilitazioni sono applicate solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).
