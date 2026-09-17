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
| Consulente | altro | no |
| Operatore | altro | no |

- Le persone con ruolo **Utente** sono i sottoscrittori e compaiono nell'elenco Sottoscrittori.
- **Aderente, Provinciale, Regionale e Nazionale** sono gli attuatori e compaiono nell'elenco Attuatori.
- **Consulente e Operatore** non compaiono in nessuno dei due elenchi.

## Chi può accedere

- Accedono Aderente, Provinciale, Regionale e Nazionale, se l'account è attivo.
- Utente, Consulente e Operatore non accedono. Anche con la password giusta vedono lo stesso messaggio delle credenziali sbagliate.
- Il Nazionale, dopo la password, deve superare il **secondo fattore**: senza, non entra. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).
- Un account nuovo resta disattivato finché email e cellulare non sono verificati. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).
- Il **recupero della password** funziona solo per gli attuatori.

Anche un sottoscrittore riceve le credenziali quando il suo account si attiva. In quel caso l'email non indica l'indirizzo della piattaforma, perché con il ruolo Utente non si accede.

## Cosa vede ciascuno

### Nel menu e nel profilo

| Voce | Nazionale | Regionale, Provinciale, Aderente |
|---|---|---|
| Dashboard | sì | sì |
| Sottoscrittori | sì | sì |
| Attuatori | sì | no |
| Aziende | sì | no |
| Prodotti formativi | sì | no |
| Profilo, schede "Dati principali" e "Utente" | sì | sì |
| Profilo, scheda "Sicurezza" | sì | no |

Nota: Attuatori, Aziende e Prodotti formativi sono nascosti solo dal menu; chi conosce l'indirizzo apre le pagine e il server non controlla il ruolo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Le **Pratiche** non sono nel menu di nessuno: si aprono dalla Dashboard. I pulsanti della Dashboard sono attivi solo se la persona collegata ha l'abilitazione generale alle pratiche universitarie e quella dell'ateneo. Vedi [Pratiche](pratiche.md).

Nota: le abilitazioni limitano solo i pulsanti della Dashboard, e l'elenco delle pratiche si apre comunque dal suo indirizzo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

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
- la piattaforma si ricarica sui Sottoscrittori con l'identità della persona scelta, e con il suo menu;
- l'operazione resta nei registri del server, con chi l'ha fatta e su chi.

Per tornare a sé stessi si usa "Esci" e si accede di nuovo con le proprie credenziali. Il Nazionale ripete anche il secondo fattore.

Il pulsante compare quando la scheda mostra lo stato "Attivo" e un ruolo fra Aderente, Provinciale, Regionale e Nazionale, anche se non ancora salvati. Compare qualunque sia il ruolo di chi guarda: un Aderente o un Provinciale che lo preme riceve "Non hai i permessi per questa operazione.".

Nota: l'interfaccia mostra il pulsante anche a chi non può usarlo e anche davanti a un Nazionale, e il server rifiuta; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Solo il Nazionale

- **Vede tutte le aziende** (vedi sotto).
- **Cambia l'azienda padre** di un'azienda. Agli altri il server risponde "Solo il nazionale può eseguire questa operazione.". Vedi [Aziende](aziende.md).
- **Gestisce i propri metodi del secondo fattore** dalla scheda "Sicurezza" del profilo. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).

Nessuno può aggiungere o togliere le passkey o l'app di autenticazione di un'altra persona: si gestiscono solo per sé stessi. Il codice via email dipende invece dall'email in anagrafica, che anche altri utenti collegati possono modificare: cambiandola, la verifica decade e il Nazionale perde quel metodo.

Nota: la protezione non copre il codice via email, perché nessun controllo di ruolo limita chi modifica l'anagrafica; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Visibilità delle aziende

- Il **Nazionale** vede tutte le aziende.
- Gli **altri** vedono la propria azienda e tutte quelle che le stanno sotto nella gerarchia: le figlie, le figlie delle figlie e così via.
- Chi **non ha un'azienda** associata non ne vede nessuna.
- Un'azienda non visibile di norma si comporta come se non esistesse: compare "Azienda non trovata.".

La regola vale per l'elenco, la scheda, la modifica, le percentuali e la ricerca per partita IVA.

Nota: in alcuni casi il server rivela comunque l'esistenza di un'azienda non visibile; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Per sottoscrittori, attuatori e pratiche non esiste una regola simile: chi accede li vede tutti.

Nota: il server non limita per ruolo né per gerarchia la lettura di sottoscrittori, attuatori e pratiche, anche dove il menu nasconde la pagina; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

## Assegnare i ruoli

### Alla creazione

- Un **nuovo sottoscrittore** riceve il ruolo Utente.
- Un **nuovo attuatore** ha, fra i "Dati principali", il campo "Ruolo attuatore". Le scelte sono Aderente (proposto), Provinciale, Regionale e Nazionale. Se non si sceglie nulla, il ruolo è Aderente. Il campo resta modificabile anche dopo.

### Dalla scheda "Utente"

La scheda "Utente" di ogni persona ha la tendina **"Ruolo"** con tutti e sette i ruoli. La schermata e il suo salvataggio sono descritti in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md). Qui contano solo le regole di permesso:

- il **ruolo** lo può cambiare qualunque utente collegato, su qualunque scheda, compresa la propria;
- **nome utente, stato e utente padre** li può cambiare solo chi modifica la propria scheda, oppure un Regionale o un Nazionale. Agli altri il server risponde "Non hai i permessi per modificare un altro utente.";
- cambiare ruolo sposta la persona da un elenco all'altro: il ruolo Utente la porta fra i Sottoscrittori, un ruolo da attuatore fra gli Attuatori.

Nota: né l'interfaccia né il server limitano chi può assegnare un ruolo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Un cambio di ruolo non chiude le sessioni già aperte della persona. Il suo menu cambia al successivo caricamento della pagina.

Nota: chi riceve un ruolo senza accesso resta collegato fino alla fine della sessione, e chi diventa Nazionale mantiene la sessione senza il secondo fattore; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

### Utente padre

L'utente padre indica l'attuatore di riferimento della persona. Si cambia dalla scheda "Utente" e segue le stesse regole di permesso del nome utente e dello stato: solo sulla propria scheda, oppure da un Regionale o da un Nazionale. Come si sceglie il nuovo padre è descritto in [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).

Oggi l'utente padre è solo un'informazione: non limita cosa vede nessuno.
