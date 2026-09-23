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

Accanto alla ragione sociale può comparire un triangolo giallo. Un clic sul
triangolo apre, subito sotto, un riquadro con il numero di errori e i problemi
dell'azienda, senza aprire la scheda; se sotto non c'è spazio si apre sopra;
si chiude con Escape o con un clic fuori:

- «Codice Fiscale mancante»;
- «Codice Fiscale duplicato con:», seguito dalle ragioni sociali delle altre
  aziende con lo stesso codice fiscale;
- «Partita IVA mancante»;
- «Partita IVA non conforme (deve essere di 11 cifre numeriche)».

Gli stessi avvisi compaiono, per intero, in un riquadro giallo in cima alla
scheda dell'azienda. Il campo interessato ha il bordo giallo e, sotto, una nota
breve:

- «Codice Fiscale mancante» e «Partita IVA mancante»: «Da compilare»;
- «Codice Fiscale duplicato con:»: «Duplicato con un'altra azienda» oppure
  «Duplicato con altre aziende»;
- «Partita IVA non conforme»: «Deve contenere 11 cifre numeriche».

La nota sparisce appena si modifica il campo e torna se si rimette il valore
salvato; il riquadro in cima resta. Sulla partita IVA la nota resta finché il
valore non ha 11 cifre (vedi «Campi»).

L'avviso sul codice fiscale duplicato nomina anche aziende che chi guarda non
potrebbe vedere.

Nota: l'avviso non rispetta la regola di visibilità; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Creare e modificare un'azienda

La scheda si intitola «Nuova azienda» oppure «Modifica azienda». I campi sono
divisi in sezioni: Dati anagrafici, Sede legale, Contatti e Coordinate
bancarie. In fondo alla pagina, a destra, ci sono «Annulla», che torna
all'elenco senza salvare, e «Salva», che salva e torna all'elenco. Un errore
di salvataggio compare in un riquadro rosso sopra i campi.

In modifica la scheda ha in più:

- sotto il titolo, la ragione sociale e, se l'azienda ha un padre, «· Figlia
  di» seguito dal nome dell'azienda padre. La ragione sociale è quella
  salvata: non cambia mentre si scrive nel campo. Compare solo la ragione
  sociale per un'azienda radice, finché il padre non è stato letto e quando
  non si riesce a sapere quale sia il padre (vedi «Il riquadro Azienda
  padre»);
- le sezioni Gerarchia e Convenzioni universitarie, dopo le altre;
- gli avvisi sui dati, descritti sopra;
- il pulsante «Salva modifiche» al posto di «Salva».

In una nuova azienda non c'è niente sotto il titolo e il Codice nazionale
resta vuoto.

### Campi

| Obbligatori | Facoltativi |
|---|---|
| Ragione sociale, Partita IVA, Codice fiscale, Via, Città, CAP, Prov. | Civico, Codice SDI, Email, PEC, Telefono, Sito web, IBAN, Codice BIC |

I campi obbligatori hanno l'asterisco e l'interfaccia non salva finché sono
vuoti.

- **Partita IVA**: accetta al massimo 11 caratteri. Mentre si scrive un
  valore diverso da 11 cifre, il campo diventa giallo e sotto compare «Deve
  contenere 11 cifre numeriche»; la nota sparisce quando il valore arriva a
  11 cifre. La nota da sola non blocca il salvataggio. Se ci sono caratteri
  diversi dalle cifre, il browser lo segnala e non invia la scheda. Se le
  cifre non sono esattamente 11, il salvataggio lo rifiuta il server (vedi
  «Controlli del server»).
- **Prov.**: accetta al massimo 2 caratteri, la sigla della provincia. Vale
  anche nella finestra di creazione rapida dalla scheda Azienda di un
  attuatore. Il limite è solo dell'interfaccia: il server accetta anche
  valori più lunghi, e una provincia già salvata più lunga si vede per intero.
- **Codice SDI, PEC, IBAN e Codice BIC**: quando sono vuoti mostrano un
  esempio: «7 caratteri» per il Codice SDI, un indirizzo di posta certificata
  per la PEC, «IT00 X000 0000 0000 0000 0000 000» per l'IBAN e «XXXXITXX» per
  il Codice BIC. Il formato non viene controllato, né dall'interfaccia né dal
  server. IBAN e Codice BIC, come il Codice nazionale, sono scritti con
  caratteri tutti della stessa larghezza, per leggerli meglio uno per uno.

Il **Codice nazionale** non è nella tabella: il server lo genera da solo, con un
valore casuale e univoco, alla creazione dell'azienda. Il campo compare in
sola lettura nella scheda dell'azienda: il valore si può selezionare e
copiare, ma non modificare. Non compare affatto nella finestra di creazione
rapida dalla scheda Azienda di un attuatore. Nessuno lo può scrivere né
modificare, né dall'interfaccia né passando un valore al server in creazione
o in modifica.

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

Compare solo nella scheda di un'azienda già salvata, nella sezione Gerarchia.
Mostra la ragione sociale dell'azienda padre, oppure «Nessuna (azienda
radice)». Se la scheda del padre non si può leggere, al posto del nome compare
«Azienda #» seguito dal suo numero interno, anche sotto il titolo della
pagina.

Se invece non si riesce a sapere quale sia il padre, al posto del riquadro
compare un riquadro rosso con il messaggio di errore, senza «Cambia padre».

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
- Il cambio si salva subito, senza passare da «Salva modifiche».
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

Si vedono in una tabella con una riga per ateneo e le colonne Lauree, Master
e Perfezionamenti: nella sezione «Convenzioni universitarie» della scheda
dell'azienda e nella sezione «Dettaglio convenzioni universitarie» della
scheda Azienda di un attuatore. Accanto a ogni valore c'è il simbolo «%»; le
combinazioni che non esistono mostrano una lineetta, «—». Un'azienda senza
percentuali salvate le ha tutte a zero.

Si modificano solo dalla scheda dell'azienda: nella scheda dell'attuatore la
sezione è in sola lettura. «Salva percentuali», sotto la tabella a destra, le
salva subito, indipendentemente dal resto della scheda dell'azienda.

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

Per le percentuali la richiesta compare fra la tabella e «Salva percentuali»;
per il cambio del padre, nel riquadro «Azienda padre», sotto il nome.

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
l'errore «Azienda non trovata.», i dati dell'azienda vuoti, con una lineetta
al posto di ogni valore, e tutte le percentuali a zero. La ricerca per partita
IVA non trova mai nulla e propone sempre di creare l'azienda.

Nota: la scheda mostra un'azienda vuota al posto di quella collegata; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Attuatore senza azienda

- Il campo «Partita IVA» accetta solo cifre, al massimo 11.
- «Cerca azienda» con meno di 11 cifre colora il campo di rosso e sotto mostra
  «Inserisci 11 cifre.».
- Se l'azienda esiste, viene associata subito all'attuatore.
- Se non esiste, si apre la finestra «Nessuna azienda trovata con questa
  Partita IVA». La finestra contiene i campi dell'azienda, con gli stessi
  limiti della scheda, e la partita IVA già compilata e in sola lettura. In
  basso a destra, «Annulla» chiude la finestra e «Crea e associa» crea
  l'azienda e la associa all'attuatore.
- La nuova azienda segue la regola dell'azienda padre di chi la crea, non
  quella dell'attuatore (vedi Gerarchia).

La ricerca trova solo le aziende visibili. Se l'azienda esiste ma non è
visibile, si apre comunque la finestra di creazione, e il salvataggio viene
rifiutato con «Esiste già un'azienda con questa Partita IVA.». Per chi non è
Nazionale questo accade con qualunque partita IVA già registrata.

Nota: la ricerca propone di creare un'azienda che esiste già; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Attuatore con azienda

- In alto compare la ragione sociale, con accanto «Cambia azienda» e
  «Rimuovi associazione». Sotto ci sono ragione sociale, partita IVA, codice
  fiscale, email, PEC e telefono; un dato vuoto mostra una lineetta, «—».
- «Cambia azienda» torna alla ricerca per partita IVA. Lì «Annulla» ripristina
  la vista dell'azienda attuale.
- «Rimuovi associazione» chiede «Rimuovere l'azienda associata a questo
  attuatore?». Se si conferma, l'azienda viene scollegata.
- Più in basso, dopo una linea di separazione, ci sono le percentuali, in
  sola lettura, descritte sopra.

### Quando si salva l'associazione

- Su un attuatore già salvato, associare, cambiare o rimuovere l'azienda ha
  effetto subito.
- Su un attuatore in creazione, l'associazione si salva con «Crea
  attuatore». Un'azienda creata dalla finestra esiste invece già da subito,
  anche se poi l'attuatore non viene creato.
