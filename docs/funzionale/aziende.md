# Aziende

Questa pagina descrive le aziende: l'elenco, la creazione e la modifica, la
gerarchia fra aziende, le percentuali delle convenzioni universitarie e il
collegamento fra un attuatore e la sua azienda.

Nel testo, «interfaccia» indica le pagine che si usano nel browser. «Server»
indica il sistema che salva i dati e applica le regole.

## Chi vede quali aziende

Il menu mostra «Aziende» solo al Nazionale.

Nota: questo limite è applicato solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Le aziende formano una gerarchia: un'azienda può avere un'azienda padre, e
ogni figlia può avere altre figlie. Il server prevede questa regola di
visibilità:

- il Nazionale vede tutte le aziende;
- chi ha un altro ruolo vede l'azienda associata alla propria anagrafica e
  tutte quelle che ne discendono, a qualunque livello;
- chi non ha un'azienda non ne vede nessuna.

Un'azienda non visibile si comporta come un'azienda inesistente: le ricerche
non la trovano e il suo indirizzo mostra «Pagina non trovata».

In questa versione il server non riconosce l'azienda di chi lavora. Chi non è
Nazionale non vede quindi alcuna azienda nelle pagine Aziende e nella scheda
Azienda di un attuatore, come se non ne avesse una. Il proprio profilo
continua a mostrare il nome dell'azienda associata.

Nota: la regola della propria azienda e delle discendenti oggi non produce effetti; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Elenco

- La ricerca «Cerca per ragione sociale» trova le aziende la cui ragione
  sociale **inizia** con il testo scritto. Un testo che compare solo a metà
  non basta. Maiuscole e minuscole sono indifferenti.
- Le colonne sono Ragione sociale e Sede. La sede riunisce via e civico, CAP,
  città e provincia.
- L'elenco segue l'ordine di inserimento. Le righe arrivano a blocchi, come
  negli altri elenchi: il blocco successivo si carica scorrendo in fondo alla
  pagina oppure con «Carica altri elementi».
- Se nessuna azienda corrisponde compare «Nessuna azienda trovata.».
- Il pulsante «Nuova» apre una scheda vuota. Chi usa un lettore di schermo
  sente la forma estesa, «Nuova azienda». Il pulsante è visibile a chiunque
  apra l'elenco.
- Un clic sulla riga apre la scheda dell'azienda.

### Avvisi sui dati

Accanto alla ragione sociale può comparire un triangolo giallo. Passandoci
sopra con il mouse, o raggiungendolo con la tastiera, mostra i problemi
dell'azienda:

- «Codice Fiscale mancante»;
- «Codice Fiscale duplicato con:», seguito dalle ragioni sociali delle altre
  aziende con lo stesso codice fiscale;
- «Partita IVA mancante»;
- «Partita IVA non conforme (deve essere di 11 cifre numeriche)».

Gli stessi avvisi compaiono in un riquadro giallo in cima alla scheda
dell'azienda.

L'avviso sul codice fiscale duplicato nomina anche aziende che chi guarda non
potrebbe vedere.

Nota: l'avviso non rispetta la regola di visibilità; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Creare e modificare un'azienda

La scheda si intitola «Nuova azienda» oppure «Modifica azienda»; in modifica
sotto il titolo compare la ragione sociale. I campi sono divisi in sezioni:
Dati anagrafici, Sede legale, Contatti e Coordinate bancarie; in modifica
seguono Gerarchia e Convenzioni universitarie. Una partita IVA che non ha 11
cifre si evidenzia in rosso mentre si scrive. «Salva» (in modifica «Salva
modifiche») salva e torna all'elenco; «Annulla» torna all'elenco senza
salvare. Un errore compare in un riquadro rosso sopra i campi.

### Campi

| Obbligatori | Facoltativi |
|---|---|
| Ragione sociale, Partita IVA, Codice fiscale, Via, Città, CAP, Provincia | Civico, Codice SDI, Email, PEC, Telefono, Sito web, IBAN, Codice BIC |

I campi obbligatori hanno l'asterisco e l'interfaccia non salva finché sono
vuoti. Il campo Partita IVA accetta al massimo 11 caratteri, e il browser
segnala i caratteri diversi dalle cifre.

Il **Codice nazionale** non è fra questi: il server lo genera da solo, con un
valore casuale e univoco, alla creazione dell'azienda. Il campo compare in
sola lettura nella scheda dell'azienda e non compare affatto nella finestra
di creazione rapida dalla scheda Azienda di un attuatore. Nessuno lo può
scrivere né modificare, né dall'interfaccia né passando un valore al server
in creazione o in modifica.

### Controlli del server

- **Partita IVA**: obbligatoria, fatta solo di cifre, lunga esattamente 11. I
  messaggi sono «La Partita IVA è obbligatoria.», «La Partita IVA deve
  contenere solo cifre.» e «La Partita IVA deve essere di 11 cifre.».
- **Codice fiscale**: obbligatorio. Il messaggio è «Il Codice Fiscale è
  obbligatorio.». Il formato non viene controllato.
- **Unicità**: il server rifiuta un valore già usato da un'altra azienda in uno
  di questi campi: codice fiscale, partita IVA, ragione sociale, email, PEC,
  telefono, IBAN. Il messaggio nomina il campo, per esempio «Esiste già
  un'azienda con questa Partita IVA.». Il confronto riguarda tutte le aziende,
  anche quelle non visibili.

### Regole in modifica

- Il server controlla l'azienda così come risulterà dopo il salvataggio:
  partita IVA di 11 cifre e codice fiscale presente, anche se non si sono
  toccati quei campi. Un'azienda con l'avviso «Codice Fiscale mancante»,
  «Partita IVA mancante» o «Partita IVA non conforme» non si salva finché non
  si corregge.
- L'interfaccia rimanda tutti i campi compilati, e il controllo di unicità li
  riguarda tutti. Un'azienda con l'avviso «Codice Fiscale duplicato con:» non
  si salva finché il suo codice fiscale resta uguale a quello dell'altra. Lo
  stesso vale per ogni altro campo univoco già doppio.
- Svuotare un campo facoltativo non lo cancella. L'interfaccia non invia i
  campi vuoti, quindi il valore precedente resta salvato.

Nota: l'interfaccia mostra il campo vuoto, ma il server conserva il valore; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Eliminazione

Le aziende non si possono eliminare, né dall'interfaccia né dal server.

## Gerarchia

### Azienda padre alla creazione

Il server prevede questa regola: la nuova azienda diventa figlia dell'azienda
di chi la crea. Se chi la crea non ha un'azienda, la nuova azienda è una
radice, cioè non ha padre.

In questa versione il server non riconosce l'azienda di chi crea, quindi ogni
nuova azienda nasce radice. Chi non è Nazionale, dopo averla creata, non la
vede.

Nota: la regola dell'azienda padre oggi non produce effetti; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Il riquadro «Azienda padre»

Compare solo nella scheda di un'azienda già salvata. Mostra la ragione sociale
dell'azienda padre, oppure «Nessuna (azienda radice)».

Passando da un'azienda a un'altra, un eventuale messaggio di errore rimasto
dall'azienda precedente sparisce: prima restava sullo schermo e sembrava
riferito a quella appena aperta.

### Cambiare il padre

- Il pulsante «Cambia padre» compare solo al Nazionale. Il server rifiuta gli
  altri con «Solo il nazionale può eseguire questa operazione.».
- Il pulsante apre la finestra «Seleziona Nuova Azienda Padre». La finestra
  elenca ragione sociale, partita IVA e città, e cerca le aziende la cui
  ragione sociale inizia con il testo scritto. Mostra solo i primi risultati:
  per trovare un'azienda conviene restringere la ricerca.
- L'azienda che si sta modificando non compare fra le scelte.
- «Seleziona» indica il nuovo padre. «Rendi radice (nessun padre)» toglie il
  padre.
- Il cambio si salva subito, senza passare dal pulsante «Salva» della scheda.
  Se il cambio azzererebbe delle percentuali, prima compare la richiesta di
  conferma descritta più avanti.

Il server accetta il nuovo padre solo se:

- esiste. Altrimenti risponde «Il nuovo padre indicato non esiste.»;
- non è l'azienda stessa. Altrimenti risponde «Un'azienda non può essere
  padre di se stessa.»;
- non discende dall'azienda. Altrimenti risponde «Il nuovo padre è un
  discendente di questa azienda: creerebbe un ciclo.»

I messaggi compaiono nel riquadro, sotto l'azienda padre. Le aziende discendenti compaiono
comunque fra le scelte: il rifiuto arriva solo dopo averne selezionata una.

Nota: l'interfaccia propone scelte che il server rifiuta; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Percentuali delle convenzioni universitarie

Ogni azienda ha otto percentuali:

- eCampus - Lauree ed eCampus - Master;
- Link - Lauree e Link - Master;
- SSML - Lauree e SSML - Master;
- A4U - Master e A4U - Perfezionamenti.

Si vedono in una tabella per ateneo e tipologia di corso (le combinazioni che
non esistono mostrano un trattino): nella sezione «Convenzioni universitarie»
della scheda dell'azienda e nella sezione «Dettaglio convenzioni
universitarie» della scheda Azienda di un attuatore. Si
modificano solo dalla scheda dell'azienda: nella scheda dell'attuatore la
sezione è in sola lettura. «Salva percentuali» le salva subito,
indipendentemente dal resto della scheda dell'azienda. Un'azienda senza
percentuali salvate le ha tutte a zero.

Il server permette di modificarle a chiunque veda l'azienda, compresa la
propria. Poiché oggi il server non riconosce l'azienda di chi lavora (vedi
«Chi vede quali aziende»), di fatto solo il Nazionale vede e modifica le
percentuali.

### Regola dell'azzeramento

- Una percentuale non può superare la stessa percentuale dell'azienda padre.
  Se la supera, viene portata a zero.
- La regola scende lungo la gerarchia. In ogni azienda discendente, a
  qualunque livello, una percentuale che supera quella del proprio padre viene
  portata a zero. Il confronto usa i valori del padre dopo gli eventuali
  azzeramenti.
- Un'azienda radice non ha limiti.
- Se il padre non ha percentuali salvate, i suoi valori contano come zero:
  ogni valore maggiore di zero della figlia viene azzerato.
- La stessa regola vale quando il Nazionale cambia il padre. Le percentuali
  dell'azienda si confrontano con quelle del nuovo padre, e a cascata quelle
  delle discendenti.

### Richiesta di conferma

Se il salvataggio, o il cambio del padre, azzererebbe qualche percentuale, il
server non scrive nulla e chiede conferma. L'interfaccia mostra «Alcune
percentuali verranno azzerate. Continuare?» con due pulsanti:

- «Conferma» salva e applica gli azzeramenti;
- «Annulla» lascia tutto com'era.

Il server indica quali aziende e quali percentuali verrebbero azzerate, ma
l'interfaccia mostra solo il messaggio generico.

Nota: l'interfaccia non mostra il dettaglio degli azzeramenti; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Valori ammessi

I campi propongono valori da 0 a 100, ma «Salva percentuali» non passa dal
controllo dei campi della pagina: né l'interfaccia né il server bloccano un
numero fuori da questo intervallo. Un campo svuotato vale zero.

Due effetti si incontrano comunque:

- con la scheda dell'azienda aperta, i campi delle percentuali fanno parte
  della pagina dell'azienda. Un valore fuori da 0 a 100, o non intero, blocca
  il «Salva modifiche» in fondo alla pagina, che non riguarda le percentuali;
- il server accetta solo numeri interi. Un valore con i decimali, salvato con
  «Salva percentuali», viene rifiutato con un messaggio tecnico.

Nota: l'intervallo da 0 a 100 è solo indicativo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Azienda di un attuatore

La scheda Azienda compare solo nelle anagrafiche degli attuatori (vedi
[Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md)). Mostra la
ricerca per partita IVA oppure l'azienda già associata.

Oggi chi non è Nazionale non vede alcuna azienda (vedi «Chi vede quali
aziende»). Su un attuatore che ha già un'azienda collegata, la scheda mostra
l'errore «Azienda non trovata.», i dati dell'azienda vuoti, con un trattino al
posto di ogni valore, e tutte le percentuali a zero. La ricerca per partita
IVA non trova mai nulla e propone sempre di creare l'azienda.

Nota: la scheda mostra un'azienda vuota al posto di quella collegata; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Attuatore senza azienda

- Il campo «PARTITA IVA» accetta solo cifre, al massimo 11.
- «Cerca azienda» con meno di 11 cifre mostra «Inserisci 11 cifre.».
- Se l'azienda esiste, viene associata subito all'attuatore.
- Se non esiste, si apre la finestra «Nessuna azienda trovata con questa
  Partita IVA». La finestra contiene i campi dell'azienda, con la partita IVA
  già compilata e non modificabile. «Crea e associa» crea l'azienda e la
  associa all'attuatore; «Annulla» chiude la finestra.
- La nuova azienda segue la regola dell'azienda padre di chi la crea, non
  quella dell'attuatore (vedi Gerarchia).

La ricerca trova solo le aziende visibili. Se l'azienda esiste ma non è
visibile, si apre comunque la finestra di creazione, e il salvataggio viene
rifiutato con «Esiste già un'azienda con questa Partita IVA.». Per chi non è
Nazionale questo accade con qualunque partita IVA già registrata.

Nota: la ricerca propone di creare un'azienda che esiste già; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Attuatore con azienda

- In alto compare la ragione sociale; sotto, partita IVA, codice fiscale,
  email, PEC e telefono.
- «Cambia azienda» torna alla ricerca per partita IVA. Lì «Annulla» ripristina
  la vista dell'azienda attuale.
- «Rimuovi associazione» chiede «Rimuovere l'azienda associata a questo
  attuatore?». Se si conferma, l'azienda viene scollegata.
- Più in basso ci sono le percentuali, in sola lettura, descritte sopra.

### Quando si salva l'associazione

- Su un attuatore già salvato, associare, cambiare o rimuovere l'azienda ha
  effetto subito.
- Su un attuatore in creazione, l'associazione si salva con «Crea
  Attuatore». Un'azienda creata dalla finestra esiste invece già da subito,
  anche se poi l'attuatore non viene creato.
