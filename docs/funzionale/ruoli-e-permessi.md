# Ruoli e permessi

Ogni persona registrata ha un ruolo. Il ruolo decide se la persona può entrare nella piattaforma, cosa vede e cosa può fare.

## I ruoli

| Ruolo | Gruppo | Può accedere |
|---|---|---|
| Utente | sottoscrittore | no |
| Aderente | attuatore | sì |
| Provinciale | attuatore | sì |
| Regionale | attuatore, amministrativo | sì |
| Nazionale | attuatore, amministrativo | sì, con il secondo fattore |
| Consulente | sottoscrittore | no |
| Operatore | attuatore | no |

- Le persone con ruolo **Utente o Consulente** sono i sottoscrittori e compaiono nell'elenco Sottoscrittori.
- **Aderente, Provinciale, Regionale, Nazionale e Operatore** compaiono nell'elenco Attuatori. L'Operatore, però, non accede alla piattaforma.

## Chi può accedere

- Accedono Aderente, Provinciale, Regionale e Nazionale, se l'account è attivo.
- Utente, Consulente e Operatore non accedono. Anche con la password giusta vedono lo stesso messaggio delle credenziali sbagliate.
- Il Nazionale, dopo la password, deve superare il **secondo fattore**: senza, non entra. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).
- Un account nuovo resta disattivato finché email e cellulare non sono verificati. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).
- Il **recupero della password** funziona solo per Aderente, Provinciale, Regionale e Nazionale.

Anche un sottoscrittore riceve le credenziali quando il suo account si attiva. In quel caso l'email non indica l'indirizzo della piattaforma, perché con il ruolo Utente non si accede.

## Cosa vede ciascuno

### Nel menu e nel profilo

| Voce | Nazionale | Regionale, Provinciale | Aderente |
|---|---|---|---|
| Dashboard | sì | sì | sì |
| Sottoscrittori | sì | sì | sì |
| Attuatori | sì | sì | no |
| Aziende | sì | sì | no |
| Pratiche | sì | sì | sì |
| Prodotti formativi | sì | no | no |
| EduNews24 | sì | sì | sì |
| Profilo, schede "Dati principali" e "Utente" | sì | sì | sì |
| Profilo, scheda "Sicurezza" | sì | no | no |

Nota: le voci nascoste non proteggono le pagine. Attuatori e Prodotti formativi si aprono digitando l'indirizzo e il server non controlla il ruolo. Anche la pagina Aziende si apre, ma lì il server applica la regola di visibilità descritta più sotto, per cui l'elenco risulta vuoto. Vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

La **Dashboard** è la prima pagina dopo l'accesso per tutti i ruoli che accedono; le sue scorciatoie sono le voci del menu del proprio ruolo. **EduNews24** mostra a tutti gli stessi contenuti. Vedi [EduNews24](edunews24.md).

La pagina **Pratiche** ospita il pannello degli atenei e mostra le pratiche secondo le regole di visibilità descritte sotto. Il Nazionale non ha il pannello né il pulsante "Nuova": vede un unico elenco di tutte le pratiche tranne le Bozze, raggruppato per stato, ed è l'unico a vedere e modificare il Codice ASG delle pratiche eCampus. Il pannello mostra il numero di pratiche per ateneo, tipologia e stato; le sue righe si aprono solo con l'abilitazione generale e quella dell'ateneo; le abilitazioni non sostituiscono i controlli del server. Vedi [Pratiche](pratiche.md).

### Dentro le pagine, solo per il Nazionale

- **Elenco Attuatori**: la colonna "Azienda".
- **Scheda di un attuatore già salvato**: la scheda "Abilitazioni". Gli interruttori, il loro salvataggio e il loro effetto sono descritti in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).
- **Scheda di un'azienda**: il pulsante "Cambia padre".

Nota: colonna "Azienda" e scheda "Abilitazioni" sono nascoste solo dall'interfaccia, e il server fornisce l'azienda e accetta modifiche alle abilitazioni da qualunque utente collegato; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Alla creazione un attuatore riceve tutte le abilitazioni tranne SSML Lamezia Terme; un sottoscrittore non ne riceve nessuna.

## Ruoli amministrativi: Regionale e Nazionale

Regionale e Nazionale possono fare due cose in più degli altri.

1. **Modificare altri utenti.** Nella scheda "Utente" di una persona cambiano nome utente, stato Attivo o Disattivo e utente padre. Gli altri ruoli possono cambiare questi dati solo nella propria scheda.
2. **Accedere come un altro utente**, descritto qui sotto.

### Accedere come un altro utente

Nella scheda "Utente" di una persona c'è il pulsante **"Accedi con questo utente"**.

Il server lo accetta solo se:

- chi lo usa è Regionale o Nazionale;
- la persona scelta è attiva e ha un'anagrafica;
- la persona scelta è Aderente, Provinciale o Regionale.

Non si può mai entrare come un **Nazionale**: il messaggio è "Il ruolo Nazionale richiede la verifica a due fattori.". Negli altri casi rifiutati compare "Utente non trovato o non impersonabile.". Il server non tiene conto della gerarchia fra le persone.

Cosa succede quando riesce:

- la propria sessione termina;
- la piattaforma si ricarica sulla Dashboard con l'identità della persona scelta, e con il suo menu;
- l'operazione resta nei registri del server, con chi l'ha fatta e su chi.

Per tornare a sé stessi si usa "Esci" e si accede di nuovo con le proprie credenziali. Il Nazionale ripete anche il secondo fattore.

Il pulsante compare solo al **Nazionale**, quando la scheda mostra lo stato "Attivo" e un ruolo fra Aderente, Provinciale, Regionale e Nazionale, anche se non ancora salvati. Il server accetta la richiesta anche da un Regionale, che però non ha più il pulsante.

Nota: l'interfaccia mostra il pulsante anche a chi non può usarlo e anche davanti a un Nazionale, e il server rifiuta; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Solo il Nazionale

- **Vede tutte le aziende** (vedi sotto).
- **Cambia l'azienda padre** di un'azienda. Agli altri il server risponde "Solo il nazionale può eseguire questa operazione.". Vedi [Aziende](aziende.md).
- **Gestisce i propri metodi del secondo fattore** dalla scheda "Sicurezza" del profilo. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

Nessuno può aggiungere o togliere le passkey o l'app di autenticazione di un'altra persona: si gestiscono solo per sé stessi. Il codice via email dipende invece dall'email in anagrafica, che anche altri utenti collegati possono modificare: cambiandola, la verifica decade e il Nazionale perde quel metodo.

Nota: la protezione non copre il codice via email, perché nessun controllo di ruolo limita chi modifica l'anagrafica; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Visibilità delle aziende

- Il **Nazionale** vede tutte le aziende.
- Gli **altri** dovrebbero vedere la propria azienda e tutte quelle che le stanno sotto nella gerarchia: le figlie, le figlie delle figlie e così via. In questa versione, però, il server non riconosce l'azienda di chi lavora, quindi chi non è Nazionale non vede alcuna azienda nelle pagine Aziende e nella scheda Azienda di un attuatore. Il proprio profilo continua a mostrare il nome dell'azienda associata.
- Chi **non ha un'azienda** associata non ne vede nessuna.
- Un'azienda non visibile di norma si comporta come se non esistesse: compare "Azienda non trovata.".

La regola vale per l'elenco, la scheda, la modifica, le percentuali e la ricerca per partita IVA.

Nota: in alcuni casi il server rivela comunque l'esistenza di un'azienda non visibile; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Visibilità di sottoscrittori, attuatori e pratiche

- Il **Nazionale** vede tutto.
- Per le **anagrafiche**, chiunque altro vede la propria e quelle delle persone che dipendono da lui o da una persona della sua stessa azienda, seguendo la catena dell'utente padre fino in fondo. Le persone della stessa azienda non compaiono per il solo fatto di esserlo: compaiono se a loro volta dipendono da qualcuno del gruppo. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).
- Per le **pratiche**, chiunque altro vede solo quelle della propria azienda, e chi non ha un'azienda non ne vede nessuna né può crearne. Vedi [Pratiche](pratiche.md).
- Ciò che non si vede risponde "non trovata", con lo stesso messaggio di una cosa inesistente: la regola non rivela nulla.

Nota: il documento PDF di una pratica non segue questa regola, e alcune pagine restano raggiungibili dall'indirizzo anche a chi non ha il ruolo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Assegnare i ruoli

### Alla creazione

Chi può assegnare quali ruoli, sia alla creazione sia nella scheda "Utente":

| Chi | Ruoli che può assegnare |
|---|---|
| Nazionale | tutti e sette |
| Regionale | Aderente, Provinciale |
| Provinciale | Aderente |
| Aderente | nessuno |

- Un **nuovo sottoscrittore** riceve sempre il ruolo Utente, chiunque lo crei; nella sua scheda "Utente" il ruolo si può poi cambiare con le regole della tabella.
- Un **nuovo attuatore** ha, fra i "Dati principali", il campo "Ruolo attuatore". Le scelte sono i ruoli da attuatore (Aderente, Provinciale, Regionale, Nazionale) che chi crea può assegnare; parte su Aderente. Il campo resta modificabile anche dopo, con le stesse regole.

Dove c'è una sola scelta possibile (per esempio un Provinciale che crea un attuatore, che può solo Aderente, o chi guarda un ruolo che non può cambiare) non c'è la tendina: il ruolo compare come valore bloccato.

### Dalla scheda "Utente"

La scheda "Utente" di ogni persona ha la tendina **"Ruolo"**, con i ruoli che chi guarda può assegnare e quello attuale della persona. La schermata e il suo salvataggio sono descritti in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md). Qui contano solo le regole di permesso:

- il **ruolo** si cambia secondo la tabella sopra, con in più, per chi non è Nazionale: non si cambia il proprio ruolo, e non si tocca quello di chi ha un ruolo da attuatore che non si potrebbe assegnare (un Regionale non cambia il ruolo di un altro Regionale o di un Nazionale). Chi ha un ruolo senza accesso (Utente, Consulente, Operatore) si può promuovere. Chi sta sotto (ha un ruolo che si potrebbe assegnare) si può anche declassare a **Utente**, solo da questa scheda: un Regionale riporta a Utente un Aderente o un Provinciale, un Provinciale un Aderente. Nei casi non ammessi il ruolo è bloccato; se la richiesta arriva comunque al server, risponde "Non puoi assegnare questo ruolo." (o "Solo il nazionale può eseguire questa operazione." per il ruolo Nazionale e il proprio). Riconfermare il ruolo già presente è ammesso, perché la scheda lo rimanda a ogni salvataggio;
- **nome utente, stato e utente padre** li può cambiare solo chi modifica la propria scheda, oppure un Regionale o un Nazionale. Per gli altri questi campi (e il pulsante "Cambia padre") sono bloccati;
- cambiare ruolo sposta la persona da un elenco all'altro: il ruolo Utente la porta fra i Sottoscrittori, un ruolo da attuatore fra gli Attuatori.

Le due tendine del ruolo di un attuatore (scheda Utente e Dati principali) seguono le stesse regole e mostrano sempre lo stesso valore: cambiarne una cambia anche l'altra.

Un cambio di ruolo non chiude le sessioni già aperte della persona. Il suo menu cambia al successivo caricamento della pagina.

Nota: chi riceve un ruolo senza accesso resta collegato fino alla fine della sessione, e chi diventa Nazionale mantiene la sessione senza il secondo fattore; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Utente padre

L'utente padre indica l'attuatore di riferimento della persona. Si cambia dalla scheda "Utente" e segue le stesse regole di permesso del nome utente e dello stato: solo sulla propria scheda, oppure da un Regionale o da un Nazionale. Come si sceglie il nuovo padre è descritto in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

L'utente padre non è solo un'informazione: è la catena su cui si regge la visibilità delle anagrafiche. Cambiarlo cambia chi vede quella persona e chi vede le persone che dipendono da lei.
