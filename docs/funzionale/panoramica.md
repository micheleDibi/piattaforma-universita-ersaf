# Panoramica della piattaforma

## Che cos'è

"Piattaforma Università" è l'applicazione web con cui la rete ERSAF gestisce le iscrizioni universitarie.

Raccoglie in un solo posto:

- **i sottoscrittori**: le persone che si iscrivono a un percorso; nelle pratiche compaiono come studenti;
- **gli attuatori**: le persone che operano nella rete, con ruolo Nazionale, Regionale, Provinciale o Aderente;
- **le aziende** a cui gli attuatori sono associati, ordinate in una gerarchia;
- **le pratiche universitarie**: ciascuna collega uno studente, un aderente emittente e un percorso formativo;
- **i prodotti formativi**: il listino dei percorsi, con prezzi e date di validità.

Le parole usate qui sono spiegate nel [Glossario](glossario.md).

## A chi serve

- **A chi lavora nella rete** con un ruolo che può accedere: Nazionale, Regionale, Provinciale e Aderente. Cosa vede ciascuno è descritto in [Ruoli e permessi](ruoli-e-permessi.md).
- **A chi collauda** le nuove versioni prima dell'uso reale.
- **Al committente**, che qui trova il quadro delle funzioni.

I sottoscrittori non entrano nella piattaforma: le loro schede le compilano gli attuatori.

## Come ci si muove

### Entrare

Si entra dalla pagina di accesso, con nome utente e password. Il Nazionale conferma anche con un secondo fattore. I dettagli sono in [Accesso e sicurezza](accesso-e-sicurezza.md).

Dopo l'accesso si arriva all'elenco dei **Sottoscrittori**. Se si rientra dopo una sessione scaduta, si torna invece alla pagina che era aperta.

### Il menu laterale

Il menu sta sul lato sinistro. Su uno schermo piccolo si apre con l'icona del menu in alto a sinistra, e si chiude da solo quando si sceglie una voce.

Le voci sono:

- **Dashboard**, per tutti;
- **Sottoscrittori**, per tutti;
- **Attuatori**, **Aziende** e **Prodotti formativi**, solo per il Nazionale.

Nota: queste tre voci sono nascoste solo dal menu, e le pagine si aprono comunque dal loro indirizzo; vedi [Limiti noti](../tecnica/sicurezza.md#limiti-noti).

Le **Pratiche** non hanno una voce di menu. Si aprono dalla Dashboard, scegliendo l'ateneo e il tipo di corso.

In fondo al menu ci sono:

- la versione dell'applicazione (vedi sotto);
- il proprio nome, che apre "Il mio profilo"; su uno schermo piccolo il profilo si apre anche dall'icona in alto a destra;
- il pulsante "Esci".

### La versione

In fondo al menu compaiono due righe:

- **"Versione N"**: il numero progressivo della pubblicazione. Cresce di uno a ogni pubblicazione riuscita; una pubblicazione non riuscita non consuma il numero.
- **"Aggiornata il gg/mm/aaaa alle hh:mm"**: data e ora italiane della pubblicazione.

Se la data non è disponibile, compare solo il numero.

Dove l'applicazione non è stata pubblicata con la procedura di rilascio, per esempio sul computer di chi sviluppa, compare "Versione di sviluppo".

Le novità delle versioni pubblicate ufficialmente sono raccolte nel [registro delle novità](../../CHANGELOG.md). Una pubblicazione di prova consuma comunque un numero, che nel registro non comparirà: si può quindi vedere "Versione N" senza trovarla nel registro. Come il registro viene aggiornato a ogni pubblicazione è spiegato in [Deploy](../tecnica/deploy.md).

## Le pagine principali

- **Accesso, Password dimenticata, Reimposta password**: entrare e recuperare la password. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).
- **Dashboard**: messaggio di benvenuto e pannello delle pratiche, diviso per ateneo. Vedi [Pratiche](pratiche.md).
- **Sottoscrittori**: elenco e schede delle persone che si iscrivono. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).
- **Attuatori**: elenco e schede di chi opera nella rete. Vedi [Sottoscrittori e attuatori](sottoscrittori-e-attuatori.md).
- **Aziende**: elenco, schede e gerarchia delle aziende. Vedi [Aziende](aziende.md).
- **Pratiche**: elenco con filtri e scheda della pratica; per alcuni tipi di pratica si scarica anche il modulo in PDF. Vedi [Pratiche](pratiche.md).
- **Prodotti formativi**: listino dei percorsi, con prezzi e validità. Vedi [Prodotti formativi](prodotti-formativi.md).
- **Il mio profilo**: i propri dati, in sola lettura; per il Nazionale anche i metodi del secondo fattore. Vedi [Accesso e sicurezza](accesso-e-sicurezza.md).
- **Pagina non trovata**: compare quando l'indirizzo non corrisponde a nessuna pagina. Il pulsante "Torna all'applicazione" riporta ai Sottoscrittori.
