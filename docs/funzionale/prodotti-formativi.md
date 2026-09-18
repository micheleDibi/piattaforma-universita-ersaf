# Prodotti formativi

Questa pagina descrive i prodotti formativi: l'elenco, la creazione, la
modifica e le righe di prezzo.

## Cos'è un prodotto formativo

Un prodotto formativo è una voce del listino: un percorso che si può scegliere
come "Percorso formativo" in una [pratica](pratiche.md). Ha:

- un codice, che non può ripetersi;
- una denominazione, che nell'elenco compare come titolo;
- il tipo di corso, per esempio lauree, master o corsi singoli;
- l'università;
- il livello, la modalità di erogazione, la facoltà, il corso di laurea e la
  durata della laurea;
- lo stato, Attivo o Non attivo;
- le righe di prezzo, ciascuna valida a partire da una data.

Il prodotto ha anche una classificazione interna che non si vede. La
piattaforma la ricava dal tipo di corso: un valore per le lauree, un altro per
tutti gli altri tipi.

Università e tipo di corso decidono se le pratiche del prodotto hanno il
documento PDF. La durata della laurea decide il livello stampato nel
documento. Vedi [Pratiche](pratiche.md).

## Chi lo vede

La voce "Prodotti formativi" compare nel menu solo al Nazionale (vedi
[Ruoli e permessi](ruoli-e-permessi.md)).

Nota: questo limite è applicato solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Elenco

L'elenco si intitola "Prodotti formativi". Il pulsante "Nuovo" apre un
prodotto nuovo. Selezionando una riga si apre la modifica del prodotto.

### Colonne

- **Titolo**: la denominazione.
- **Codice**.
- **Università**.
- **Tipo di corso**.
- **Stato**: "Attivo" oppure "Non attivo".

Se un valore manca, compare un trattino.

### Ricerca e filtri

Il campo "Cerca per titolo o codice" mostra i prodotti la cui denominazione o
il cui codice contiene il testo scritto. Maiuscole e minuscole non contano.

Il pulsante "Filtri" apre tre filtri:

- **Università**: gli atenei registrati nella piattaforma, oppure "Tutte le
  università".
- **Tipo di corso**: i tipi di corso registrati, oppure "Tutti i tipi".
- **Stato del prodotto**: "Attivo: Tutti", "Attivo: Sì" oppure "Attivo: No".

Accanto alla scritta "Filtri" compare il numero dei filtri attivi. Il
pulsante "Azzera filtri" riporta i tre filtri al valore iniziale. La ricerca
resta com'è.

Ricerca e filtri restano nell'indirizzo della pagina. Chi torna dalla modifica
ritrova l'elenco con le stesse scelte.

### Ordine e caricamento

I prodotti sono in ordine di inserimento, dal più vecchio.

L'elenco si carica a blocchi. Il blocco successivo arriva scorrendo verso il
fondo della pagina, oppure con il pulsante "Carica altri elementi". Se nessun
prodotto corrisponde, compare "Nessun risultato trovato per i filtri di
ricerca selezionati."

## Creazione e modifica

La pagina si intitola "Nuovo prodotto" oppure "Modifica prodotto".

### Campi

| Campo | Regole e scelte |
|---|---|
| Codice Prodotto | Obbligatorio. In creazione è proposto dalla piattaforma |
| Tipo di Corso / Laurea | Facoltativo. In creazione propone LAUREE |
| Attivo | Casella. In creazione è spuntata |
| Università | Da scegliere fra Università Telematica eCampus, Link Campus University, Scuola Superiore Universitaria di Mediazione Linguistica Lamezia Terme, Avatar4University. Vedi la nota più sotto |
| Denominazione | Obbligatoria |
| Livello | Facoltativo: 1 oppure 2 |
| Modalità di Erogazione | Facoltativa: FULL ONLINE, BLENDED, PRESENZIALE |
| Facoltà | Facoltativa |
| Corso di Laurea | Facoltativo. Ogni voce riporta la classe e il nome del corso |
| Durata Laurea | Facoltativa: TRIENNALE, MAGISTRALE, CICLO UNICO |

I tipi di corso fra cui scegliere sono: MASTER, MASTER AREA SCUOLA, MASTER
CLASSI DI CONCORSO, CORSI DI PERFEZIONAMENTO, PERCORSO DOCENTI, CORSI DI
FORMAZIONE, CORSI DI ALTA FORMAZIONE, LAUREE, CORSI SINGOLI, CORSI SPECIALI.

Un prodotto salvato senza tipo di corso, aperto in modifica, mostra LAUREE. Se
lo si salva senza cambiare la scelta, il prodotto diventa di tipo LAUREE.

Le scelte delle tendine del modulo sono fisse. Se nell'archivio si aggiungono
atenei o tipi di corso, i filtri dell'elenco li mostrano, il modulo no.

Nota: le tendine del modulo non seguono le voci registrate nella piattaforma; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Nel modulo l'università sembra facoltativa, perché si può lasciare su
"Seleziona l'università". Il salvataggio però la richiede:

- in creazione compare il messaggio in inglese "Input should be a valid
  integer";
- in modifica il salvataggio non riesce, e il messaggio può parlare di un
  errore sul codice anche se il codice non c'entra.

Nota: l'interfaccia lascia vuoto un campo che il sistema rifiuta; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Codice

- In creazione il modulo propone il codice successivo: "ERSAF_COD_" seguito
  da un numero di almeno quattro cifre. Il numero è il più alto già usato in
  questa forma, più uno.
- Il codice si può cambiare a mano, anche in modifica.
- Il codice non può essere vuoto: "Il campo codice non può essere vuoto."
- In creazione, un codice già usato dà "Il codice '…' è già stato assegnato a
  un altro prodotto."
- Dopo questo errore, e dopo altri rifiuti dovuti a conflitti sui dati, il
  modulo sostituisce il codice con il successivo disponibile, anche se era
  stato scritto a mano. Basta controllarlo e salvare di nuovo.
- In modifica, un codice usato da un altro prodotto dà "Il codice '…' è già
  occupato da un altro prodotto." Il modulo non propone un'alternativa.

Il campo invita a "generare" il codice, ma non c'è un pulsante per farlo. Il
codice proposto arriva solo all'apertura di un prodotto nuovo o dopo un
rifiuto.

Nota: la generazione del codice promessa dal campo non esiste; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Salvataggio

Il pulsante si chiama "Salva Prodotto" in creazione e "Aggiorna Prodotto" in
modifica. Durante il salvataggio mostra "Salvataggio in corso...".

Se il salvataggio riesce compare "Prodotto salvato con successo!
Reindirizzamento in corso..." oppure "Prodotto aggiornato con successo!
Reindirizzamento in corso...". Dopo circa un secondo si torna all'elenco.

Il pulsante "Annulla" torna all'elenco senza salvare.

## Righe di prezzo

La sezione "Dettaglio prodotto" contiene le righe di prezzo. Ogni riga dice
quanto costa il prodotto a partire da una data. Le colonne sono: Inizio
Validità, Fine Validità, Prezzo (€), Durata (mesi), CFU, Tasse (€), Azioni.

Le righe di prezzo non compilano il prezzo delle pratiche: nella pratica il
prezzo si scrive a mano.

### Regole

- Il prezzo è obbligatorio in ogni riga.
- Nelle righe nuove il prezzo deve essere maggiore di zero. Le righe già
  salvate possono restare a zero.
- Le tasse sono facoltative e non possono essere negative.
- Prezzo e tasse accettano la virgola o il punto, con al massimo due
  decimali. Si mostrano con due decimali e la virgola.
- Nei campi del prezzo e delle tasse il punto e la virgola indicano sempre i
  decimali: non si usano per separare le migliaia. Chi scrive 1.250 ottiene
  1,25. In questi due campi il segno meno non si può scrivere.
- Durata e CFU sono numeri interi facoltativi.

I messaggi indicano il numero della riga:

- "Errore nella riga N: Il prezzo è un campo obbligatorio."
- "Errore nella riga N: Per i nuovi dettagli il prezzo deve essere maggiore
  di zero."
- "Errore nella riga N: Le tasse non possono essere negative." Compare solo su
  una riga già salvata con un valore negativo.

Nota: i controlli su prezzo e tasse sono applicati solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Fine validità

La fine validità si calcola al salvataggio:

- ogni riga finisce il giorno prima dell'inizio della riga successiva;
- se la riga successiva non ha una data di inizio, la riga finisce il giorno
  prima del salvataggio;
- l'ultima riga non scade: la sua fine validità è il 31/12/9999.

Il campo si può modificare a video, ma al salvataggio il valore viene
ricalcolato. Il calcolo segue l'ordine delle righe sulla pagina: la
piattaforma non riordina le righe per data e non controlla che le date siano
in sequenza.

### Aggiungere ed eliminare righe

- Un prodotto nuovo parte con una riga che inizia oggi.
- Le righe si aggiungono solo in modifica, con il pulsante "Aggiungi nuova
  riga". La riga nuova inizia oggi e la riga precedente viene chiusa a ieri.
- Si aggiunge una riga alla volta: il pulsante resta bloccato finché la riga
  nuova non è salvata o eliminata.
- Il cestino compare solo sulle righe non ancora salvate. Le righe già salvate
  non si eliminano.
- Se si elimina la riga nuova, al salvataggio l'ultima riga rimasta torna
  senza scadenza.
- Anche la riga iniziale di un prodotto nuovo si può eliminare. In quel caso
  il prodotto si salva senza righe di prezzo.
- Aprendo in modifica un prodotto senza righe di prezzo, la tabella mostra una
  riga nuova che inizia oggi. Per salvare bisogna scriverne il prezzo oppure
  eliminarla.

## Stato Attivo

La casella "Attivo" segna il prodotto come attivo o non attivo. Nell'elenco lo
stato compare nella colonna Stato e si può usare come filtro.

Lo stato non limita la scelta del prodotto in una pratica: anche i prodotti
non attivi compaiono fra i percorsi formativi.

## Cosa non si può fare

- Eliminare un prodotto: non c'è un pulsante e il sistema non prevede
  l'operazione. Si può solo segnarlo come non attivo.
- Gestire atenei e tipi di corso: la piattaforma non ha pagine per farlo.

Nota: per i tipi di corso il limite è applicato solo dall'interfaccia; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).
